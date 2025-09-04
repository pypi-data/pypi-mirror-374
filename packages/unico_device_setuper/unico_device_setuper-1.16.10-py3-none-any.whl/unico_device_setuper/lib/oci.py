import contextlib
import dataclasses
import datetime
import functools
import pathlib
import typing

import oci_client

from unico_device_setuper.lib import cfg, util

FILE_URL_PREFIX = 'file://'


@dataclasses.dataclass
class CreatedObject:
    path: pathlib.Path
    created_at: datetime.datetime


class ResponseLike(typing.Protocol):
    @property
    def status_code(self) -> int: ...

    @functools.cached_property
    def text(self) -> str: ...


def _check_response(action: str, response: ResponseLike, accepted_status: set[int] | None = None):
    if accepted_status is None:
        accepted_status = {200}

    if response.status_code not in accepted_status:
        raise RuntimeError(f'{response.status_code} Could not {action}: {response.text}')


async def _get_namespace(client: oci_client.Client):
    namespace_response = await client.objectstorage_get('/n')
    _check_response('get namespace', namespace_response)
    assert isinstance(namespace_response.json, str)
    return namespace_response.json


async def _create_bucket(client: oci_client.Client, name: str, namespace: str):
    list_response = await client.objectstorage_get(
        f'/n/{namespace}/b/?compartmentId={client.tenant_id}'
    )
    _check_response('list existing buckets', list_response)

    assert isinstance(list_response.json, list)
    for bucket in list_response.json:
        assert isinstance(bucket, dict)
        if bucket['name'] == name:
            return

    # do not check create response
    # if it fails putting objects in it will fail too
    # this allows to not crash on race conditions

    await client.objectstorage_post(
        f'/n/{namespace}/b/', {'compartmentId': client.tenant_id, 'name': name}
    )


def file_part_generator(file: pathlib.Path, part_size_bytes: int):
    with file.open('rb') as f:
        while len(content := f.read(part_size_bytes)) > 0:
            yield content


@dataclasses.dataclass
class Context:
    bucket_name: str
    namespace: str
    client: oci_client.Client
    upload_part_size: int
    config: cfg.Oci

    @contextlib.asynccontextmanager
    @staticmethod
    async def make(config: cfg.Oci):
        async with oci_client.Client.from_config(config.client) as client:
            namespace = await _get_namespace(client)
            await _create_bucket(client, config.bucket_name, namespace)

            yield Context(
                bucket_name=config.bucket_name,
                namespace=namespace,
                client=client,
                upload_part_size=config.upload_part_size,
                config=config,
            )

    async def delete(self, object_path: pathlib.Path):
        delete_response = await self.client.objectstorage_delete(
            f'/n/{self.namespace}/b/{self.bucket_name}/o/{object_path}'
        )
        _check_response('delete object', delete_response, accepted_status={204, 404})

    async def create_multipart_upload(self, object_path: pathlib.Path):
        upload_create_response = await self.client.objectstorage_post(
            f'/n/{self.namespace}/b/{self.bucket_name}/u', {'object': str(object_path)}
        )
        _check_response('create new upload', upload_create_response)
        assert isinstance(upload_create_response.json, dict)
        upload_id = upload_create_response.json['uploadId']
        assert isinstance(upload_id, str)
        return upload_id

    async def upload_part(
        self, num: int, content: bytes, object_path: pathlib.Path, upload_id: str
    ):
        upload_part_response = await self.client.objectstorage_put(
            f'/n/{self.namespace}/b/{self.bucket_name}/u/{object_path}'
            f'?uploadId={upload_id}&uploadPartNum={num + 1}',
            content,
        )
        _check_response('upload part', upload_part_response)
        return upload_part_response.headers['Etag']

    async def commit_upload(
        self, object_path: pathlib.Path, upload_id: str, upload_refs: list[str]
    ):
        commit_upload_response = await self.client.objectstorage_post(
            f'/n/{self.namespace}/b/{self.bucket_name}/u/{object_path}?uploadId={upload_id}',
            {
                'partsToCommit': [
                    {'etag': ref, 'partNum': num + 1} for num, ref in enumerate(upload_refs)
                ]
            },
        )
        _check_response('commit uplaod', commit_upload_response)

    async def abbort_upload(self, object_path: pathlib.Path, upload_id: str):
        abbort_upload_response = await self.client.objectstorage_delete(
            f'/n/{self.namespace}/b/{self.bucket_name}/u/{object_path}?uploadId={upload_id}'
        )
        _check_response('abort upload', abbort_upload_response, {204})

    async def upload_file(self, object_path: pathlib.Path, file_path: pathlib.Path):
        upload_id = await self.create_multipart_upload(object_path)
        try:
            refs = [
                await self.upload_part(num, content, object_path, upload_id)
                for num, content in enumerate(
                    util.file_part_generator(file_path, self.upload_part_size)
                )
            ]
            await self.commit_upload(object_path, upload_id, refs)
        except:
            await self.abbort_upload(object_path, upload_id)
            raise

    async def upload_object(self, object_path: pathlib.Path, data: bytes):
        url = f'/n/{self.namespace}/b/{self.bucket_name}/o/{object_path}'
        upload_create_response = await self.client.objectstorage_put(url, data)
        _check_response('create new object', upload_create_response)

    async def list_(self, prefix: pathlib.Path):
        list_object_response = await self.client.objectstorage_get(
            f'/n/{self.namespace}/b/{self.bucket_name}/o?prefix={prefix}&fields=name,timeCreated,timeModified'
        )
        _check_response('list objects', list_object_response)

        assert isinstance(list_object_response.json, dict)
        objects = list_object_response.json['objects']
        assert isinstance(objects, list)
        created_objects = list[CreatedObject]()

        for object in objects:
            assert isinstance(object, dict)
            name = object['name']
            assert isinstance(name, str)
            creation_datetime = object['timeCreated']
            assert isinstance(creation_datetime, str)
            modification_datetime = object.get('timeModified')
            assert modification_datetime is None or isinstance(modification_datetime, str)
            created_objects.append(
                CreatedObject(
                    pathlib.Path(name),
                    datetime.datetime.fromisoformat(modification_datetime or creation_datetime),
                )
            )
        return created_objects

    async def get_file(self, object_path: pathlib.Path, file_path: pathlib.Path):
        with file_path.open('wb') as file:
            get_object_response = await self.client.objectstorage_get(
                f'/n/{self.namespace}/b/{self.bucket_name}/o/{object_path}', file
            )

        if get_object_response.status_code != 200:
            get_object_response.content = file_path.read_bytes()
            file_path.unlink(missing_ok=True)
            _check_response('get file', get_object_response)

    async def get_object(self, path: pathlib.Path):
        get_object_response = await self.client.objectstorage_get(
            f'/n/{self.namespace}/b/{self.bucket_name}/o/{path}'
        )
        _check_response('get object', get_object_response, accepted_status={200, 404})
        if get_object_response.status_code == 404:
            return None
        return get_object_response.content

    async def exists(self, path: pathlib.Path):
        response = await self.client.objectstorage_head(
            f'/n/{self.namespace}/b/{self.bucket_name}/o/{path}'
        )
        _check_response('checking object', response, {200, 404})
        return response.status_code == 200

    async def pre_authenticate(
        self, name: str, duration: datetime.timedelta, object_path: pathlib.Path
    ):
        response = await self.client.objectstorage_post(
            f'/n/{self.namespace}/b/{self.bucket_name}/p',
            {
                'accessType': 'ObjectRead',
                'name': name,
                'objectName': str(object_path),
                'timeExpires': (util.now() + duration)
                .astimezone(datetime.UTC)
                .strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            },
        )
        _check_response('create pre-authenticated request', response)
        assert isinstance(response.json, dict)
        url = response.json['fullPath']
        assert isinstance(url, str)
        return url
