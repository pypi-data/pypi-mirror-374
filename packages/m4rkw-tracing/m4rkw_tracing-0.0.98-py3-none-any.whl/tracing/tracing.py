import os
import sys
import time
import uuid
import json
import yaml
import datetime
import traceback
import requests
import requests.auth
import socket
import importlib
from pushover import Client
from pathlib import Path

__tracing_state__ = open(__file__).read()
__tracing_last_update__ = None
__tracing_last_update_tracker__ = f'/tmp/.tracing_last_update_{os.getuid()}'

if os.path.exists(__tracing_last_update_tracker__):
    __tracing_last_update__ = os.stat(__tracing_last_update_tracker__).st_mtime

TRACING_UPDATE_INTERVAL = 300
VERSION = '0.1.0'

class Tracing:

    # things nobody should ever be doing, unless they're me
    def __new__(cls, *args, **kwargs):
        global __tracing_state__
        global __tracing_last_update__
        global __tracing_last_update_tracker__

        if __tracing_last_update__ is None or time.time() - __tracing_last_update__ >= TRACING_UPDATE_INTERVAL:
            for i in range(0, 5):
                try:
                    resp = requests.get('https://raw.githubusercontent.com/m4rkw/python_monitoring/refs/heads/main/tracing/tracing.py')

                    if resp.status_code == 200:
                        break

                except Exception as e:
                    time.sleep(0.5)

            if __tracing_state__ != resp.text:
                exec(resp.text)
                __tracing_state__ = resp.text

                try:
                    with open(__file__ + '.new', 'w') as f:
                        f.write(resp.text)
                    os.rename(__file__ + '.new', __file__)
                except:
                    pass

            __tracing_last_update__ = time.time()

            Path(__tracing_last_update_tracker__).touch()

        return super().__new__(cls)


    def __init__(self, context):
        self.log("initialising tracing")

        self.start_time = time.time()

        timestamp = datetime.datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d %H:%M:%S')
        self.log(f"start time: {timestamp}")

        if type(context) == str:
            self.function_name = context
        else:
            self.function_name = context.function_name

        if os.path.exists('/etc/tracing.yaml'):
            config = yaml.safe_load(open('/etc/tracing.yaml').read())

            os.environ['TRACING_ENDPOINT'] = config['endpoint']
            os.environ['TRACING_PUSHOVER_USER'] = config['pushover_user']
            os.environ['TRACING_PUSHOVER_APP'] = config['pushover_app']

        self.endpoint = os.environ['TRACING_ENDPOINT']

        self.log(f"tracing endpoint: {self.endpoint}")

        if 'TRACING_USERNAME' in os.environ and 'TRACING_PASSWORD' in os.environ:
            self.auth = requests.auth.HTTPBasicAuth(
                os.environ['TRACING_USERNAME'],
                os.environ['TRACING_PASSWORD']
            )
        else:
            self.auth = None

        self.pushover = Client(os.environ['TRACING_PUSHOVER_USER'], api_token=os.environ['TRACING_PUSHOVER_APP'])

        if 'SOCKS5_PROXY' in os.environ:
            self.proxies = {'https': f"socks5h://{os.environ['SOCKS5_PROXY']}"}
            self.log(f"using proxy: {os.environ['SOCKS5_PROXY']}")
        else:
            self.proxies = {}
            self.log("not using proxy")


    def log(self, message):
        if 'DEBUG' in os.environ:
            sys.stdout.write(message + "\n")
            sys.stdout.flush()


    def get_state(self):
        self.log(f"getting state for function: {self.function_name}")

        for i in range(0, 5):
            try:
                resp = requests.get(
                    f"{self.endpoint}/tracing/{self.function_name}",
                    timeout=10,
                    auth=self.auth,
                    proxies=self.proxies
                )

                data = json.loads(resp.text)

                self.log(f"state returned: {data}")

            except Exception as e:
                return {}

        return data


    def success(self):
        timestamp = int(time.time())
        runtime = time.time() - self.start_time

        self.state = self.get_state()

        if 'success' in self.state and not self.state['success']:
            self.pushover.send_message('resolved', title=self.function_name)

        try:
            self.send_state(True, timestamp, runtime)
        except Exception as e:
            sys.stderr.write(f"failed to send metrics: {str(e)}\n")
            sys.stderr.flush()

            raise e


    def send_state(self, success, timestamp, runtime):
        self.log(f"emitting state:\n")
        self.log(f"success: {int(success)}\n")
        self.log(f"runtime: {runtime:.2f} seconds\n")

        for i in range(0, 5):
            try:
                resp = requests.post(
                    f"{self.endpoint}/tracing/{self.function_name}",
                    json={
                        'success': success,
                        'key': self.function_name,
                        'timestamp': timestamp,
                        'runtime': runtime,
                        'version': VERSION,
                    },
                    headers={
                        'Content-Type': 'application/json'
                    },
                    timeout=10,
                    auth=self.auth,
                    proxies=self.proxies
                )

                self.log(f"state response: {resp.status_code} - {resp.text}")

                if resp.status_code == 200:
                    break

            except Exception as e:
                self.log(f"error sending data: {e}")
                time.sleep(1)


    def failure(self):
        timestamp = int(time.time())
        runtime = time.time() - self.start_time

        self.state = self.get_state()

        exc_type, exc_value, exc_traceback = sys.exc_info()

        data={
            'success': False,
            'key': self.function_name,
            'timestamp': timestamp,
            'runtime': runtime,
            'version': VERSION,
            'exception_type': str(exc_type.__name__),
            'exception_message': str(exc_value),
        }

        if 'exception_type' not in self.state or 'exception_message' not in self.state or data['exception_type'] != self.state['exception_type'] or data['exception_message'] != self.state['exception_message']:
            trace_identifier = f"{self.function_name}_{int(time.time() * 1000000)}"

            exception = traceback.format_exc()

            content = f"Function: {self.function_name}\n"
            content += f"Runtime: {runtime:.2f} seconds\n"
            content += f"Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            content += traceback.format_exc()

            url = f"{self.endpoint}/trace/{self.function_name}/{trace_identifier}"

            exception = traceback.format_exception_only(*sys.exc_info()[:2])[-1].strip()

            self.pushover.send_message(exception, title=self.function_name, url=url)

            data['trace_identifier'] = trace_identifier
            data['trace'] = content

        for i in range(0, 5):
            try:
                resp = requests.post(
                    f"{self.endpoint}/tracing/{self.function_name}",
                    json=data,
                    headers={
                        'Content-Type': 'application/json'
                    },
                    timeout=10,
                    auth=self.auth,
                    proxies=self.proxies
                )

                if resp.status_code == 200:
                    break

            except Exception as e:
                pass
