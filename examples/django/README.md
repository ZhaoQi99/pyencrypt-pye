# Pyencrypt Django Example

This example shows how to use `pyencrypt` with Django.

## How to use
See the Docker usage instructions in examples [README](../README.md#docker).

## Test
* runserver: `curl http://127.0.0.1:8001/account/login/\?username\=admin\&password\=admin`
* gunicorn: `curl http://127.0.0.1:8002/account/login/\?username\=admin\&password\=admin`

## With license
`pyencrypt encrypt --in-place --yes --with-license --after="$(date -d '+1 minute' '+%Y-%m-%dT%H:%M:%S %z')"`

Add the following code to your login view (e.g., [`account/views.py`](./account/views.py)) to check the license:
```python
try:
    import loader

    file_loader = loader.EncryptFileLoader("")
    if file_loader.license is True:
        file_loader.check()
except ModuleNotFoundError:
    pass
except Exception as e:
    return JsonResponse({"message": str(e)}, status=403)
```

## Note
* `manage.py` shouldn't be encrypted.
* `gunicorn.py` shouldn't be encrypted.

### Loader Installation
For Loader installation instructions, see the examples [ README](../README.md#loader-installation).
* Copy `encrypted/loader*.so` to where `manage.py` is located.
* Add `import loader` at the top of `<project>/__init__.py`.
