import json
import os
import pathlib
import shutil

import httpx
import slugify

import unico_device_setuper.lib
from unico_device_setuper.lib import util


def iter_endpoints(impl_path: pathlib.Path):
    for tag_dir in (impl_path / 'api').iterdir():
        if tag_dir.is_dir():
            for endpoint_file in tag_dir.iterdir():
                if endpoint_file.suffix == '.py' and endpoint_file.stem != '__init__':
                    yield endpoint_file


def patch_endpoints(impl_path: pathlib.Path):
    for endpoint_file in iter_endpoints(impl_path):
        endpoint_file.write_text(
            endpoint_file.read_text()
            .replace('asyncio_detailed(', 'detailed_request(')
            .replace('asyncio(', 'request(')
            .replace('*,', '')
        )


def make_init_py(impl_path: pathlib.Path):
    content = ''
    all: list[str] = []

    tag_dir_endpoint_paths_map = util.groupby(iter_endpoints(impl_path), key=lambda e: e.parent)
    for tag_dir, endpoint_paths in tag_dir_endpoint_paths_map.items():
        content += f'from .{impl_path.name}.api.{tag_dir.name} import (\n'
        for endpoint_path in endpoint_paths:
            content += f'    {endpoint_path.stem},\n'
            all.append(endpoint_path.stem)
        content += ')\n'

    import_statements = (impl_path / 'models' / '__init__.py').read_text().split('from .')[1:]
    import_statements[-1] = import_statements[-1].partition('__all__')[0]
    for import_statement in import_statements:
        module_name, _, model_name = import_statement.partition(' import ')
        model_name = model_name.strip()
        if model_name.startswith('('):
            model_name = model_name[1:-1].strip()[:-1]

        content += f'from .{impl_path.name}.models.{module_name} import {model_name}\n'
        all.append(model_name)

    content += f'from .{impl_path.name}.client import Client\n'
    all.append('Client')

    content += '__all__ = [\n'
    for element in all:
        content += f"    '{element}',\n"
    content += ']\n'

    (impl_path.parent / '__init__.py').write_text(content)


async def generate_api(openapi_url: str, lib_name: str):
    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(openapi_url)
        assert response.status_code == 200, (openapi_url, response.status_code, response.text)
        openapi_specs = response.json()

    specs_info = openapi_specs.get('info')
    specs_title = specs_info.get('title') if specs_info is not None else None

    if specs_title is None:
        raise RuntimeError(f'OpenAPI specs does not have a title, infos: {specs_info}')

    generated_module = slugify.slugify(specs_title + '_client', separator='_')

    with util.temporary_dir(util.module_path(unico_device_setuper).parent) as tmp_dir:
        (tmp_dir / 'openapi.json').write_text(json.dumps(openapi_specs))
        os.chdir(tmp_dir)
        try:
            [
                _
                async for _ in util.exec_proc(
                    pathlib.Path('openapi-python-client'), 'generate', '--url', openapi_url
                )
            ]
        except Exception as e:
            e.add_note(
                'If you believed this is due to `openapi_python_client` not being found, make '
                'sure it is installed using `pipx install openapi_python_client --include-deps`'
            )
            raise

        generated_module_path = tmp_dir / generated_module.replace('_', '-') / generated_module

        lib_path = util.module_path(unico_device_setuper.lib) / lib_name
        impl_path = lib_path / 'impl'
        shutil.rmtree(lib_path, ignore_errors=True)
        lib_path.mkdir(parents=True, exist_ok=True)
        generated_module_path.rename(impl_path)
        patch_endpoints(impl_path)
        make_init_py(impl_path)
