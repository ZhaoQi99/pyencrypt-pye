# Pyencrypt Django Example

This example shows how to use `pyencrypt` with Django.

## How to use
```shell
docker compose up -d
```

## Build image
```shell
docker build -f Dockerfile -t demo:v1.0 .
docker build -f Dockerfile -t demo:v1.0 --build-arg ENCRYPT_KEY=YOUR_FIXED_KEY .
docker save demo:v1.0| gzip > demo:v1.0_v1.0.tar.gz
```

## Test
* runserver: `curl http://127.0.0.1:8001/account/login/?username=admin&password=admin`
* gunicorn: `curl http://127.0.0.1:8002/account/login/?username=admin&password=admin`

## Note
* `manage.py` shouldn't be encrypted.
* `gunicorn.py` shouldn't be encrypted.

### Loader
* Copy `encrypted/loader*.so` to where `manage.py` is located.
* Add `import loader` at the top of `<project>/__init__.py`.
* Don't forget to remove `encrypted` and `build` directory.

### Docker
* For preventing to extract origin layer from image, using [`scratch`](https://docs.docker.com/build/building/base-images/#create-a-base-image) to convert image to single layer.
  > [docker: extracting a layer from a image - Stack Overflow](https://stackoverflow.com/questions/40575752/docker-extracting-a-layer-from-a-image)
* Remember to specify `WORKDIR`, `ENTRYPOINT` and other in `Dockerfile` again after `scratch`.