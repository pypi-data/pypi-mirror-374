import contextlib
import pathlib

from unico_device_setuper.cli import stp
from unico_device_setuper.lib import aio, cnsl, datadir, dl, pkg, uninav, util


async def get_is_already_installed(
    version_name: uninav.VersionName, uninav_install_path: pathlib.Path, setup: stp.Setup
):
    installed = await uninav.get_installed_version(setup.adb, setup.aapt)
    if installed is not None:
        cnsl.print_gray(f'Uninav {installed.version} est déjà installé')
        if installed.version == version_name:
            checksum = util.get_local_checksum(uninav_install_path)
            if installed.checksum == checksum:
                return True

            cnsl.print_gray('La somme de contrôle de la version installée ne corresponds pas')

    return False


async def grant_permission(permission: str, setup: stp.Setup):
    with contextlib.suppress(util.SubprocessError):
        await setup.adb.shell(f'pm grant {uninav.PACKAGE_NAME} {permission}')


async def grant_permissions(setup: stp.Setup):
    apk_path_map = await pkg.get_apk_path_map(setup.adb)
    permissions = await pkg.get_permissions_from_apk_path(
        apk_path_map[uninav.PACKAGE_NAME], setup.aapt
    )

    await aio.gather_unordered(grant_permission(permission, setup) for permission in permissions)


@cnsl.command('Installation de Uninav', 'Uninav installé')
async def install_uninav(setup: stp.Setup):
    version_name = await setup.get_uninav_version()
    if version_name is None:
        return False

    uninav_install_path = (
        datadir.get() / 'uninav' / setup.unitech_env.name.lower() / f'{version_name}.apk'
    )

    if not uninav_install_path.exists():
        await dl.download_url(
            version_name.get_uninav_download_url(setup.unitech_env),
            uninav_install_path,
            setup.http_client,
            uninav_install_path.name,
        )

    if not await get_is_already_installed(version_name, uninav_install_path, setup):
        with cnsl.step(f"installation de l'APK {version_name}"):
            await setup.uninav.install_apk(uninav_install_path)

    await grant_permissions(setup)
    return True
