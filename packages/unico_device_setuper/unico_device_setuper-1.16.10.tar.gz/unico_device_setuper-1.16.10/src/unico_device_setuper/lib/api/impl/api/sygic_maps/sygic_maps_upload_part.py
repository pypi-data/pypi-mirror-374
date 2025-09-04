from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.sygic_maps_upload_part_payload import SygicMapsUploadPartPayload
from ...models.sygic_maps_upload_part_response import SygicMapsUploadPartResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    
    body: SygicMapsUploadPartPayload,
    authorization: Union[None, Unset, str] = UNSET,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    _kwargs: Dict[str, Any] = {
        "method": "put",
        "url": "/sygic_maps/upload_part",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
     client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, SygicMapsUploadPartResponse]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = SygicMapsUploadPartResponse.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, SygicMapsUploadPartResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    
    client: Union[AuthenticatedClient, Client],
    body: SygicMapsUploadPartPayload,
    authorization: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, SygicMapsUploadPartResponse]]:
    """Upload Part

    Args:
        authorization (Union[None, Unset, str]):
        body (SygicMapsUploadPartPayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, SygicMapsUploadPartResponse]]
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
    body: SygicMapsUploadPartPayload,
    authorization: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, SygicMapsUploadPartResponse]]:
    """Upload Part

    Args:
        authorization (Union[None, Unset, str]):
        body (SygicMapsUploadPartPayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, SygicMapsUploadPartResponse]
    """

    return sync_detailed(
        client=client,
        body=body,
        authorization=authorization,
    ).parsed


async def detailed_request(
    
    client: Union[AuthenticatedClient, Client],
    body: SygicMapsUploadPartPayload,
    authorization: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, SygicMapsUploadPartResponse]]:
    """Upload Part

    Args:
        authorization (Union[None, Unset, str]):
        body (SygicMapsUploadPartPayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, SygicMapsUploadPartResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def request(
    
    client: Union[AuthenticatedClient, Client],
    body: SygicMapsUploadPartPayload,
    authorization: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, SygicMapsUploadPartResponse]]:
    """Upload Part

    Args:
        authorization (Union[None, Unset, str]):
        body (SygicMapsUploadPartPayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, SygicMapsUploadPartResponse]
    """

    return (
        await detailed_request(
            client=client,
            body=body,
            authorization=authorization,
        )
    ).parsed
