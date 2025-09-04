import pathlib
import shutil
import stat
import zipfile

import httpx
import tqdm

from unico_device_setuper.lib import datadir, rl


async def download_url(
    url: rl.Url,
    file_path: pathlib.Path,
    http_client: httpx.AsyncClient,
    label: str | None = None,
    redirect_count: int | None = None,
) -> None:
    if redirect_count is not None and redirect_count > 20:
        raise RuntimeError('too many redirects')

    async with http_client.stream(method='GET', url=str(url)) as resp:
        if resp.status_code == 302:
            location = resp.headers.get('location')
            if location is None:
                raise RuntimeError(f'Failed to download {url}: redirect without location header')
            return await download_url(
                url=rl.Url(location),
                file_path=file_path,
                http_client=http_client,
                label=label,
                redirect_count=(redirect_count or 0) + 1,
            )

        if resp.status_code != 200:
            content = (await resp.aread()).decode('utf-8')
            raise RuntimeError(f'Failed to download {url}: {content} (code {resp.status_code})')
        content_length = int(resp.headers.get('content-length', 0))
        tmp_file_path = file_path.with_stem(file_path.stem + '_tmp')
        tmp_file_path.parent.mkdir(parents=True, exist_ok=True)

        progress_bar = tqdm.tqdm(
            total=content_length,
            desc=f'Téléchargment de {label}' or file_path.name,
            unit='o',
            unit_scale=True,
        )
        with tmp_file_path.open(mode='wb') as f:
            async for data in resp.aiter_bytes(chunk_size=1024):
                size = f.write(data)
                progress_bar.update(size)
        tmp_file_path.replace(file_path)
        return None


async def download_and_extract_zipped_executable(
    archive_url: rl.Url,
    exe_archive_path: pathlib.Path,
    output_path: pathlib.Path,
    http_client: httpx.AsyncClient,
):
    with datadir.get_temporary() as tmp_dir:
        archive_path = tmp_dir / 'archive.zip'
        await download_url(archive_url, archive_path, http_client, label=output_path.name)

        extracted_dir = tmp_dir / 'extracted'
        with zipfile.ZipFile(archive_path, 'r') as zip:
            zip.extractall(extracted_dir)

        top_levels_files = list(extracted_dir.iterdir())
        if len(top_levels_files) > 1:
            raise RuntimeError(f'Archive contains {len(top_levels_files)} top level files')

        extracted_dir = top_levels_files[0]

        exe_path = extracted_dir / exe_archive_path
        exe_path.chmod(exe_path.stat().st_mode | stat.S_IXUSR)

        shutil.rmtree(output_path, ignore_errors=True)
        exe_path.rename(output_path)
