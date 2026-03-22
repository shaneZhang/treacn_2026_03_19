import os
import multiprocessing

bind = f"{os.environ.get('GUNICORN_BIND_ADDRESS', '0.0.0.0')}:{os.environ.get('GUNICORN_BIND_PORT', '5000')}"
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
threads = int(os.environ.get('GUNICORN_THREADS', 2))
worker_class = 'gevent'
timeout = int(os.environ.get('GUNICORN_TIMEOUT', 120))
graceful_timeout = int(os.environ.get('GUNICORN_GRACEFUL_TIMEOUT', 120))
keepalive = int(os.environ.get('GUNICORN_KEEPALIVE', 5))
max_requests = int(os.environ.get('GUNICORN_MAX_REQUESTS', 1000))
max_requests_jitter = int(os.environ.get('GUNICORN_MAX_REQUESTS_JITTER', 50))
preload_app = True
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = '/app/tmp'
accesslog = '-'
errorlog = '-'
loglevel = os.environ.get('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
capture_output = True
enable_stdio_inheritance = True
def on_starting(server):
    server.log.info("Starting Interest Social API Server")

def on_exit(server):
    server.log.info("Shutting down Interest Social API Server")

def worker_exit(server, worker):
    server.log.info(f"Worker {worker.pid} exited")

def pre_fork(server, worker):
    pass

def post_fork(server, worker):
    server.log.info(f"Worker spawned with PID: {worker.pid}")

def pre_exec(server):
    server.log.info("Forked child, re-executing.")

def worker_int(worker):
    worker.log.info(f"Worker {worker.pid} received INT or QUIT signal")

def worker_abort(worker):
    worker.log.info(f"Worker {worker.pid} received SIGABRT signal")
