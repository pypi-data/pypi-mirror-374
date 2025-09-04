import datetime
import pathlib

import fastapi
import pydantic

from unico_device_setuper.backend import state, token
from unico_device_setuper.lib import serde, util

ROUTER = fastapi.APIRouter(prefix='/sygic_maps', tags=['Sygic Maps'])
OBJECT_PATH = pathlib.Path('SygicLib.tar')


##


class SygicMapsBeginUploadResponse(pydantic.BaseModel):
    upload_id: str


@ROUTER.post('/begin_upload', response_model=SygicMapsBeginUploadResponse)
async def begin_upload_endpoint(state: state.State, _: token.Token):
    upload_id = await state.oci.create_multipart_upload(OBJECT_PATH)
    return SygicMapsBeginUploadResponse(upload_id=upload_id)


##


class SygicMapsUploadPartPayload(pydantic.BaseModel):
    content: serde.BytesBase64
    num: int
    upload_id: str


class SygicMapsUploadPartResponse(pydantic.BaseModel):
    upload_ref: str


@ROUTER.put('/upload_part', response_model=SygicMapsUploadPartResponse)
async def upload_part_endpoint(
    payload: SygicMapsUploadPartPayload, state: state.State, _: token.Token
):
    upload_ref = await state.oci.upload_part(
        num=payload.num,
        content=payload.content,
        object_path=OBJECT_PATH,
        upload_id=payload.upload_id,
    )
    return SygicMapsUploadPartResponse(upload_ref=upload_ref)


##


class SygicMapsCommitPayload(pydantic.BaseModel):
    upload_id: str
    upload_refs: list[str]


@ROUTER.post('/commit_upload', response_model=None)
async def commit_upload_endpoint(
    payload: SygicMapsCommitPayload, state: state.State, _: token.Token
):
    await state.oci.commit_upload(
        object_path=OBJECT_PATH, upload_id=payload.upload_id, upload_refs=payload.upload_refs
    )


##


class SygicMapsAbortPayload(pydantic.BaseModel):
    upload_id: str


@ROUTER.delete('/abort_upload', response_model=None)
async def abort_upload_endpoint(payload: SygicMapsAbortPayload, state: state.State, _: token.Token):
    await state.oci.abbort_upload(object_path=OBJECT_PATH, upload_id=payload.upload_id)


##


class SygicMapsPreAuthenticateResponse(pydantic.BaseModel):
    url: str


@ROUTER.get('/pre_authenticate', response_model=SygicMapsPreAuthenticateResponse)
async def get_pre_authenticate_endpoint(state: state.State, token: token.Token):
    url = await state.oci.pre_authenticate(
        name=f'Download request'
        f' for {OBJECT_PATH}'
        f' by {token.username}'
        f' at {util.dump_iso_datetime(util.now())}',
        object_path=OBJECT_PATH,
        duration=datetime.timedelta(hours=1),
    )
    return SygicMapsPreAuthenticateResponse(url=url)


##


class SygicMapsGetVersionResponse(pydantic.BaseModel):
    created_at: serde.DatetimeIso | None


@ROUTER.get('/get_version', response_model=SygicMapsGetVersionResponse)
async def get_version_endpoint(state: state.State, _: token.Token):
    object_list = await state.oci.list_(OBJECT_PATH)
    created_at = None if len(object_list) == 0 else object_list[0].created_at
    return SygicMapsGetVersionResponse(created_at=created_at)
