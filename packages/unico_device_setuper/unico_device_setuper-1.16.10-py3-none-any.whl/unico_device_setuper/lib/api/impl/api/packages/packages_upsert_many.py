from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.empty_response import EmptyResponse
from ...models.http_validation_error import HTTPValidationError
from ...models.package import Package
from ...types import UNSET, Response, Unset


def _get_kwargs(
    
    body: List["Package"],
    authorization: Union[None, Unset, str] = UNSET,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/packages/upsert_many",
    }

    _body = []
    for body_item_data in body:
        body_item = body_item_data.to_dict()
        _body.append(body_item)

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
     client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[EmptyResponse, HTTPValidationError]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = EmptyResponse.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
     client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[EmptyResponse, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    
    client: Union[AuthenticatedClient, Client],
    body: List["Package"],
    authorization: Union[None, Unset, str] = UNSET,
) -> Response[Union[EmptyResponse, HTTPValidationError]]:
    """Upsert Many

    Args:
        authorization (Union[None, Unset, str]):
        body (List['Package']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[EmptyResponse, HTTPValidationError]]
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
    body: List["Package"],
    authorization: Union[None, Unset, str] = UNSET,
) -> Optional[Union[EmptyResponse, HTTPValidationError]]:
    """Upsert Many

    Args:
        authorization (Union[None, Unset, str]):
        body (List['Package']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[EmptyResponse, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        body=body,
        authorization=authorization,
    ).parsed


async def detailed_request(
    
    client: Union[AuthenticatedClient, Client],
    body: List["Package"],
    authorization: Union[None, Unset, str] = UNSET,
) -> Response[Union[EmptyResponse, HTTPValidationError]]:
    """Upsert Many

    Args:
        authorization (Union[None, Unset, str]):
        body (List['Package']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[EmptyResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        body=body,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def request(
    
    client: Union[AuthenticatedClient, Client],
    body: List["Package"],
    authorization: Union[None, Unset, str] = UNSET,
) -> Optional[Union[EmptyResponse, HTTPValidationError]]:
    """Upsert Many

    Args:
        authorization (Union[None, Unset, str]):
        body (List['Package']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[EmptyResponse, HTTPValidationError]
    """

    return (
        await detailed_request(
            client=client,
            body=body,
            authorization=authorization,
        )
    ).parsed
