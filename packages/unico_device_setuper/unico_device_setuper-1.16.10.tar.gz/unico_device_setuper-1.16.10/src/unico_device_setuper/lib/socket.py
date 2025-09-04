import asyncio
import contextlib
import dataclasses
import datetime
import typing

import tqdm

from unico_device_setuper.lib import cnsl, util

OnConnection: typing.TypeAlias = typing.Callable[
    [asyncio.StreamReader, asyncio.StreamWriter], typing.Awaitable[None]
]


@contextlib.asynccontextmanager
async def _setup_server(connection_handler: OnConnection):
    server = await asyncio.start_server(connection_handler, 'localhost', 0)
    port: int = server.sockets[0].getsockname()[1]
    try:
        yield port
    finally:
        server.close()


@dataclasses.dataclass
class _ReceiveStatus:
    finished_reading: bool


PACKET_SIZE = 2**22


async def send_receive(
    wait_context: typing.Callable[[int], typing.AsyncContextManager[bool | None]],
    timeout: datetime.timedelta,
    input_size: int,
    input: util.SupportsRead[bytes],
    ouput_size_wait_label: str,
    output: util.SupportsWrite[bytes],
):
    status = _ReceiveStatus(finished_reading=False)

    async def on_connection(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        writer.write(input_size.to_bytes(8, 'big', signed=True))
        await writer.drain()
        if input_size > 0:
            with tqdm.tqdm(
                total=input_size, unit='o', unit_scale=True, desc="Téléversement vers l'appareil"
            ) as progress:
                while len(packet := input.read(PACKET_SIZE)) > 0:
                    writer.write(packet)
                    progress.update(len(packet))
                    await writer.drain()

        with cnsl.step(ouput_size_wait_label):
            output_size = int.from_bytes(await reader.readexactly(8), byteorder='big', signed=True)

        if output_size > 0:
            with tqdm.tqdm(
                total=output_size,
                unit='o',
                unit_scale=True,
                desc="Téléchargement depuis l'appareil",
            ) as progress:
                while len(packet := await reader.read(PACKET_SIZE)) > 0:
                    output.write(packet)
                    progress.update(len(packet))

        writer.close()

        status.finished_reading = True

    async with _setup_server(on_connection) as port, wait_context(port) as should_continue:
        if should_continue is False:
            return False

        started_at = util.now()
        while util.now() - started_at < timeout:
            if status.finished_reading:
                return True
            await asyncio.sleep(0.05)

        cnsl.print_red('Impossible de se connecter à Uninav')
        return False
