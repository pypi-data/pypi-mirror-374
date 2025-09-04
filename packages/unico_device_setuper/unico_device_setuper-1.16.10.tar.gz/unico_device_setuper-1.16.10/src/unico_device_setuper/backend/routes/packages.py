import dataclasses

import fastapi
import pydantic

from unico_device_setuper.backend import state, token
from unico_device_setuper.lib import oci_object, serde, util

ROUTER = fastapi.APIRouter(prefix='/packages', tags=['Packages'])

##


class PackageName(pydantic.BaseModel):
    name: str


class Package(PackageName):
    label: str
    disabled: bool


class CreatedPackage(Package):
    created: serde.Author
    updated: serde.Author | None = None


class PackagesModel(pydantic.BaseModel):
    packages: dict[str, CreatedPackage] = pydantic.Field(default_factory=dict)


@dataclasses.dataclass(frozen=True)
class PackagesObject(oci_object.ModelOciObject[PackagesModel]):
    @staticmethod
    def get_model_cls():
        return PackagesModel


def make_author(token: token.Token):
    return serde.Author(by=token.username, at=util.now())


class EmptyResponse(pydantic.BaseModel):
    pass


##


@ROUTER.post('/upsert_many', response_model=EmptyResponse)
async def upsert_endpoint(payload: list[Package], state: state.State, token: token.Token):
    packages = await PackagesObject().get(state.oci) or PackagesModel()
    for package in payload:
        if (exisiting_package := packages.packages.get(package.name)) is not None:
            if exisiting_package.label != package.label:
                exisiting_package.label = package.label
                exisiting_package.updated = make_author(token)

            if exisiting_package.disabled != package.disabled:
                exisiting_package.disabled = package.disabled
                exisiting_package.updated = make_author(token)
        else:
            packages.packages[package.name] = CreatedPackage(
                label=package.label,
                name=package.name,
                disabled=package.disabled,
                created=make_author(token),
            )
    await PackagesObject().create(packages, state.oci)
    return EmptyResponse()


@ROUTER.get('/get_all', response_model=PackagesModel)
async def get_all_endpoint(state: state.State, _: token.Token):
    return await PackagesObject().get(state.oci) or PackagesModel()
