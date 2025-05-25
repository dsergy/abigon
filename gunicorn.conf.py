import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = '/home/art/mvp/logs/access.log'
errorlog = '/home/art/mvp/logs/error.log'
loglevel = 'info'

# Process naming
proc_name = 'mvp'

# Server mechanics
daemon = False
pidfile = '/home/art/mvp/gunicorn.pid'
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None

# Server hooks
def on_starting(server):
    """
    Called just before the master process is initialized.
    """
    pass

def on_reload(server):
    """
    Called to recycle workers during a reload via SIGHUP.
    """
    pass

def post_fork(server, worker):
    """
    Called just after a worker has been forked.
    """
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_fork(server, worker):
    """
    Called just prior to forking the worker subprocess.
    """
    pass

def pre_exec(server):
    """
    Called just prior to forking the master process.
    """
    server.log.info("Forked master process, reloading workers")

def when_ready(server):
    """
    Called just after the server is started.
    """
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    """
    Called when a worker receives SIGINT or SIGQUIT.
    """
    worker.log.info("worker received INT or QUIT signal")

def worker_abort(worker):
    """
    Called when a worker receives SIGABRT.
    """
    worker.log.info("worker received SIGABRT signal")

def worker_exit(server, worker):
    """
    Called when a worker exits.
    """
    server.log.info("Worker exited (pid: %s)", worker.pid)

def nworkers_changed(server, new_value, old_value):
    """
    Called when the number of workers is changed.
    """
    server.log.info("Number of workers changed from %s to %s", old_value, new_value)

def on_exit(server):
    """
    Called just before exiting the master process.
    """
    server.log.info("Master process is exiting")

# Graceful timeout
graceful_timeout = 30

# Max requests
max_requests = 1000
max_requests_jitter = 50

# Worker class
worker_class = 'sync'

# Worker connections
worker_connections = 1000

# Timeout
timeout = 30

# Keep-alive
keepalive = 2

# Server mechanics
daemon = False
pidfile = '/home/art/mvp/gunicorn.pid'
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None

# Server hooks
def on_starting(server):
    """
    Called just before the master process is initialized.
    """
    pass

def on_reload(server):
    """
    Called to recycle workers during a reload via SIGHUP.
    """
    pass

def post_fork(server, worker):
    """
    Called just after a worker has been forked.
    """
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_fork(server, worker):
    """
    Called just prior to forking the worker subprocess.
    """
    pass

def pre_exec(server):
    """
    Called just prior to forking the master process.
    """
    server.log.info("Forked master process, reloading workers")

def when_ready(server):
    """
    Called just after the server is started.
    """
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    """
    Called when a worker receives SIGINT or SIGQUIT.
    """
    worker.log.info("worker received INT or QUIT signal")

def worker_abort(worker):
    """
    Called when a worker receives SIGABRT.
    """
    worker.log.info("worker received SIGABRT signal")

def worker_exit(server, worker):
    """
    Called when a worker exits.
    """
    server.log.info("Worker exited (pid: %s)", worker.pid)

def nworkers_changed(server, new_value, old_value):
    """
    Called when the number of workers is changed.
    """
    server.log.info("Number of workers changed from %s to %s", old_value, new_value)

def on_exit(server):
    """
    Called just before exiting the master process.
    """
    server.log.info("Master process is exiting") 