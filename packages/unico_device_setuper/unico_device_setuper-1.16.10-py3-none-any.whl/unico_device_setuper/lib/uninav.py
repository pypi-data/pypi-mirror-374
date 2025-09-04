import contextlib
import dataclasses
import pathlib
import typing

import bs4
import httpx

from unico_device_setuper.lib import aapt, adb, cnsl, env, pkg, unitech, util

PACKAGE_NAME = 'com.unico.dev.appmobile'
STATIC_UNINAV_RELEASES_PATH = 'unico-navigation-releases/'
ANDROID_EXTERNAL_DATA_DIR = pathlib.Path('/') / 'storage' / 'emulated' / '0' / 'Android' / 'data'


@dataclasses.dataclass
class VersionName:
    values: tuple[int, int, int, int]

    @staticmethod
    def parse(s: str):
        nums = list(map(util.parse_int, s.split('.')))
        if not util.no_none(nums):
            return None

        nums = tuple(nums)
        if len(nums) != 4:
            return None

        return VersionName(nums)

    def __str__(self):
        return '.'.join(map(str, self.values))

    def get_uninav_download_url(self, unitech_env: env.UnitechEnv):
        return (
            unitech_env.static_base_url
            / STATIC_UNINAV_RELEASES_PATH
            / f'unico-navigationV{self}.apk'
        )

    @staticmethod
    async def list(unitech_env: env.UnitechEnv, http_client: httpx.AsyncClient):
        response = await http_client.get(unitech_env.static_base_url / STATIC_UNINAV_RELEASES_PATH)
        assert response.status_code == 200, (response.url, response.status_code, response.text)
        apk_prefix = 'unico-navigationV'
        apk_suffix = '.apk'
        return [
            version
            for link in bs4.BeautifulSoup(response.text, 'html.parser').find_all('a')
            if isinstance(link, bs4.Tag)
            and (apk_name := link.get('href')) is not None
            and isinstance(apk_name, str)
            and apk_name.startswith(apk_prefix)
            and apk_name.endswith(apk_suffix)
            and (
                version := VersionName.parse(
                    apk_name.removeprefix(apk_prefix).removesuffix(apk_suffix)
                )
            )
            is not None
        ]

    @staticmethod
    async def get_client_default(unitech_client: unitech.Client):
        change_log = await unitech.get_device_update_change_log.request(unitech_client)
        assert isinstance(change_log, unitech.ChangelogResponse)
        return VersionName.parse(change_log.latest_version_name)

    @staticmethod
    async def choose(
        unitech_env: env.UnitechEnv, unitech_client: unitech.Client, http_client: httpx.AsyncClient
    ):
        client_default_version = await VersionName.get_client_default(unitech_client)
        cnsl.print_blue('Choisir une version de Uninav:')
        versions = await VersionName.list(unitech_env, http_client)
        return await cnsl.print_choose(
            sorted(versions, key=lambda v: v.values),
            prompt='Version: ',
            formater=lambda v: str(v)
            + (' (version du client)' if v == client_default_version else ''),
        )


def get_installed_version(adb: adb.Adb, aapt: aapt.Aapt):
    return pkg.InstalledPackage[VersionName].get(
        PACKAGE_NAME, adb, aapt, version_parser=VersionName.parse
    )


@dataclasses.dataclass
class Uninav:
    adb: adb.Adb
    aapt: aapt.Aapt

    async def install_apk(self, apk_path: pathlib.Path):
        with contextlib.suppress(util.SubprocessError):
            await self.adb.uninstall(PACKAGE_NAME)

        await self.adb.install(apk_path)

    @contextlib.asynccontextmanager
    async def _start_activity(
        self,
        activity_name: str,
        min_version: VersionName,
        action: str,
        args: dict[str, str | int] | None = None,
    ):
        installed = await get_installed_version(self.adb, self.aapt)
        if installed is None:
            cnsl.warn("Uninav n'est pas installé")
            yield False
            return

        if installed.version.values < min_version.values:
            cnsl.warn(
                f'Uninav {installed.version} est installé, '
                f'mais Uninav {min_version} est requis pour {action}'
            )
            yield False
            return

        extra = ''
        for key, value in (args or {}).items():
            match value:
                case str():
                    extra += f' --es {key} {value}'
                case int():
                    extra += f' --ei {key} {value}'

        await self.adb.shell(f'am start -n {PACKAGE_NAME}/.core.setuper.{activity_name}{extra}')
        yield True
        await self.stop()

    @contextlib.asynccontextmanager
    async def start_sygic_files_io_activity(
        self, kind: typing.Literal['import', 'export'], port: int, packet_size: int
    ):
        app_external_data_dir = ANDROID_EXTERNAL_DATA_DIR / PACKAGE_NAME
        async with self.adb.reverse(port) as remote_port:
            await self.adb.shell(f'mkdir -p {app_external_data_dir / 'files'}')
            with contextlib.suppress(util.SubprocessError):
                await self.adb.shell(f'chmod 777 {app_external_data_dir}')
            with contextlib.suppress(util.SubprocessError):
                await self.adb.shell(f'chmod 777 {app_external_data_dir / 'files'}')
            async with self._start_activity(
                'SygicFilesIoActivity',
                min_version=VersionName((6, 15, 0, 0)),
                action='manipuler les cartes Sygic',
                args={'SOCKET_PORT': remote_port, 'IO_KIND': kind, 'PACKET_SIZE': packet_size},
            ) as is_launched:
                yield is_launched

    def start_id_device_logger_activity(self):
        return self._start_activity(
            'IdDeviceLoggerActivity',
            min_version=VersionName((6, 14, 0, 0)),
            action="obtenir l'identifiant de l'appareil",
        )

    async def stop(self):
        await pkg.close_package(self.adb, PACKAGE_NAME)
