from unico_device_setuper.cli import stp
from unico_device_setuper.lib import auth


async def logout_sygic(setup: stp.Setup):
    auth.clear_credentials(auth.SYGIC_NAME, setup.args.sygic_env)
    return True


async def logout_unitech(setup: stp.Setup):
    auth.clear_credentials(auth.UNITECH_NAME, setup.unitech_env)
    return True
