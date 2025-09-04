import contextlib
import dataclasses
import typing

import fastapi
import slugify
import starlette.middleware
import starlette.middleware.base

import unico_device_setuper
from unico_device_setuper.backend import routes, state, token_verifier
from unico_device_setuper.lib import cfg, oci

type StateMaker = typing.Callable[[fastapi.FastAPI], typing.AsyncContextManager[state.State]]
type Middleware = typing.Callable[
    [fastapi.Request, typing.Callable[[fastapi.Request], typing.Awaitable[fastapi.Response]]],
    typing.Awaitable[fastapi.Response],
]


@dataclasses.dataclass
class ApiInfo:
    title: str
    contact_name: str
    contact_url: str
    contact_email: str


@contextlib.asynccontextmanager
async def make_state(config: cfg.Config, app: fastapi.FastAPI):
    app.version = unico_device_setuper.__version__

    async with oci.Context.make(config.oci) as oci_:
        yield state.RawState(
            config=config, token_verifier=token_verifier.TokenVerifier(config.security), oci=oci_
        )


def make_app_from_config(config: cfg.Config):
    return make_app(
        ApiInfo(
            title='Device Setuper',
            contact_name='Unico France',
            contact_url='https://www.unicofrance.com/',
            contact_email='contact@unicofrance.com',
        ),
        routers=routes.ROUTERS,
        state_maker=lambda app: make_state(config=config, app=app),
        middlewares=[],
    )


def _iter_path_operations(schema: dict[str, typing.Any]):
    paths = schema['paths']
    for route, path in paths.items():
        if len(path) == 1:
            yield '', route, next(iter(path.values()))
        else:
            for method, operation in path.items():
                yield method, route, operation


def _rename_operation_ids(schema: dict[str, typing.Any]):
    for method, route, operation in _iter_path_operations(schema):
        operation['operationId'] = slugify.slugify(f'{method} {route}', separator='_')


def _rename_summaries(schema: dict[str, typing.Any]):
    for method, route, operation in _iter_path_operations(schema):
        operation['summary'] = ' '.join(
            [
                s.capitalize()
                for s in slugify.slugify(
                    f'{method} {route.rpartition('/')[-1]}', separator=' '
                ).split()
            ]
        )


def make_app(
    api_info: ApiInfo,
    *,
    routers: list[fastapi.APIRouter],
    state_maker: StateMaker,
    middlewares: list[Middleware],
):
    @contextlib.asynccontextmanager
    async def lifespan(app: fastapi.FastAPI):
        async with state_maker(app) as state:
            yield state.attach()

    app = fastapi.FastAPI(
        lifespan=lifespan,
        title=api_info.title,
        contact={
            'name': api_info.contact_name,
            'url': api_info.contact_url,
            'email': api_info.contact_email,
        },
        middleware=[
            starlette.middleware.Middleware(
                starlette.middleware.base.BaseHTTPMiddleware, dispatch=middleware
            )
            for middleware in middlewares
        ],
    )

    for router in routers:
        app.include_router(router)

    openapi_schema = app.openapi()
    _rename_summaries(openapi_schema)
    _rename_operation_ids(openapi_schema)
    app.openapi_schema = openapi_schema

    return app
