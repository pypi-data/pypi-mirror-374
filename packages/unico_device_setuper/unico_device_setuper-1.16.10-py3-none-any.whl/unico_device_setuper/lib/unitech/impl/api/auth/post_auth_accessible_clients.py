from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.accessible_clients_payload import AccessibleClientsPayload
from ...models.accessible_clients_response_item import AccessibleClientsResponseItem
from ...types import UNSET, Response, Unset


def _get_kwargs(
    
    body: AccessibleClientsPayload,
    authorization: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/auth/accessibleClients",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
     client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[list["AccessibleClientsResponseItem"], str]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for componentsschemas_accessible_clients_response_item_data in _response_200:
            componentsschemas_accessible_clients_response_item = AccessibleClientsResponseItem.from_dict(
                componentsschemas_accessible_clients_response_item_data
            )

            response_200.append(componentsschemas_accessible_clients_response_item)

        return response_200

    if response.status_code == 401:
        response_401 = cast(str, response.json())
        return response_401

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
     client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[list["AccessibleClientsResponseItem"], str]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    
    client: Union[AuthenticatedClient, Client],
    body: AccessibleClientsPayload,
    authorization: Union[None, Unset, str] = UNSET,
) -> Response[Union[list["AccessibleClientsResponseItem"], str]]:
    """
    Args:
        authorization (Union[None, Unset, str]):
        body (AccessibleClientsPayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[list['AccessibleClientsResponseItem'], str]]
    """

    kwargs = _get_kwargs(
        body=body,
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    
    client: Union[AuthenticatedClient, Client],
    body: AccessibleClientsPayload,
    authorization: Union[None, Unset, str] = UNSET,
) -> Optional[Union[list["AccessibleClientsResponseItem"], str]]:
    """
    Args:
        authorization (Union[None, Unset, str]):
        body (AccessibleClientsPayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[list['AccessibleClientsResponseItem'], str]
    """

    return sync_detailed(
        client=client,
        body=body,
        authorization=authorization,
    ).parsed


async def detailed_request(
    
    client: Union[AuthenticatedClient, Client],
    body: AccessibleClientsPayload,
    authorization: Union[None, Unset, str] = UNSET,
) -> Response[Union[list["AccessibleClientsResponseItem"], str]]:
    """
    Args:
        authorization (Union[None, Unset, str]):
        body (AccessibleClientsPayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[list['AccessibleClientsResponseItem'], str]]
    """

    kwargs = _get_kwargs(
        body=body,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def request(
    
    client: Union[AuthenticatedClient, Client],
    body: AccessibleClientsPayload,
    authorization: Union[None, Unset, str] = UNSET,
) -> Optional[Union[list["AccessibleClientsResponseItem"], str]]:
    """
    Args:
        authorization (Union[None, Unset, str]):
        body (AccessibleClientsPayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[list['AccessibleClientsResponseItem'], str]
    """

    return (
        await detailed_request(
            client=client,
            body=body,
            authorization=authorization,
        )
    ).parsed
