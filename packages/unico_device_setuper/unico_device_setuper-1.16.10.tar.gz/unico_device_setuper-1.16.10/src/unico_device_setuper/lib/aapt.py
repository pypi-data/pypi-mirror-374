import contextlib
import dataclasses
import pathlib

import httpx

from unico_device_setuper.lib import adb, datadir, dl, rl, util

APDE_DOWNLOAD_URL = rl.Url('https://github.com/Calsign/APDE/archive/refs/tags/v0.5.1-alpha.zip')


@dataclasses.dataclass
class Aapt:
    adb_ctx: adb.Adb
    aapt_remote_path: pathlib.Path

    def dump_badging(self, remote_apk_path: pathlib.Path):
        return self.adb_ctx.shell_gen(f'{self.aapt_remote_path} dump badging {remote_apk_path}')

    @contextlib.asynccontextmanager
    @staticmethod
    async def make(adb_ctx: adb.Adb, http_client: httpx.AsyncClient):
        aapt_path = datadir.get() / 'aapt'
        if not util.is_executable(aapt_path):
            await dl.download_and_extract_zipped_executable(
                APDE_DOWNLOAD_URL,
                pathlib.Path('APDE') / 'src' / 'main' / 'assets' / 'aapt-binaries' / 'aapt-arm-pie',
                aapt_path,
                http_client,
            )

        aapt_remote_path = pathlib.Path('/') / 'data' / 'local' / 'tmp' / 'aapt'
        try:
            await adb_ctx.push(aapt_path, aapt_remote_path)
            yield Aapt(adb_ctx, aapt_remote_path)
        finally:
            await adb_ctx.shell(f"rm '{aapt_remote_path}'")
