# Pyencrypt Flask Example

This example shows how to use `pyencrypt` with Flask.

## How to use
### Quick Start with Docker
```shell
docker compose up -d
```

### Manual Installation
```shell
pip install -r requirements.txt

flask --app app run --host 0.0.0.0 --port 8000
# Or run with gunicorn
# gunicorn -b 0.0.0.0:8000 "app:create_app()"
```

## Build Docker Image
```shell
docker build -f Dockerfile -t demo:v1.0 .
docker build -f Dockerfile -t demo:v1.0 --build-arg ENCRYPT_KEY=YOUR_FIXED_KEY .
docker save demo:v1.0| gzip > demo:v1.0_v1.0.tar.gz
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
None

### Loader
* Copy `encrypted/loader*.so` to the project root.
* Add `import loader` at the top of `app/__init__.py`.
* Don't forget to remove `encrypted` and `build` directory.

### Docker
* For preventing to extract origin layer from image, using [`scratch`](https://docs.docker.com/build/building/base-images/#create-a-base-image) to convert image to single layer.
  > [docker: extracting a layer from a image - Stack Overflow](https://stackoverflow.com/questions/40575752/docker-extracting-a-layer-from-a-image)
* Remember to specify `WORKDIR`, `ENTRYPOINT` and other in `Dockerfile` again after `scratch`.
