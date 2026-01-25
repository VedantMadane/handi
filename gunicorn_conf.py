import multiprocessing
import os

# Gunicorn Configuration

# Bind to 0.0.0.0:8000
bind = "0.0.0.0:8000"

# Worker Options
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"

# Logging
loglevel = "info"
accesslog = "-"  # stdout
errorlog = "-"   # stderr

# Timeout (Production might need longer for slow clients, but keep tight for API)
timeout = 120

# Keepalive
keepalive = 5

# Reload (False for production)
reload = False
