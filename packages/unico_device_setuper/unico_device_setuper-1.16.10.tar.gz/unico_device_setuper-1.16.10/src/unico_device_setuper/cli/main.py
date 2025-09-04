import asyncio
import dataclasses
import sys
import typing

import typer

import unico_device_setuper
from unico_device_setuper.cli import command, logout, server, stp
from unico_device_setuper.lib import adb, auth, cnsl, datadir, env, uninav

Handler: typing.TypeAlias = typing.Callable[[stp.Setup], typing.Awaitable[bool]]


COMMANDS: dict[str, Handler] = {
    'ban-package': command.ban_package.ban_package,
    'unban-package': command.unban_package.unban_package,
    'uninstall-packages': command.uninstall_packages.uninstall_packages,
    'install-uninav': command.install_uninav.install_uninav,
    'register-uninav': command.register_unitech.register_unitech,
    'register-sygic': command.register_sygic.register_sygic,
    'install-maps': command.install_maps.install_maps,
    'publish-maps': command.publish_maps.publish_maps,
    'logout-sygic': logout.logout_sygic,
    'logout-unitech': logout.logout_unitech,
}


def get_default_skip_step():
    return None


@dataclasses.dataclass
class GlobalOptions:
    unitech_client_strategy: auth.ClientStrategy = auth.PICK_INTERACTIVE
    sygic_products_names: list[str] | None = None
    uninav_version: uninav.VersionName | None = None
    device_owner: str | None = None
    api_env: env.ApiEnv = dataclasses.field(default_factory=env.ApiEnv.get_default)
    unitech_env: env.UnitechEnv | None = dataclasses.field(
        default_factory=env.UnitechEnv.get_default
    )
    sygic_env: env.SygicEnv = dataclasses.field(default_factory=env.SygicEnv.get_default)
    skip_uninstall_packages: bool | None = dataclasses.field(default_factory=get_default_skip_step)
    skip_install_maps: bool | None = dataclasses.field(default_factory=get_default_skip_step)

    def get_args(self):
        return stp.Args(
            unitech_client_strategy=GLOBAL_OPTIONS.unitech_client_strategy,
            sygic_products_names=GLOBAL_OPTIONS.sygic_products_names,
            uninav_version=GLOBAL_OPTIONS.uninav_version,
            device_owner=GLOBAL_OPTIONS.device_owner,
            api_env=GLOBAL_OPTIONS.api_env,
            unitech_env=GLOBAL_OPTIONS.unitech_env,
            sygic_env=GLOBAL_OPTIONS.sygic_env,
            skip_uninstall_packages=GLOBAL_OPTIONS.skip_uninstall_packages,
            skip_install_maps=GLOBAL_OPTIONS.skip_install_maps,
        )


GLOBAL_OPTIONS = GlobalOptions()


def display_help(ctx: typer.Context):
    typer.echo(ctx.get_help())
    cnsl.print(f' [bold yellow]Version:[/] [bold]{unico_device_setuper.__version__}')
    cnsl.print(f' [bold yellow]Data directory:[/] [bold]{datadir.get()}')
    cnsl.print()


def add_arguments(f: typing.Callable[[typer.Context], None]):
    default_api_env_value = typing.cast('typing.Any', GLOBAL_OPTIONS.api_env.value)
    default_unitech_env_value = (
        typing.cast('typing.Any', GLOBAL_OPTIONS.unitech_env.value)
        if GLOBAL_OPTIONS.unitech_env is not None
        else None
    )
    default_sygic_env_value = typing.cast('typing.Any', GLOBAL_OPTIONS.sygic_env.value)

    def wrapper(
        ctx: typer.Context,
        *,
        api_env: env.ApiEnv = default_api_env_value,
        unitech_env: typing.Optional[env.UnitechEnv] = default_unitech_env_value,
        sygic_env: env.SygicEnv = default_sygic_env_value,
        unitech_client: typing.Optional[str] = None,
        sygic_products_names: typing.Optional[list[str]] = typer.Option(None, '--license'),  # noqa: B008
        no_sygic_product: bool = typer.Option(False, '--no-license'),  # noqa: FBT003
        uninav_version: typing.Optional[str] = None,
        device_owner: typing.Optional[str] = None,
        skip_uninstall_packages: typing.Optional[bool] = GLOBAL_OPTIONS.skip_uninstall_packages,
        skip_install_maps: typing.Optional[bool] = GLOBAL_OPTIONS.skip_install_maps,
        version: bool = typer.Option(False, '--version'),  # noqa: FBT003
        help: bool = typer.Option(False, '--help'),  # noqa: FBT003
    ):
        if help:
            display_help(ctx)
            sys.exit()

        if version:
            cnsl.print(unico_device_setuper.__version__)
            sys.exit()

        if sygic_products_names and no_sygic_product:
            cnsl.print_red('Cannot specify both --license and no --no-license')
            sys.exit()

        if unitech_client is not None:
            GLOBAL_OPTIONS.unitech_client_strategy = auth.PickWithName(unitech_client)

        if sygic_products_names:
            GLOBAL_OPTIONS.sygic_products_names = sygic_products_names

        if no_sygic_product:
            GLOBAL_OPTIONS.sygic_products_names = []

        if uninav_version is not None:
            version_name = uninav.VersionName.parse(uninav_version)
            if version_name is None:
                cnsl.print_red(f'Nom de version invalide: {uninav_version}')
                sys.exit()
            GLOBAL_OPTIONS.uninav_version = version_name

        GLOBAL_OPTIONS.device_owner = device_owner
        GLOBAL_OPTIONS.skip_uninstall_packages = skip_uninstall_packages
        GLOBAL_OPTIONS.skip_install_maps = skip_install_maps
        GLOBAL_OPTIONS.api_env = api_env
        GLOBAL_OPTIONS.unitech_env = unitech_env
        GLOBAL_OPTIONS.sygic_env = sygic_env
        return f(ctx)

    return wrapper


async def executor(handler: Handler):
    async with stp.UndevicedSetup.make(GLOBAL_OPTIONS.get_args()) as undeviced_setup:
        devices = await adb.Device.parse_all(undeviced_setup.undeviced_adb)
        if len(devices) == 0:
            cnsl.warn('Aucun appareil détecté')

        for device in devices:
            async with undeviced_setup.with_device(device) as setup:
                await handler(setup)


def add_commands(app: typer.Typer):
    for command_name, handler in COMMANDS.items():
        app.registered_commands.append(
            typer.models.CommandInfo(
                name=command_name,
                callback=add_arguments(lambda _, handler=handler: asyncio.run(executor(handler))),
            )
        )


APP = typer.Typer(pretty_exceptions_enable=False, add_completion=False)


@APP.callback(invoke_without_command=True)
@add_arguments
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        asyncio.run(server.watch_and_setup_devices(GLOBAL_OPTIONS.get_args()))


add_commands(APP)
