# Frequently Asked Questions

## Gunicorn Worker keep restarting when starting server (`WORKER TIMEOUT`)
```shell
[2025-04-01 14:54:24 +0800] [15231] [INFO] Starting gunicorn 20.1.0
[2025-04-01 14:54:24 +0800] [15231] [INFO] Listening at: http://0.0.0.0:8000 (15231)
[2025-04-01 14:54:24 +0800] [15231] [INFO] Using worker: gevent
[2025-04-01 14:54:24 +0800] [15233] [INFO] Booting worker with pid: 15233
[2025-04-01 14:54:55 +0800] [15231] [CRITICAL] WORKER TIMEOUT (pid:15233)
INFO 2025-04-01 14:54:55: Worker exiting (pid: 15233)
[2025-04-01 14:54:55 +0800] [15409] [INFO] Booting worker with pid: 15409
```

Code decryption may increases application startup time, which may cause the worker to exceed the default timeout threshold (30 seconds), leading to `WORKER TIMEOUT` errors.

To resolve this, increase Gunicorn’s [--timeout](https://docs.gunicorn.org/en/latest/settings.html#timeout) setting to factor in the additional decryption time.
```shell
# Set timeout to 60 seconds via command line:
gunicorn --workers 4 --timeout 60 --worker-class gevent your_app:app  

# Or configure via a config file (gunicorn.py):  
timeout = 60  
worker_class = "gevent"  
```