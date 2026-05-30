# Pyencrypt Flask Example

This example shows how to use `pyencrypt` with Flask.

## How to use
### Quick Start with Docker
See the shared Docker notes in [../README.md](../README.md#docker).
### Manual Installation
```shell
pip install -r requirements.txt

flask --app app run --host 0.0.0.0 --port 8000
# Or run with gunicorn
# gunicorn -b 0.0.0.0:8000 "app:create_app()"
```

## Test Endpoints
* Flask CLI: `curl http://127.0.0.1:8001/account/login/\?username\=admin\&password\=admin`
* gunicorn: `curl http://127.0.0.1:8002/account/login/\?username\=admin\&password\=admin`

## With License
```shell
pyencrypt encrypt --in-place --yes --with-license --after="$(date -d '+1 minute' '+%Y-%m-%dT%H:%M:%S %z')"
```

Add a decorator to your login view (e.g., [`app/auth.py`](./app/auth.py)) to check the license:
```python
def _check_license() -> str | None:
    try:
        import loader

        file_loader = loader.EncryptFileLoader("")
        if file_loader.license is True:
            file_loader.check()
    except ModuleNotFoundError:
        return None
    except Exception as exc:
        return str(exc)
    return None


def require_license(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        error = _check_license()
        if error:
            return jsonify({"message": error}), 403
        return view(*args, **kwargs)

    return wrapper
    
@bp.get("/login/")
@require_license
def login():
    ...
```

## Notes
### Loader Installation
For Loader installation instructions, see the examples [ README](../README.md#loader-installation).
* Add `import loader` at the top of `app/__init__.py`.

