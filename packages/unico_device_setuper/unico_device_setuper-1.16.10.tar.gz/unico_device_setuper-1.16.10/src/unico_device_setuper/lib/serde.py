import base64
import datetime
import typing

import pydantic

from unico_device_setuper.lib import util


def annotate_str[T](
    type: type[T],
    serializer: typing.Callable[[T], str],
    deserializer: typing.Callable[[str], T | None],
    *,
    format_name: str | None = None,
):
    def validator(v: object):
        if isinstance(v, str):
            deser_v = deserializer(v)
            if deser_v is not None:
                return deser_v
            raise ValueError(f'Value is not a valid {format_name}')
        return v

    if format_name is None:
        format_name = type.__name__

    return (
        pydantic.BeforeValidator(validator),
        pydantic.PlainSerializer(serializer),
        pydantic.WithJsonSchema({'type': 'string', 'format': format_name}),
    )


# Base64


def ser_bytes_base64(data: bytes):
    return base64.b64encode(data).decode('ascii', errors='strict')


def deser_bytes_base64(s: str):
    return base64.b64decode(s.encode('ascii'), validate=True)


BytesBase64 = typing.Annotated[
    bytes, *annotate_str(bytes, ser_bytes_base64, deser_bytes_base64, format_name='base64')
]


# Datetime


type DatetimeIso = typing.Annotated[
    datetime.datetime,
    *annotate_str(
        datetime.datetime,
        util.dump_iso_datetime,
        util.load_iso_datetime,
        format_name='ISO datetime',
    ),
]


class Author(pydantic.BaseModel):
    by: str
    at: DatetimeIso
