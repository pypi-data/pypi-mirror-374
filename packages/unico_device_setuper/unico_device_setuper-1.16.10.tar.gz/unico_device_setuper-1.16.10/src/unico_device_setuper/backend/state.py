import dataclasses
import typing

import fastapi
import starlette.datastructures

from unico_device_setuper.backend import token_verifier
from unico_device_setuper.lib import cfg, oci


@dataclasses.dataclass
class RawState:
    token_verifier: token_verifier.TokenVerifier
    config: cfg.Config
    oci: oci.Context

    def attach(self):
        return {'state': self}


def _detach_state(attached_state: starlette.datastructures.State):
    state = getattr(attached_state, 'state', None)
    if state is None:
        raise RuntimeError('Cannot find state')
    if not isinstance(state, RawState):
        raise TypeError('Invalid state')
    return state


def detach_state(request: fastapi.Request):
    return _detach_state(request.state)


State = typing.Annotated[RawState, fastapi.Depends(detach_state)]
