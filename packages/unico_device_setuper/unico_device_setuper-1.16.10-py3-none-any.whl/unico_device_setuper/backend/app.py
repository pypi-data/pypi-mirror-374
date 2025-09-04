import uvicorn

from unico_device_setuper.backend import app_maker
from unico_device_setuper.lib import cfg

APP = app_maker.make_app_from_config(cfg.read_config())


def local_app():
    uvicorn.run(
        f'{__name__}:APP',
        reload=True,
        reload_excludes=['data/'],
        port=cfg.read_config().gunicorn.port,
        lifespan='on',
    )
