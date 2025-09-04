import typing

from unico_device_setuper.cli import stp
from unico_device_setuper.lib import aio, api, cnsl, pkg, util


async def uninstall_package(
    package_name: str, installed_package_names: typing.Container[str], setup: stp.Setup
):
    if package_name not in installed_package_names:
        cnsl.print_gray(f'{package_name} déjà désinstallé')
        return
    try:
        await setup.adb.shell(f'pm uninstall -k --user 0 {package_name}')
        cnsl.print_greeen(f'{package_name} désinstallé avec succès')
    except util.SubprocessError:
        cnsl.print_red(f'Erreur lors de la désinstallation de {package_name}')


async def uninstall_listed_packages(
    installed_package_names: typing.Container[str], setup: stp.Setup
):
    packages = await api.packages_get_all.request(setup.api_client)
    assert isinstance(packages, api.PackagesModel), packages
    await aio.gather_unordered(
        (
            uninstall_package(package.name, installed_package_names, setup)
            for package in (
                packages.packages.additional_properties if packages.packages else {}
            ).values()
            if not package.disabled
        ),
        max_concurrency=20,
    )


LAUNCHER_APP_PACKAGE_NAMES = ['com.sec.android.app.launcher']


async def clear_launcher_app_storage(
    installed_package_names: typing.Container[str], setup: stp.Setup
):
    for laucher_app_package_name in LAUNCHER_APP_PACKAGE_NAMES:
        if laucher_app_package_name in installed_package_names:
            await setup.adb.shell(f'pm clear {laucher_app_package_name}')


@cnsl.command(
    'Désinstallation des applications par défaut', 'Applications par défaut desinstallées'
)
async def uninstall_packages(setup: stp.Setup):
    if await setup.get_skip_uninstall_packages():
        cnsl.warn('Désinstallation des applications par défaut ignorée')
        return False

    apk_path_map = await pkg.get_apk_path_map(setup.adb)
    await uninstall_listed_packages(apk_path_map, setup)
    await clear_launcher_app_storage(apk_path_map, setup)
    return True
