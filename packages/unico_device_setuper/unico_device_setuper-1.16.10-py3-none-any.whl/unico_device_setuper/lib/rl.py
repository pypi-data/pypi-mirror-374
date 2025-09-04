import pathlib
import typing

import httpx
import pydantic


class Url(httpx.URL):
    def __truediv__(self, s: str | pathlib.Path):
        parts = [s] if isinstance(s, str) else s.parts
        result = self
        for part in parts:
            if part != '/':
                result = self.__class__(self, path=f'{result.path}{part}')
        return result


def _url_validator(v: Url | str):
    if isinstance(v, Url):
        return v
    return Url(v)


def _url_serializer(v: Url):
    return str(v)


SerdeUrl = typing.Annotated[
    Url, pydantic.BeforeValidator(_url_validator), pydantic.PlainSerializer(_url_serializer)
]
