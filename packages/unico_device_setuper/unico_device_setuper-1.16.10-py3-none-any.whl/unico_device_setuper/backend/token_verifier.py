import contextlib
import dataclasses
import uuid

import fastapi
import jose
import jose.exceptions
import jose.jwt
import pydantic

from unico_device_setuper.lib import cfg


class TokenPayload(pydantic.BaseModel):
    permissions: int | None = None
    username: str | None = None


@dataclasses.dataclass
class User:
    permission: int
    username: str


@dataclasses.dataclass
class TokenVerifier:
    config: cfg.Security

    @staticmethod
    def _get_token_part(authorization: str | None):
        if authorization is None:
            raise fastapi.HTTPException(401, 'misssing authorization')
        parts = authorization.split()
        if len(parts) != 2:
            raise fastapi.HTTPException(401, "format must be '<scheme> <token>'")
        (scheme, token) = parts
        if scheme.lower() != 'bearer':
            raise fastapi.HTTPException(401, "scheme must be 'bearer'")
        return token

    def _get_verified_payload(self, authorization: str | None):
        token = self._get_token_part(authorization)

        try:
            return jose.jwt.decode(token, key=self.config.secret, algorithms=self.config.algorithms)
        except jose.exceptions.JWTClaimsError as e:
            raise fastapi.HTTPException(401, f'Invalid claims: {e}') from e
        except jose.exceptions.ExpiredSignatureError as e:
            raise fastapi.HTTPException(401, f'Expired auth: {e}') from e
        except jose.exceptions.JWTError as e:
            raise fastapi.HTTPException(401, f'Invalid auth: {e}') from e

    def verify_auth(self, authorization: str | None):
        payload = self._get_verified_payload(authorization)

        try:
            user = TokenPayload(**payload)
        except pydantic.ValidationError as e:
            raise fastapi.HTTPException(401, f'invalid token payload: {e.json()}') from e

        if user.username is None:
            raise fastapi.HTTPException(401, 'token payload must have a username')

        # remove uuid at the start of the username
        with contextlib.suppress(ValueError):
            uuid.UUID(user.username[:36])
            user.username = user.username[36:].strip()

        if user.permissions is None or user.permissions < self.config.admin_permissions:
            raise fastapi.HTTPException(
                403,
                f'current permissions: {user.permissions}, '
                f'required permissions: {self.config.admin_permissions}',
            )

        return User(permission=user.permissions, username=user.username)
