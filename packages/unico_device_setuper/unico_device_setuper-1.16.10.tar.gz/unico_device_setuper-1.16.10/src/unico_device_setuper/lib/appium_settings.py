import contextlib
import dataclasses
import pathlib

import httpx

from unico_device_setuper.lib import aapt, adb, cnsl, datadir, dl, pkg, rl, util

PACKAGE_NAME = 'io.appium.settings'


@dataclasses.dataclass
class InstalledAppiumSettings:
    version: str
    check_sum: str


async def get_is_already_installed(
    version: str, local_apk_path: pathlib.Path, adb: adb.Adb, aapt: aapt.Aapt
):
    installed = await pkg.InstalledPackage[str].get(PACKAGE_NAME, adb, aapt, str)
    if installed is not None:
        cnsl.print_gray(f'Appium settings v{version} est déjà installé')
        if installed.version == version:
            checksum = util.get_local_checksum(local_apk_path)
            if installed.checksum == checksum:
                return True

            cnsl.print_gray('La somme de contrôle de la version installée ne corresponds pas')

    return False


@dataclasses.dataclass
class AppiumSettings:
    adb_ctx: adb.Adb

    def set_position(self, longitude: float, latitude: float, speed: float, bearing: float):
        return self.adb_ctx.shell(
            'am start-foreground-service'
            ' --user 0'
            f' -n {PACKAGE_NAME}/.LocationService'
            f' --es longitude {longitude}'
            f' --es latitude {latitude}'
            f' --es speed {speed}'
            f' --es bearing {bearing}'
        )

    @classmethod
    @contextlib.asynccontextmanager
    async def make(
        cls, version: str, adb: adb.Adb, aapt: aapt.Aapt, http_client: httpx.AsyncClient
    ):
        apk_path = datadir.get() / 'appium_settings' / f'{version}.apk'
        if not util.is_file(apk_path):
            await dl.download_url(
                rl.Url(
                    f'https://github.com/appium/io.appium.settings/releases/download/v{version}/settings_apk-debug.apk'
                ),
                apk_path,
                http_client,
                label=apk_path.name,
            )

        if not await get_is_already_installed(version, apk_path, adb, aapt):
            with cnsl.step('Installation de Appium settings'):
                with contextlib.suppress(util.SubprocessError):
                    await adb.uninstall(PACKAGE_NAME)

                await adb.install(apk_path)

        await adb.shell(f'appops set {PACKAGE_NAME} android:mock_location allow')
        await adb.shell(f'pm grant {PACKAGE_NAME} android.permission.ACCESS_FINE_LOCATION')
        with contextlib.suppress(Exception):
            await adb.shell(f'cmd notification suspend-package {PACKAGE_NAME}')

        try:
            yield AppiumSettings(adb_ctx=adb)
        finally:
            with contextlib.suppress(util.SubprocessError):
                await adb.shell(f'am stopservice {PACKAGE_NAME}/.LocationService')
            with contextlib.suppress(util.SubprocessError):
                await adb.shell(f'appops set {PACKAGE_NAME} android:mock_location deny')
