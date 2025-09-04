import asyncio
import base64
import contextlib
import dataclasses
import datetime
import json
import typing

import slugify

from unico_device_setuper.cli import stp
from unico_device_setuper.lib import cnsl, unitech

SETUPER_ACTIVITY_TIMEOUT = datetime.timedelta(seconds=10)


async def find_device_id_in_logs(logs: typing.AsyncGenerator[str, None]):
    try:
        async for line in logs:
            line_parts = line.split('ID_DEVICE: ')
            if len(line_parts) > 1:
                return line_parts[-1]
        return None
    finally:
        await logs.aclose()


async def get_id_device(setup: stp.Setup):
    await setup.uninav.stop()
    await setup.adb.logcat('-c')
    async with setup.uninav.start_id_device_logger_activity() as is_launched:
        if not is_launched:
            return None
        line_generator = setup.adb.logcat_gen()
        try:
            return await asyncio.wait_for(
                find_device_id_in_logs(line_generator),
                timeout=SETUPER_ACTIVITY_TIMEOUT.total_seconds(),
            )
        except TimeoutError:
            await line_generator.aclose()
            cnsl.print_red("Impossible de trouver l'id device")
            return None
        finally:
            await setup.uninav.stop()


@dataclasses.dataclass
class ParsedDeviceName:
    owner: str
    num: int

    @staticmethod
    def parse(s: str):
        match slugify.slugify(s).split('-'):
            case ['tab', owner, 'sams', num]:
                with contextlib.suppress(ValueError):
                    return ParsedDeviceName(owner, int(num))
            case _:
                pass
        return None

    def __str__(self):
        return f'tab.{self.owner}.sams.{self.num}'


def get_new_device_name(devices: list[unitech.RegisterDeviceResponse], device_owner: str):
    return str(
        ParsedDeviceName(
            device_owner,
            max(
                (
                    name.num
                    for device in devices
                    if (name := ParsedDeviceName.parse(device.name)) is not None
                    and name.owner == device_owner
                ),
                default=0,
            )
            + 1,
        )
    )


async def get_devices(setup: stp.Setup):
    unitech_client = await setup.get_unitech_client()
    if unitech_client is None:
        return None
    devices_response = await unitech.get_device_all_devices.request(unitech_client)
    assert isinstance(devices_response, list), devices_response
    return devices_response


async def get_client_id(setup: stp.Setup):
    unitech_client = await setup.get_unitech_client()
    if unitech_client is None:
        return None

    auth = unitech_client.get_async_httpx_client().headers['authorization']
    decoded_payload = json.loads(base64.b64decode(auth.split('.')[1] + '===='))

    return decoded_payload['id_client']


@cnsl.command("Enregistrement de l'appareil sur Unitech", 'Appareil enregistré sur Unitech')
async def register_unitech(setup: stp.Setup):
    if (device_id := await get_id_device(setup)) is None:
        return False

    cnsl.print(f"Id de l'appareil: {device_id}")
    devices = await get_devices(setup)
    if devices is None:
        return False
    device_with_same_id = next((d for d in devices if d.id_device == device_id), None)
    device_name = None
    device_owner = await setup.get_device_owner()
    if device_with_same_id is not None:
        current_client_id = await get_client_id(setup)
        if device_with_same_id.id_client == current_client_id:
            cnsl.print_gray('Appareil déjà enregistré')
        else:
            cnsl.print_gray('Appareil déjà enregistré sur un autre client')

        if (
            parsed_name := ParsedDeviceName.parse(device_with_same_id.name)
        ) is None or parsed_name.owner != device_owner:
            cnsl.print_gray(
                f"Ancien nom invalide: {device_with_same_id.name}, renomage de l'appareil"
            )
        else:
            device_name = device_with_same_id.name

    if device_name is None:
        device_name = get_new_device_name(devices, device_owner)

    unitech_client = await setup.get_unitech_client()
    if unitech_client is None:
        return False

    register_response = await unitech.post_auth_device_register_device.request(
        unitech_client, unitech.RegisterDevicePayload(device_name, device_id)
    )
    assert isinstance(register_response, unitech.RegisterDeviceResponse), register_response
    cnsl.print(f"Nom de l'appareil: {device_name}")

    return True
