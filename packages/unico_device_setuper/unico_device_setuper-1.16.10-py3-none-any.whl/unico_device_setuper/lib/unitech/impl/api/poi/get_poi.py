from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_pois_response_item import GetPoisResponseItem
from ...types import UNSET, Response, Unset


def _get_kwargs(
    
    authorization: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/poi/",
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
     client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[list["GetPoisResponseItem"]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for componentsschemas_get_pois_response_item_data in _response_200:
            componentsschemas_get_pois_response_item = GetPoisResponseItem.from_dict(
                componentsschemas_get_pois_response_item_data
            )

            response_200.append(componentsschemas_get_pois_response_item)

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
     client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["GetPoisResponseItem"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    
    client: Union[AuthenticatedClient, Client],
    authorization: Union[None, Unset, str] = UNSET,
) -> Response[list["GetPoisResponseItem"]]:
    """
    Args:
        authorization (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['GetPoisResponseItem']]
    """

    kwargs = _get_kwargs(
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    
    client: Union[AuthenticatedClient, Client],
    authorization: Union[None, Unset, str] = UNSET,
) -> Optional[list["GetPoisResponseItem"]]:
    """
    Args:
        authorization (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['GetPoisResponseItem']
    """

    return sync_detailed(
        client=client,
        authorization=authorization,
    ).parsed


async def detailed_request(
    
    client: Union[AuthenticatedClient, Client],
    authorization: Union[None, Unset, str] = UNSET,
) -> Response[list["GetPoisResponseItem"]]:
    """
    Args:
        authorization (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['GetPoisResponseItem']]
    """

    kwargs = _get_kwargs(
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def request(
    
    client: Union[AuthenticatedClient, Client],
    authorization: Union[None, Unset, str] = UNSET,
) -> Optional[list["GetPoisResponseItem"]]:
    """
    Args:
        authorization (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['GetPoisResponseItem']
    """

    return (
        await detailed_request(
            client=client,
            authorization=authorization,
        )
    ).parsed
