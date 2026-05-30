# Pyencrypt Examples

This directory contains examples of how to use pyencrypt.

* [`Django`](./django): Pyencrypt Django Example
* [`FastAPI`](./fastapi): Pyencrypt FastAPI Example
* [`Flask`](./flask): Pyencrypt Flask Example


## Docker

The following Docker-related steps are shared by all examples in this directory.

### Quick Start
```shell
docker compose up -d
```

### Build Docker Image
```shell
docker build -f Dockerfile -t demo:v1.0 .
docker build -f Dockerfile -t demo:v1.0 --build-arg ENCRYPT_KEY=YOUR_FIXED_KEY .
docker save demo:v1.0| gzip > demo:v1.0_v1.0.tar.gz
```

### Image Protection (use scratch to prevent layer extraction)
* For preventing to extract origin layer from image, using [`scratch`](https://docs.docker.com/build/building/base-images/#create-a-base-image) to convert image to single layer.
  > [docker: extracting a layer from a image - Stack Overflow](https://stackoverflow.com/questions/40575752/docker-extracting-a-layer-from-a-image)
* Remember to specify `WORKDIR`, `ENTRYPOINT` and other in `Dockerfile` again after `scratch`.
  
## Loader Installation
1. Copy `encrypted/loader*.so` to the project root or the location specified by the example.
2. Add `import loader` at the top of the project entry module.
3. Don't forget to remove `encrypted` and `build` directory.