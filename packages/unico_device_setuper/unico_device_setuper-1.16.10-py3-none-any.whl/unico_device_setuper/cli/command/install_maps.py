import datetime
import io
import shutil

import slugify

from unico_device_setuper.cli import stp
from unico_device_setuper.lib import api, cnsl, datadir, dl, rl, socket


async def download_sygic_maps(setup: stp.Setup):
    get_version_response = await api.sygic_maps_get_version.request(setup.api_client)

    assert isinstance(get_version_response, api.SygicMapsGetVersionResponse), (
        'Failed to get sygic maps version',
        get_version_response,
    )

    if get_version_response.created_at is None:
        cnsl.warn('Pas de cartes Sygic publiées')
        return None

    sygic_maps_dir = datadir.get() / 'sygic_maps'
    sygic_maps_path = sygic_maps_dir / f'{ slugify.slugify(get_version_response.created_at)}.tar'

    if sygic_maps_path.exists():
        return sygic_maps_path

    pre_auth_response = await api.sygic_maps_pre_authenticate.request(setup.api_client)
    assert isinstance(pre_auth_response, api.SygicMapsPreAuthenticateResponse), (
        'Failed to preauthenticate',
        pre_auth_response,
    )

    shutil.rmtree(sygic_maps_dir, ignore_errors=True)
    sygic_maps_path.parent.mkdir(parents=True, exist_ok=True)

    await dl.download_url(
        rl.Url(pre_auth_response.url), sygic_maps_path, setup.http_client, label='sygic_maps'
    )

    return sygic_maps_path


@cnsl.command('Installation des cartes Sygic', 'Cartes Sygic installées')
async def install_maps(setup: stp.Setup):
    if await setup.get_skip_install_maps():
        cnsl.warn('Installation des cartes Sygic ignorée')
        return False

    archive_path = await download_sygic_maps(setup)
    if archive_path is None:
        return False

    with archive_path.open('rb') as input:
        return await socket.send_receive(
            lambda port: setup.uninav.start_sygic_files_io_activity(
                'import', port=port, packet_size=socket.PACKET_SIZE
            ),
            input_size=archive_path.stat().st_size,
            timeout=datetime.timedelta(seconds=300),
            input=input,
            ouput_size_wait_label="Désarchivage des cartes sur l'appareil",
            output=io.BytesIO(b''),
        )
