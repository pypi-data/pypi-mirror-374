from http import HTTPStatus
from typing import Any, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import UNSET, Response, Unset


def _get_kwargs(
    
    producing_place_id: Union[Unset, str] = UNSET,
    producer_id: Union[Unset, str] = UNSET,
    event_id: Union[Unset, str] = UNSET,
    authorization: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    params: dict[str, Any] = {}

    params["producingPlaceId"] = producing_place_id

    params["producerId"] = producer_id

    params["eventId"] = event_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/attachment/",
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
    producing_place_id: Union[Unset, str] = UNSET,
    producer_id: Union[Unset, str] = UNSET,
    event_id: Union[Unset, str] = UNSET,
    authorization: Union[None, Unset, str] = UNSET,
) -> Response[Any]:
    """
    Args:
        producing_place_id (Union[Unset, str]):
        producer_id (Union[Unset, str]):
        event_id (Union[Unset, str]):
        authorization (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        producing_place_id=producing_place_id,
        producer_id=producer_id,
        event_id=event_id,
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def detailed_request(
    
    client: Union[AuthenticatedClient, Client],
    producing_place_id: Union[Unset, str] = UNSET,
    producer_id: Union[Unset, str] = UNSET,
    event_id: Union[Unset, str] = UNSET,
    authorization: Union[None, Unset, str] = UNSET,
) -> Response[Any]:
    """
    Args:
        producing_place_id (Union[Unset, str]):
        producer_id (Union[Unset, str]):
        event_id (Union[Unset, str]):
        authorization (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        producing_place_id=producing_place_id,
        producer_id=producer_id,
        event_id=event_id,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
