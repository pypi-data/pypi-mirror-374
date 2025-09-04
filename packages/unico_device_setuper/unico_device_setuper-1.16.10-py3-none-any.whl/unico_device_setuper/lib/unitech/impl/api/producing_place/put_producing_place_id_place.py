from http import HTTPStatus
from typing import Any, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...models.put_producing_place_id_place_body import PutProducingPlaceIdPlaceBody
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: str,
    
    body: PutProducingPlaceIdPlaceBody,
    authorization: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/producingPlace/{id}/place",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

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
    id: str,
    
    client: Union[AuthenticatedClient, Client],
    body: PutProducingPlaceIdPlaceBody,
    authorization: Union[None, Unset, str] = UNSET,
) -> Response[Any]:
    """
    Args:
        id (str):
        authorization (Union[None, Unset, str]):
        body (PutProducingPlaceIdPlaceBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def detailed_request(
    id: str,
    
    client: Union[AuthenticatedClient, Client],
    body: PutProducingPlaceIdPlaceBody,
    authorization: Union[None, Unset, str] = UNSET,
) -> Response[Any]:
    """
    Args:
        id (str):
        authorization (Union[None, Unset, str]):
        body (PutProducingPlaceIdPlaceBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
