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
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or run with FastAPI
fastapi dev main.py
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

### Direct API Calls

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
* `main.py` shouldn't be encrypted

### Loader
* Copy `encrypted/loader*.so` to the project root
* Add `import loader` at the top of `__init__.py`
* Don't forget to remove `encrypted` and `build` directory.

### Docker Best Practices
* Uses multi-stage build for smaller final image
* Converts to single layer using `scratch` base image
* Remember to specify `WORKDIR`, `ENTRYPOINT` in Dockerfile after `scratch`