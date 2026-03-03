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

## Setuptools build fails: `Multiple top-level packages discovered in a flat-layout`
```shell
[root@xxxxxx export]# pyencrypt encrypt --in-place --yes --with-license --after="$(date -d '+6 month' '+%Y-%m-%dT%H:%M:%S %z')" .
Your randomly encryption 🔑 is jhzSU9l+HAtRS0NnJxkD/mYbxgFhUNxogPXO1iq9L/w=
🔐 Encrypting  [####################################]  100%
Generate license file successfully. Your license file is located in license.lic

Compiling /export/encrypted/loader.py because it changed.
[1/1] Cythonizing /export/encrypted/loader.py
/home/export/servers/python3.13/lib/python3.13/site-packages/setuptools/_distutils/dist.py:287: UserWarning: Unknown distribution option: 'cdclass'
  warnings.warn(msg)
error: Multiple top-level packages discovered in a flat-layout: ['app', 'init', 'logs', 'sqls', 'licenses', 'encrypted', 'generated', 'script_in_git'].

To avoid accidental inclusion of unwanted files or directories,
setuptools will not proceed with this build.

If you are trying to create a single distribution with multiple packages
on purpose, you should not rely on automatic discovery.
Instead, consider the following options:

1. set up custom discovery (`find` directive with `include` or `exclude`)
2. use a `src-layout`
3. explicitly set `py_modules` or `packages` with a list of names

To find more information, look for "package discovery" on setuptools docs.
```

This happens when `setuptools` tries to auto-discover Python packages from a [`flat-layout`](https://setuptools.pypa.io/en/latest/userguide/package_discovery.html#flat-layout) project root (no `src/` directory) but finds multiple top-level directories that look like importable packages. To prevent accidentally shipping extra folders, `setuptools` aborts the build.

Fix: explicitly tell setuptools which package(s) to include by adding the following configuration to your `pyproject.toml`; alternatively, switch to [`src-layout`](https://setuptools.pypa.io/en/latest/userguide/package_discovery.html#src-layout).
```toml
[tool.setuptools.packages.find]
where = ["<project_root>"]
include = ["*"]
namespaces = false
```
