import contextlib
import pathlib
import tomllib

import platformdirs
import slugify

import unico_device_setuper
from unico_device_setuper.lib import util

BASE_DIR = util.module_path(unico_device_setuper).parent.parent


def is_release_version():
    pyproject_path = BASE_DIR / 'pyproject.toml'
    with contextlib.suppress(FileNotFoundError):
        pyproject = tomllib.loads(pyproject_path.read_text())
        if slugify.slugify(pyproject.get('project', {}).get('name'), separator='_') == (
            unico_device_setuper.PACKAGE_NAME
        ):
            return False
    return True


def get():
    if is_release_version():
        return pathlib.Path(platformdirs.user_data_dir(appname=util.APP_NAME)).absolute()

    return BASE_DIR / 'data'


@contextlib.contextmanager
def get_temporary():
    with util.temporary_dir(get()) as dir:
        yield dir
