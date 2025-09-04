import abc
import contextlib
import dataclasses
import datetime
import inspect
import pathlib

import pydantic

from unico_device_setuper.lib import oci


@dataclasses.dataclass(frozen=True)
class OciObject(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def get_extension() -> str: ...

    @classmethod
    def get_name(cls):
        return pathlib.Path(inspect.getfile(cls)).stem

    @classmethod
    def get_prefix(cls):
        return pathlib.Path(cls.get_name())

    @classmethod
    def get_file_name(cls):
        return f'{cls.get_name()}{cls.get_extension()}'

    def get_path(self):
        path = self.get_prefix()
        for f in dataclasses.fields(self.__class__):
            assert isinstance(f.type, type)
            assert issubclass(f.type, str)
            value = getattr(self, f.name)
            assert isinstance(value, str)
            path = path / f.name / value
        return path / self.get_file_name()

    @classmethod
    def try_from_path(cls, p: pathlib.Path):
        expected_prefix = cls.get_prefix()
        with contextlib.suppress(ValueError, TypeError):
            *parts, file_name = p.parts
            prefix_parts = parts[: len(expected_prefix.parts)]
            args_parts = parts[len(expected_prefix.parts) :]
            if prefix_parts == list(expected_prefix.parts) and file_name == cls.get_file_name():
                args = {
                    args_parts[2 * i]: args_parts[2 * i + 1] for i in range(len(args_parts) // 2)
                }
                return cls(**args)
        return None

    async def delete(self, oci_ctx: oci.Context):
        await oci_ctx.delete(self.get_path())


class FileOciObject(OciObject):
    async def create(self, file_path: pathlib.Path, oci_ctx: oci.Context):
        await oci_ctx.upload_file(object_path=self.get_path(), file_path=file_path)

    async def get(self, file_path: pathlib.Path, oci_ctx: oci.Context):
        await oci_ctx.get_file(object_path=self.get_path(), file_path=file_path)


class TextOciObject(OciObject):
    async def create(self, text: str, oci_ctx: oci.Context):
        await oci_ctx.upload_object(object_path=self.get_path(), data=text.encode())

    async def get(self, oci_ctx: oci.Context):
        content = await oci_ctx.get_object(path=self.get_path())
        if content is None:
            return None
        return content.decode()


class ModelOciObject[M: pydantic.BaseModel](OciObject):
    @staticmethod
    @abc.abstractmethod
    def get_model_cls() -> type[M]: ...

    @staticmethod
    def get_extension():
        return '.json'

    async def create(self, model: M, oci_ctx: oci.Context):
        await oci_ctx.upload_object(self.get_path(), model.model_dump_json().encode('utf-8'))
        return self

    async def get(self, oci_ctx: oci.Context):
        content = await oci_ctx.get_object(self.get_path())
        with contextlib.suppress(pydantic.ValidationError):
            return self.get_model_cls().model_validate_json((content or b'').decode('utf-8'))
        return None

    async def get_pre_auth(self, oci_ctx: oci.Context, duration: datetime.timedelta):
        return await oci_ctx.pre_authenticate(
            f'Read access to {self.get_path()}', duration, self.get_path()
        )
