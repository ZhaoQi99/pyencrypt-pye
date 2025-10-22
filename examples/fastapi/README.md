# Pyencrypt FastAPI Example

This example shows how to use `pyencrypt` with FastAPI.


## How to use
### Quick Start with Docker
```shell
docker compose up -d
```

### Manual Installation
```shell
pip install -r requirements.txt

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# Or run with FastAPI
fastapi dev app/main.py
```

## Build Docker Image
```shell
docker build -f Dockerfile -t demo:v1.0 .
docker build -f Dockerfile -t demo:v1.0 --build-arg ENCRYPT_KEY=YOUR_FIXED_KEY .
docker save demo:v1.0| gzip > demo:v1.0_v1.0.tar.gz
```

## Test Endpoints
* FastAPI Dev: `curl http://127.0.0.1:8001/account/login/\?username\=admin\&password\=admin`
* uvicorn: `curl http://127.0.0.1:8002/account/login/\?username\=admin\&password\=admin`

## With License
```shell
pyencrypt encrypt --in-place --yes --with-license --after="$(date -d '+1 minute' '+%Y-%m-%dT%H:%M:%S %z')"
```

The license checking is implemented as a FastAPI dependency in [`app/dependencies.py`](./app/dependencies.py):
```python
def check_license() -> None:
    try:
        import loader

        file_loader = loader.EncryptFileLoader("")
        if file_loader.license is True:
            file_loader.check()
    except ModuleNotFoundError:
        pass
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))
```

## Notes
* `main.py` should remain unencrypted. 
* Alternatively, rename the original (`app/main.pye` → `app/main_enc.pye`) and create a small unencrypted wrapper (app/main.py) that imports from the renamed module.:
	```shell
	RUN mv app/main.py app/main_enc.py,
	RUN echo 'from app.main_enc import *' > app/main.py
	```
* To use the `fastapi` CLI command, install `FastAPI` with standard extras: `pip install "fastapi[standard]"`.

### Loader
* Copy `encrypted/loader*.so` to the project root.
* Add `import loader` at the top of `app/__init__.py`
* Don't forget to remove `encrypted` and `build` directory.

### Docker
* For preventing to extract origin layer from image, using [`scratch`](https://docs.docker.com/build/building/base-images/#create-a-base-image) to convert image to single layer.
  > [docker: extracting a layer from a image - Stack Overflow](https://stackoverflow.com/questions/40575752/docker-extracting-a-layer-from-a-image)
* Remember to specify `WORKDIR`, `ENTRYPOINT` and other in `Dockerfile` again after `scratch`.