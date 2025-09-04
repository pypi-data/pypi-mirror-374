import contextlib
import dataclasses
import enum
import pathlib
import sys
import typing

import httpx
import slugify

from unico_device_setuper.lib import cnsl, datadir, dl, rl, util

ADB_DARWIN_DOWNLOAD_URL = rl.Url(
    'https://dl.google.com/android/repository/platform-tools-latest-darwin.zip'
)


ADB_LINUX_DOWNLOAD_URL = rl.Url(
    'https://dl.google.com/android/repository/platform-tools-latest-linux.zip'
)


SettingsNamespace: typing.TypeAlias = typing.Literal['system', 'secure', 'global']


class DeviceStatus(enum.Enum):
    DEVICE = enum.auto()
    UNAUTHORIZED = enum.auto()
    OFFLINE = enum.auto()
    NO_DEVICE = enum.auto()
    NO_STATUS = enum.auto()
    UNKNOWN_STATUS = enum.auto()
    AUTHORIZING = enum.auto()

    def format_error(self):
        match self:
            case DeviceStatus.DEVICE:
                error = None
            case DeviceStatus.UNAUTHORIZED:
                error = 'Non autorisé'
            case DeviceStatus.OFFLINE:
                error = 'Inatteignable'
            case DeviceStatus.NO_DEVICE:
                error = 'Non connecté'
            case DeviceStatus.NO_STATUS:
                error = 'Aucun status'
            case DeviceStatus.UNKNOWN_STATUS:
                error = 'Status inconnu'
            case DeviceStatus.AUTHORIZING:
                error = "En cours d'autorisation"
        return error

    @staticmethod
    def parse(value: str | None):
        if value is None:
            return DeviceStatus.NO_STATUS

        for status in DeviceStatus:
            if slugify.slugify(status.name) == slugify.slugify(value):
                return status

        cnsl.warn(f"Status de l'appareil inconnu : {value}")
        return DeviceStatus.UNKNOWN_STATUS


@dataclasses.dataclass
class DeviceInfos:
    product: str | None = None
    model: str | None = None

    def format(self):
        infos: list[str] = []
        if self.product is not None:
            infos.append(f'produit: {self.product}')
        if self.model is not None:
            infos.append(f'modèle: {self.model}')
        return ', '.join(infos)

    @staticmethod
    def parse(values: list[str]):
        infos = DeviceInfos()
        for value in values:
            name, _, info = value.partition(':')
            for field in dataclasses.fields(DeviceInfos):
                if (
                    field.name == name
                    and isinstance(field.type, type)
                    and issubclass(str, field.type)
                ):
                    setattr(infos, field.name, info)
        return infos


@dataclasses.dataclass
class Device:
    serial: str
    status: DeviceStatus
    infos: DeviceInfos

    @property
    def label(self):
        return f'{self.serial}{f' ({infos})' if (infos := self.infos.format()) else ''}'

    @staticmethod
    def parse(line: str):
        match line.split():
            case [serial, status_value, *infos_values]:
                pass
            case [serial]:
                status_value = None
                infos_values = []
            case _:
                return None

        return Device(
            serial=serial,
            status=DeviceStatus.parse(status_value),
            infos=DeviceInfos.parse(infos_values),
        )

    @staticmethod
    async def parse_all(adb: 'UndevicedAdb'):
        reached_device_list = False
        devices = list[Device]()
        for line in await adb.devices('-l'):
            if line.strip() == 'List of devices attached':
                reached_device_list = True
                continue

            if not reached_device_list:
                continue
            if (device := Device.parse(line)) is not None:
                devices.append(device)
        return devices


def _exec_gen(adb_exe: pathlib.Path, *args: object):
    return util.exec_proc(adb_exe, *map(str, args))


async def _exec(adb_exe: pathlib.Path, *args: object):
    return [line async for line in util.exec_proc(adb_exe, *map(str, args))]


@dataclasses.dataclass
class UndevicedAdb:
    adb_exe: pathlib.Path

    @contextlib.asynccontextmanager
    @staticmethod
    async def make(http_client: httpx.AsyncClient):
        adb_path = datadir.get() / 'adb'
        match sys.platform:
            case 'darwin':
                download_url = ADB_DARWIN_DOWNLOAD_URL
            case 'linux':
                download_url = ADB_LINUX_DOWNLOAD_URL
            case _:
                raise RuntimeError('plaform not supported')

        if not util.is_executable(adb_path):
            await dl.download_and_extract_zipped_executable(
                download_url, pathlib.Path('adb'), adb_path, http_client
            )
        ctx = UndevicedAdb(adb_path)
        await ctx.start_server()
        yield ctx

    async def all_devices(self):
        any_device = False
        for device in await Device.parse_all(self):
            any_device = True
            status_error = device.status.format_error()
            if status_error is not None:
                cnsl.warn(f'Appareil ignoré {device.label}: {status_error}')
                continue
            yield self.with_device(device)
        if not any_device:
            cnsl.warn('Aucun appreil trouvé')

    async def with_first_device(self):
        adb_ctx_list = [d async for d in self.all_devices()]
        assert len(adb_ctx_list) > 0
        adb_ctx = adb_ctx_list[0]
        if len(adb_ctx_list) > 1:
            cnsl.warn(
                f'Plusieurs appareils detectés: uniquement {adb_ctx.device.label} sera utilisé'
            )
        return adb_ctx

    def with_device(self, device: Device):
        return Adb(self, device)

    def _exec(self, *args: object):
        return _exec(self.adb_exe, *args)

    def devices(self, *args: str):
        return self._exec('devices', *args)

    def start_server(self):
        return self._exec('start-server')

    def kill_server(self):
        return self._exec('kill-server')


@dataclasses.dataclass
class Adb:
    _undeviced: UndevicedAdb
    device: Device

    def _exec_gen(self, *args: object):
        return _exec_gen(self._undeviced.adb_exe, '-s', self.device.serial, *args)

    def _exec(self, *args: object):
        return _exec(self._undeviced.adb_exe, '-s', self.device.serial, *args)

    ##

    def logcat(self, *args: str):
        return self._exec('logcat', *args)

    def logcat_gen(self, *args: str):
        return self._exec_gen('logcat', *args)

    ##

    def install(self, local_apk_path: pathlib.Path):
        return self._exec('install', local_apk_path)

    def uninstall(self, package_name: str):
        return self._exec('uninstall', package_name)

    ##

    def shell_gen(self, cmd: str):
        return self._exec_gen('shell', cmd)

    def shell(self, cmd: str):
        return self._exec('shell', cmd)

    ##

    async def settings_get(self, key: str, namespace: SettingsNamespace):
        lines = await self.shell(f'settings get {namespace} {key}')
        return lines[0]

    async def settings_set(self, key: str, value: str, namespace: SettingsNamespace):
        await self.shell(f'settings put {namespace} {key} {value}')

    @contextlib.asynccontextmanager
    async def settings_set_tmp(self, key: str, value: str, namespace: SettingsNamespace):
        old_value = await self.settings_get(key, namespace)
        try:
            await self.settings_set(key, value, namespace)
            yield
        finally:
            await self.settings_set(key, old_value, namespace)

    ##

    async def push(self, local_path: pathlib.Path, remote_dir: pathlib.Path):
        return await self._exec('push', local_path, remote_dir)

    async def pull(self, remote_path: pathlib.Path, local_dir: pathlib.Path):
        local_dir.mkdir(parents=True, exist_ok=True)
        return await self._exec('pull', remote_path, local_dir)

    ##

    @contextlib.asynccontextmanager
    async def reverse(self, port: int):
        output = await self._exec('reverse', f'tcp:{0}', f'tcp:{port}')
        remote_port = int(output[0])
        try:
            yield remote_port
        finally:
            output = await self._exec('reverse', '--remove', f'tcp:{remote_port}')
