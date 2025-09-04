import datetime
import enum
import os

import oci_client
import pydantic
import slcfg

import unico_device_setuper
from unico_device_setuper.lib import util


class Oci(pydantic.BaseModel):
    client: oci_client.Config
    bucket_name: str
    upload_part_size: int


class Security(pydantic.BaseModel):
    secret: str
    algorithms: list[str]
    admin_permissions: int


class Gunicorn(pydantic.BaseModel):
    accesslog: str
    errorlog: str
    loglevel: str
    capture_output: bool
    timeout: datetime.timedelta
    host: str
    port: int
    workers: int | None


class Config(pydantic.BaseModel):
    oci: Oci
    security: Security
    gunicorn: Gunicorn


class Env(slcfg.Environment):
    LOCAL = enum.auto()
    DEPLOYED = enum.auto()


def read_config():
    base_path = util.module_path(unico_device_setuper).parent.parent
    os.chdir(base_path)
    env = Env.get_from_env('DEVICE_SETUPER_ENV', default=Env.LOCAL)
    env_name = env.name.lower()
    return slcfg.read_config(
        Config,
        [
            slcfg.toml_file_layer(base_path / 'config' / 'base.toml'),
            slcfg.toml_file_layer(base_path / 'config' / f'{env_name}.toml'),
            slcfg.toml_file_layer(base_path / 'config.toml', optional=True),
            slcfg.env_base64_toml_layer('DEVICE_SETUPER_CONFIG', optional=True),
        ],
    )
