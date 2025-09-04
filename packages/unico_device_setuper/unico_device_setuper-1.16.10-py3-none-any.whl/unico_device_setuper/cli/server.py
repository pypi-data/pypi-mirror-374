import asyncio
import time

from unico_device_setuper.cli import stp
from unico_device_setuper.cli.command import (
    install_maps,
    install_uninav,
    register_sygic,
    register_unitech,
    uninstall_packages,
)
from unico_device_setuper.lib import adb, cnsl, util

VALID_STATUS_LABEL = 'Ok'


async def setup_device_handler(setup: stp.Setup):
    await uninstall_packages.uninstall_packages(setup)
    await install_uninav.install_uninav(setup)
    await register_unitech.register_unitech(setup)
    await register_sygic.register_sygic(setup)
    await install_maps.install_maps(setup)
    cnsl.print()


async def enter_setup_device(
    device: adb.Device, done_serials: set[str], undeviced_setup: stp.UndevicedSetup
):
    if device.serial in done_serials:
        cnsl.device_display(device.serial, 'Déjà paramètré', 'info')
        return

    async with undeviced_setup.with_device(device) as setup:
        cnsl.device_display(device.serial, 'Début du paramètrage', 'info')
        t0 = time.perf_counter()
        await setup_device_handler(setup)
        cnsl.device_display(
            device.serial,
            'Fin du paramètrage',
            style='info',
            note=f'[{util.format_timdelta_s(time.perf_counter() - t0)}]',
        )
    done_serials.add(device.serial)


def handle_device_update(before: adb.Device | None, current: adb.Device | None):
    if before is not None:
        if current is not None:
            if before.status != current.status:
                before_error = before.status.format_error() or VALID_STATUS_LABEL
                current_error = current.status.format_error()
                cnsl.device_display(
                    current.serial,
                    f'{before_error} -> {current_error or VALID_STATUS_LABEL}',
                    'info' if current_error is None else 'error',
                )

        else:
            cnsl.device_display(before.serial, 'Déconnecté', style='error')
    elif current is not None:
        error = current.status.format_error()
        cnsl.device_display(
            current.serial,
            'Connecté' + (f' ({error})' if error is not None else ''),
            style='info' if error is None else 'error',
            note=f'({VALID_STATUS_LABEL})' if error is None else None,
        )


async def watch_and_setup_devices(args: stp.Args):
    handled_devices: dict[str, adb.Device | None] = {}
    done_serials: set[str] = set()

    async with stp.UndevicedSetup.make(args) as setup:
        cnsl.print_cyan("\n=== À l'écoute de nouveaux appareils ===")

        while True:
            devices = {d.serial: d for d in await adb.Device.parse_all(setup.undeviced_adb)}
            for serial in devices | handled_devices:
                device = devices.get(serial)
                handled_device = handled_devices.get(serial)
                if handled_device != device:
                    handle_device_update(handled_device, device)

                    if device is not None and device.status.format_error() is None:
                        await enter_setup_device(device, done_serials, setup)

                handled_devices[serial] = device

            try:
                await asyncio.sleep(0.2)
            except asyncio.exceptions.CancelledError:
                cnsl.print_pink('\n\nBye :)')
                return
