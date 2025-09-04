import base64
import datetime
import io
import pathlib
import tarfile

import tqdm

from unico_device_setuper.cli import stp
from unico_device_setuper.lib import api, cnsl, datadir, socket, util


def clean_sygic_files(archive_path: pathlib.Path):
    with cnsl.step('Nettoyage des cartes'), datadir.get_temporary() as tmp_dir:
        with tarfile.open(archive_path, 'r') as tar:
            tar.extractall(path=tmp_dir, filter='data')

        sygiclib_path = tmp_dir / 'SygicLib'
        if not sygiclib_path.exists():
            cnsl.print_red('Cannot find SygicLib')
            return None

        util.safe_unlink(sygiclib_path / 'Maps' / 'content.lic')
        util.safe_unlink(sygiclib_path / 'Maps' / 'footprint.info')

        for path in (sygiclib_path / 'Android').iterdir():
            if path.suffix == '.dat':
                util.safe_unlink(path)

        cleaned_archive_path = archive_path.with_name(f'{archive_path.stem}_cleaned.tar')

        with tarfile.open(cleaned_archive_path, 'w') as tar:
            tar.add(sygiclib_path, arcname='SygicLib')

        return cleaned_archive_path


async def upload_maps(archive_path: pathlib.Path, api_client: api.Client):
    with (
        tqdm.tqdm(
            desc='Téléversement vers le serveur',
            total=archive_path.stat().st_size,
            unit_scale=True,
            unit='o',
        ) as progress,
        archive_path.open(mode='rb') as f,
    ):
        begin_upload_response = await api.sygic_maps_begin_upload.request(api_client)
        assert isinstance(begin_upload_response, api.SygicMapsBeginUploadResponse), (
            'Failed to start uploading maps',
            begin_upload_response,
        )
        upload_id = begin_upload_response.upload_id
        try:
            refs = list[str]()
            while part := f.read(2**25):
                part_upload_response = await api.sygic_maps_upload_part.request(
                    api_client,
                    api.SygicMapsUploadPartPayload(
                        base64.b64encode(part).decode(), num=len(refs), upload_id=upload_id
                    ),
                )
                assert isinstance(part_upload_response, api.SygicMapsUploadPartResponse), (
                    'Failed to upload part',
                    part_upload_response,
                )
                progress.update(len(part))
                refs.append(part_upload_response.upload_ref)

            commit_response = await api.sygic_maps_commit_upload.request(
                api_client, api.SygicMapsCommitPayload(upload_id, refs)
            )
            assert commit_response is None, ('Failed to commit upload', commit_response)
        except:
            await api.sygic_maps_abort_upload.request(
                api_client, api.SygicMapsAbortPayload(upload_id)
            )
            raise


@cnsl.command('Publications des cartes Sygic', 'Cartes Sygic publiées')
async def publish_maps(setup: stp.Setup):
    with datadir.get_temporary() as tmp_dir:
        archive_path = tmp_dir / 'SygicLib.tar'

        with archive_path.open('wb') as output:
            success = await socket.send_receive(
                lambda port: setup.uninav.start_sygic_files_io_activity(
                    'export', port=port, packet_size=socket.PACKET_SIZE
                ),
                timeout=datetime.timedelta(seconds=300),
                input_size=0,
                input=io.BytesIO(b''),
                ouput_size_wait_label="Archivage des cartes sur l'appareil",
                output=output,
            )
            if not success:
                return False

        cleaned_archive_path = clean_sygic_files(archive_path)
        if cleaned_archive_path is not None:
            await upload_maps(cleaned_archive_path, setup.api_client)

    return True
