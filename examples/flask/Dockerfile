FROM python:3.10-bullseye as build

WORKDIR /root/demo

RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

ARG PYPI_URL=https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
RUN pip config set global.index-url $PYPI_URL

RUN sed -i 's@deb.debian.org@mirrors.aliyun.com@g' /etc/apt/sources.list
RUN sed -i 's@security.debian.org@mirrors.aliyun.com@g' /etc/apt/sources.list

RUN apt update
RUN apt install gettext git vim lrzsz less gcc -y

ADD requirements.txt /root/demo
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app /root/demo/app

# --- Encryption ---
ARG ENCRYPT_KEY
ENV PYE_ENCRYPT_KEY=$ENCRYPT_KEY

RUN pip install pyencrypt-pye
# RUN pyencrypt encrypt --in-place --yes .
RUN pyencrypt encrypt --in-place --yes --with-license --after="$(date -d '+1 minute' '+%Y-%m-%dT%H:%M:%S %z')" .
RUN cp encrypted/loader*.so .
RUN rm -rf encrypted build/

RUN echo "import loader\n$(cat app/__init__.py)" > app/__init__.py


RUN pip uninstall pyencrypt-pye pycryptodome Cython python-minifier -y
# --- Encryption ---


FROM scratch
COPY --from=build / /

WORKDIR /root/demo
EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:create_app()"]
