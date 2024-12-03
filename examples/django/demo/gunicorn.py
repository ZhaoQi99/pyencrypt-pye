bind = "0.0.0.0:8000"
workers = 1
worker_class = "gevent"
worker_tmp_dir = "/tmp"
pidfile = "/tmp/gunicorn.pid"
accesslog = "-"
