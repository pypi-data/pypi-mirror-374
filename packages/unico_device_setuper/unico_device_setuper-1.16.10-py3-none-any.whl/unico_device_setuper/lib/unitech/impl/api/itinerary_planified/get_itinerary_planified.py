from http import HTTPStatus
from typing import Any, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import UNSET, Response, Unset


def _get_kwargs(
    
    ids: Union[Unset, str] = UNSET,
    authorization: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    params: dict[str, Any] = {}

    params["ids"] = ids

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/itinerary-planified/",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response( client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Any:
    return None


def _build_response( client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    
    client: Union[AuthenticatedClient, Client],
    ids: Union[Unset, str] = UNSET,
    authorization: Union[None, Unset, str] = UNSET,
) -> Response[Any]:
    """
    Args:
        ids (Union[Unset, str]):
        authorization (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        ids=ids,
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def detailed_request(
    
    client: Union[AuthenticatedClient, Client],
    ids: Union[Unset, str] = UNSET,
    authorization: Union[None, Unset, str] = UNSET,
) -> Response[Any]:
    """
    Args:
        ids (Union[Unset, str]):
        authorization (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        ids=ids,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
