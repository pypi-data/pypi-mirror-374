import contextlib
import dataclasses

import httpx

from unico_device_setuper.lib import (
    aapt,
    adb,
    api,
    auth,
    cnsl,
    datadir,
    env,
    sygic,
    uninav,
    unitech,
)


@dataclasses.dataclass
class Args:
    unitech_client_strategy: auth.ClientStrategy
    sygic_products_names: list[str] | None
    uninav_version: uninav.VersionName | None
    device_owner: str | None
    api_env: env.ApiEnv
    unitech_env: env.UnitechEnv | None
    sygic_env: env.SygicEnv
    skip_uninstall_packages: bool | None
    skip_install_maps: bool | None


async def make_sygic_client(sygic_env: env.SygicEnv, http_client: httpx.AsyncClient):
    return sygic.Client(
        base_url=sygic_env.api_base_url,
        http_client=http_client,
        api_key=await auth.get_sygic_api_key(sygic_env, http_client),
    )


def get_default_device_owner():
    if datadir.is_release_version():
        return 'uni'
    return 'tmp'


@dataclasses.dataclass
class UndevicedSetup:
    args: Args
    api_client: api.Client
    http_client: httpx.AsyncClient
    undeviced_adb: adb.UndevicedAdb
    _unitech_client: unitech.Client
    _sygic_client: sygic.Client | None
    _uninav_version: uninav.VersionName | None
    _device_owner: str | None
    _sygic_license_products: list[sygic.LicenseProduct] | None
    _skip_uninstall_packages: bool | None
    _skip_install_maps: bool | None
    unitech_env: env.UnitechEnv

    @contextlib.asynccontextmanager
    @staticmethod
    async def make(args: Args):
        unitech_env = args.unitech_env
        if unitech_env is None:
            unitech_env = await env.UnitechEnv.choose()

        cnsl.print_gray(f'Environement Unitech: {unitech_env.value}')
        cnsl.print_gray(f'Environement Sygic: {args.sygic_env.value}')
        api_auth_token = await auth.get_unitech_auth_token(
            args.api_env.unitech_auth_env, client_strategy=auth.PICK_ANY
        )
        assert api_auth_token is not None  # should not fail with PICK_ANY, otherwise cannot do much

        async with (
            unitech.Client(base_url=str(unitech_env.api_base_url)) as unitech_client,
            api.Client(
                base_url=str(args.api_env.api_base_url),
                headers={'Authorization': f'Bearer {api_auth_token}'},
            ) as api_client,
            httpx.AsyncClient() as http_client,
            adb.UndevicedAdb.make(http_client) as undeviced_adb,
        ):
            yield UndevicedSetup(
                args=args,
                api_client=api_client,
                http_client=http_client,
                undeviced_adb=undeviced_adb,
                unitech_env=unitech_env,
                _unitech_client=unitech_client,
                _sygic_client=None,
                _sygic_license_products=None,
                _uninav_version=args.uninav_version,
                _device_owner=args.device_owner,
                _skip_uninstall_packages=args.skip_uninstall_packages,
                _skip_install_maps=args.skip_install_maps,
            )

    @contextlib.asynccontextmanager
    async def with_device(self, device: adb.Device):
        adb_ = self.undeviced_adb.with_device(device)
        async with aapt.Aapt.make(adb_, self.http_client) as aapt_:
            yield Setup(self, adb_, aapt_, uninav.Uninav(adb_, aapt_))

    async def get_unitech_client(self):
        headers = self._unitech_client.get_async_httpx_client().headers
        auth_header_name = 'Authorization'
        if headers.get(auth_header_name) is None:
            auth_token = await auth.get_unitech_auth_token(
                self.unitech_env, self.args.unitech_client_strategy
            )
            if auth_token is None:
                return None
            headers[auth_header_name] = f'Bearer {auth_token}'
        return self._unitech_client

    async def get_sygic_client(self):
        if self._sygic_client is None:
            self._sygic_client = await make_sygic_client(self.args.sygic_env, self.http_client)
        return self._sygic_client

    async def get_uninav_version(self):
        if self._uninav_version is None:
            unitech_client = await self.get_unitech_client()
            if unitech_client is None:
                return None
            self._uninav_version = await uninav.VersionName.choose(
                unitech_env=self.unitech_env,
                unitech_client=unitech_client,
                http_client=self.http_client,
            )
        return self._uninav_version

    async def get_device_owner(self):
        if self._device_owner is None:
            default = get_default_device_owner()
            self._device_owner = (
                await cnsl.input(f"Propriétaire de l'appareil (par défaut: {default}): ")
            ) or default
        return self._device_owner

    async def get_sygic_license_products(self):
        if self._sygic_license_products is None:
            sygic_client = await self.get_sygic_client()
            self._sygic_license_products = await sygic.choose_license_products(
                self.args.sygic_products_names, sygic_client, self.unitech_env
            )
        return self._sygic_license_products

    async def get_skip_uninstall_packages(self):
        if self._skip_uninstall_packages is None:
            self._skip_uninstall_packages = await cnsl.confirm(
                'Désinstaller les applications par défaut ?'
            )
        return self._skip_uninstall_packages

    async def get_skip_install_maps(self):
        if self._skip_install_maps is None:
            self._skip_install_maps = await cnsl.confirm('Installer les cartes Sygic ?')
        return self._skip_install_maps


@dataclasses.dataclass
class Setup:
    _undeviced_setup: UndevicedSetup
    adb: adb.Adb
    aapt: aapt.Aapt
    uninav: uninav.Uninav

    def get_unitech_client(self):
        return self._undeviced_setup.get_unitech_client()

    def get_sygic_client(self):
        return self._undeviced_setup.get_sygic_client()

    def get_uninav_version(self):
        return self._undeviced_setup.get_uninav_version()

    def get_device_owner(self):
        return self._undeviced_setup.get_device_owner()

    def get_sygic_license_products(self):
        return self._undeviced_setup.get_sygic_license_products()

    def get_skip_uninstall_packages(self):
        return self._undeviced_setup.get_skip_uninstall_packages()

    def get_skip_install_maps(self):
        return self._undeviced_setup.get_skip_install_maps()

    @property
    def args(self):
        return self._undeviced_setup.args

    @property
    def api_client(self):
        return self._undeviced_setup.api_client

    @property
    def http_client(self):
        return self._undeviced_setup.http_client

    @property
    def unitech_env(self):
        return self._undeviced_setup.unitech_env
