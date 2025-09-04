import typing

import fastapi

from unico_device_setuper.backend import state, token_verifier


async def _get_user_token_data(
    state: state.State, authorization: str | None = fastapi.Header(None)
):
    return state.token_verifier.verify_auth(authorization)


Token = typing.Annotated[token_verifier.User, fastapi.Depends(_get_user_token_data)]
