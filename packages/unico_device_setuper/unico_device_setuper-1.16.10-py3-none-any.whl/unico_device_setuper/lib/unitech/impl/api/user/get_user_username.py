from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.current_user_response import CurrentUserResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    username: str,
    
    authorization: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/user/{username}",
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
     client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[CurrentUserResponse]:
    if response.status_code == 200:
        response_200 = CurrentUserResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
     client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[CurrentUserResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    username: str,
    
    client: Union[AuthenticatedClient, Client],
    authorization: Union[None, Unset, str] = UNSET,
) -> Response[CurrentUserResponse]:
    """
    Args:
        username (str):
        authorization (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CurrentUserResponse]
    """

    kwargs = _get_kwargs(
        username=username,
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    username: str,
    
    client: Union[AuthenticatedClient, Client],
    authorization: Union[None, Unset, str] = UNSET,
) -> Optional[CurrentUserResponse]:
    """
    Args:
        username (str):
        authorization (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CurrentUserResponse
    """

    return sync_detailed(
        username=username,
        client=client,
        authorization=authorization,
    ).parsed


async def detailed_request(
    username: str,
    
    client: Union[AuthenticatedClient, Client],
    authorization: Union[None, Unset, str] = UNSET,
) -> Response[CurrentUserResponse]:
    """
    Args:
        username (str):
        authorization (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CurrentUserResponse]
    """

    kwargs = _get_kwargs(
        username=username,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def request(
    username: str,
    
    client: Union[AuthenticatedClient, Client],
    authorization: Union[None, Unset, str] = UNSET,
) -> Optional[CurrentUserResponse]:
    """
    Args:
        username (str):
        authorization (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CurrentUserResponse
    """

    return (
        await detailed_request(
            username=username,
            client=client,
            authorization=authorization,
        )
    ).parsed
