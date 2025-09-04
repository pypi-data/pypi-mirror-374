import contextlib
import dataclasses
import enum
import getpass
import json
import sys
import typing

import httpx
import keyring
import keyring.errors
import pydantic
import slugify

from unico_device_setuper.lib import cnsl, env, unitech, util


def get_credentials_key(login_platform: str, env: env.Env):
    return f'{login_platform}_{env.name}_credentials'


async def get_credentials[T: pydantic.BaseModel](
    login_platform_name: str,
    env: env.Env,
    callback: typing.Callable[[str, str], typing.Awaitable[T]],
    credential_type: type[T],
) -> T:
    credentials_key = get_credentials_key(login_platform_name, env)
    encoded_credentials = keyring.get_password(util.APP_NAME, credentials_key)
    if encoded_credentials is not None:
        with contextlib.suppress(pydantic.ValidationError):
            return credential_type.model_validate_json(encoded_credentials)

    cnsl.print_blue(f'Connexion à votre compte {login_platform_name.capitalize()} ({env.value}):')
    username = input("Nom d'utilisateur: ")
    password = getpass.getpass('Mot de passe: ')
    cnsl.print('')

    credentials = await callback(username, password)

    keyring.set_password(util.APP_NAME, credentials_key, credentials.model_dump_json())
    return credentials


def clear_credentials(login_platform_name: str, env: env.Env):
    with contextlib.suppress(keyring.errors.PasswordDeleteError):
        keyring.delete_password(util.APP_NAME, get_credentials_key(login_platform_name, env))


# Unitech


class UnitechCredentials(pydantic.BaseModel):
    username: str
    password: str


UNITECH_NAME = 'unitech'


@dataclasses.dataclass
class PickWithName:
    name: str


class PickAny(enum.Enum):
    PICK_ANY = enum.auto()


PICK_ANY = PickAny.PICK_ANY


class PickInteractive(enum.Enum):
    PICK_INTERACTIVE = enum.auto()


PICK_INTERACTIVE = PickInteractive.PICK_INTERACTIVE

ClientStrategy: typing.TypeAlias = PickWithName | PickAny | PickInteractive


async def choose_client(
    clients: list[unitech.AccessibleClientsResponseItem], strategy: ClientStrategy
):
    match strategy:
        case PickWithName(name):
            slugified_name = slugify.slugify(name)
            client = next((c for c in clients if slugify.slugify(c.name) == slugified_name), None)
            if client is None:
                cnsl.print_red(f'Aucun client avec le nom [hot_pink3]`{name}`[/hot_pink3]')
                return None
        case PickAny():
            client = clients[0]
        case PickInteractive():
            cnsl.print_blue('Chosir un client:')
            client = await cnsl.print_choose(
                sorted(clients, key=lambda c: slugify.slugify(c.name)),
                prompt='Client: ',
                formater=lambda c: c.name.strip(),
            )
            cnsl.print()

    return client


async def get_unitech_auth_token(env: env.Env, client_strategy: ClientStrategy):
    credentials = await get_credentials(
        login_platform_name=UNITECH_NAME,
        env=env,
        callback=lambda username, password: util.wrap_async(
            UnitechCredentials(username=username, password=password)
        ),
        credential_type=UnitechCredentials,
    )
    api_client = unitech.Client(base_url=str(env.api_base_url))
    login_first_stage_response = await unitech.post_auth_accessible_clients.detailed_request(
        client=api_client,
        body=unitech.AccessibleClientsPayload(credentials.username, credentials.password),
    )
    if login_first_stage_response.status_code != 200:
        clear_credentials(UNITECH_NAME, env)
        error_message = 'Erreur inconnue'
        with contextlib.suppress(json.JSONDecodeError, KeyError):
            error_message = json.loads(login_first_stage_response.content)['displayMessage']
        cnsl.print_red(f'{error_message}')
        sys.exit()

    assert isinstance(login_first_stage_response.parsed, list)

    client = await choose_client(login_first_stage_response.parsed, client_strategy)
    if client is None:
        return None

    login_second_stage_response = await unitech.post_auth_token.request(
        client=api_client,
        body=unitech.TokenPayload(credentials.username, credentials.password, id_client=client.id),
    )
    assert isinstance(login_second_stage_response, unitech.TokenResponse)
    return login_second_stage_response.access_token


# Sygic


class SygicCredential(pydantic.BaseModel):
    api_key: str


SYGIC_NAME = 'sygic'


async def sygic_login(username: str, password: str, env: env.Env, http_client: httpx.AsyncClient):
    response = await http_client.post(
        url=f'{env.api_base_url}/authentication', json={'userEmail': username, 'password': password}
    )
    return SygicCredential(api_key=response.json().get('apiKey'))


async def get_sygic_api_key(env: env.Env, http_client: httpx.AsyncClient):
    return (
        await get_credentials(
            login_platform_name=SYGIC_NAME,
            env=env,
            callback=lambda username, password: sygic_login(username, password, env, http_client),
            credential_type=SygicCredential,
        )
    ).api_key
