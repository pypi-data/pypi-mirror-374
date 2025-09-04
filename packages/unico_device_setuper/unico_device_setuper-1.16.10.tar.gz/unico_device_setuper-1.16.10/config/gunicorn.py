import os  # noqa: INP001

from unico_device_setuper.lib import cfg

_config = cfg.read_config().gunicorn

accesslog = _config.accesslog
errorlog = _config.errorlog
loglevel = _config.loglevel
capture_output = _config.capture_output
timeout = round(_config.timeout.total_seconds())
worker_class = 'uvicorn.workers.UvicornWorker'
bind = f'{_config.host}:{_config.port}'

if _config.workers:
    workers = _config.workers
else:
    workers = cpu_count - 1 if (cpu_count := os.cpu_count()) is not None and cpu_count > 1 else 1
