import enum
import typing

from unico_device_setuper.lib import cnsl, datadir, rl


class UnitechEnv(enum.Enum):
    LOCAL = 'local'
    DEV = 'dev'
    PRE_PROD = 'pre-prod'
    PROD = 'prod'

    @property
    def api_base_url(self):
        if self == UnitechEnv.LOCAL:
            return rl.Url('http://localhost:3000')
        return rl.Url(f'https://api.{self.value}.unicofrance.com')

    @property
    def static_base_url(self) -> rl.Url:
        if self == UnitechEnv.LOCAL:
            return UnitechEnv.DEV.static_base_url
        return rl.Url(f'https://static.{self.value}.unicofrance.com')

    @classmethod
    def get_default(cls):
        if datadir.is_release_version():
            return cls.PROD
        return cls.LOCAL

    @staticmethod
    async def choose():
        cnsl.print_blue('Choisir un environement Unitech')
        return await cnsl.print_choose(
            list(UnitechEnv), prompt='Environement: ', formater=lambda e: e.value
        )


class ApiEnv(enum.Enum):
    LOCAL = 'local'
    DEPLOYED = 'deployed'

    @property
    def api_base_url(self):
        if self == ApiEnv.LOCAL:
            return rl.Url('http://localhost:12000')
        return rl.Url('https://device-setuper.prod.unicofrance.com')

    @property
    def unitech_auth_env(self):
        if self == ApiEnv.LOCAL:
            return UnitechEnv.LOCAL
        return UnitechEnv.PROD

    @classmethod
    def get_default(cls):
        if datadir.is_release_version():
            return cls.DEPLOYED
        return cls.LOCAL


class SygicEnv(enum.Enum):
    PRIMARY = 'primary'
    SECONDARY = 'secondary'

    @property
    def api_base_url(self):
        return rl.Url('https://api.bls.sygic.com/api/v1')

    @classmethod
    def get_default(cls):
        if datadir.is_release_version():
            return cls.PRIMARY
        return cls.SECONDARY


Env: typing.TypeAlias = SygicEnv | UnitechEnv
