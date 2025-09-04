from http import HTTPStatus
from typing import Any, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import UNSET, Response, Unset


def _get_kwargs(
    
    producing_place_query: Union[Unset, str] = UNSET,
    id_itinerary: Union[Unset, str] = UNSET,
    page: Union[Unset, str] = UNSET,
    city: Union[Unset, str] = UNSET,
    authorization: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    params: dict[str, Any] = {}

    params["producingPlaceQuery"] = producing_place_query

    params["idItinerary"] = id_itinerary

    params["page"] = page

    params["city"] = city

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/device/searchProducingPlace",
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
    producing_place_query: Union[Unset, str] = UNSET,
    id_itinerary: Union[Unset, str] = UNSET,
    page: Union[Unset, str] = UNSET,
    city: Union[Unset, str] = UNSET,
    authorization: Union[None, Unset, str] = UNSET,
) -> Response[Any]:
    """
    Args:
        producing_place_query (Union[Unset, str]):
        id_itinerary (Union[Unset, str]):
        page (Union[Unset, str]):
        city (Union[Unset, str]):
        authorization (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        producing_place_query=producing_place_query,
        id_itinerary=id_itinerary,
        page=page,
        city=city,
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def detailed_request(
    
    client: Union[AuthenticatedClient, Client],
    producing_place_query: Union[Unset, str] = UNSET,
    id_itinerary: Union[Unset, str] = UNSET,
    page: Union[Unset, str] = UNSET,
    city: Union[Unset, str] = UNSET,
    authorization: Union[None, Unset, str] = UNSET,
) -> Response[Any]:
    """
    Args:
        producing_place_query (Union[Unset, str]):
        id_itinerary (Union[Unset, str]):
        page (Union[Unset, str]):
        city (Union[Unset, str]):
        authorization (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        producing_place_query=producing_place_query,
        id_itinerary=id_itinerary,
        page=page,
        city=city,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
