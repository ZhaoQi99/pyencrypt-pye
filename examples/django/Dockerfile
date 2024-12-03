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
RUN pip install -r requirements.txt
COPY . /root/demo/

RUN python manage.py collectstatic --noinput

# --- Encryption ---
RUN pip install git+https://github.com/ZhaoQi99/pyencrypt-pye.git
RUN pyencrypt encrypt --in-place --yes .
RUN cp encrypted/loader*.so .
RUN rm -rf encrypted build/

RUN echo "import loader\n$(cat demo/__init__.py)" > demo/__init__.py

COPY manage.py /root/demo
COPY demo/gunicorn.py /root/demo/demo

RUN pip uninstall pyencrypt-pye pycryptodome Cython python-minifier -y
# --- Encryption ---


FROM scratch
COPY --from=build / /

WORKDIR /root/demo
EXPOSE 8000
# ENTRYPOINT [ "bash", "/root/demo/bin/start.sh"]
