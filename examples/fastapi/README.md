# Pyencrypt FastAPI Example

This example shows how to use `pyencrypt` with FastAPI.


## How to use
### Quick Start with Docker
See the shared Docker notes in [../README.md](../README.md#docker).

### Manual Installation
```shell
pip install -r requirements.txt

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# Or run with FastAPI
fastapi dev app/main.py
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

        file_loader = loader.EncryptFileImporter("")
        if file_loader.license is True:
            file_loader.check()
    except ModuleNotFoundError:
        pass
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))
```
Then use it in the login handler with `Depends` in [app/routers/login.py](./app/routers/login.py):
```python
@router.get("/login/")
async def login(
    username: str = Query(...),
    password: str = Query(...),
    _: None = Depends(check_license),
):
    ...
```

## Notes
* `main.py` should remain unencrypted. 
* Alternatively, rename the original (`app/main.pye` → `app/main_enc.pye`) and create a small unencrypted wrapper (app/main.py) that imports from the renamed module.:
	```shell
	RUN mv app/main.py app/main_enc.py,
	RUN echo 'from app.main_enc import *' > app/main.py
	```
* To use the `fastapi` CLI command, install `FastAPI` with standard extras: `pip install "fastapi[standard]"`.

### Loader Installation
For Loader installation instructions, see the examples [ README](../README.md#loader-installation).
* Add `import loader` at the top of `app/__init__.py`
