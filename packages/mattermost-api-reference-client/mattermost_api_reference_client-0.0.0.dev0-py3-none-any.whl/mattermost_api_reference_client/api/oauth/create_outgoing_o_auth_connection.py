from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.outgoing_o_auth_connection_get_item import OutgoingOAuthConnectionGetItem
from ...models.outgoing_o_auth_connection_post_item import OutgoingOAuthConnectionPostItem
from ...types import UNSET, Response


def _get_kwargs(
    *,
    body: OutgoingOAuthConnectionPostItem,
    team_id: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["team_id"] = team_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v4/oauth/outgoing_connections",
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, OutgoingOAuthConnectionGetItem]]:
    if response.status_code == 201:
        response_201 = OutgoingOAuthConnectionGetItem.from_dict(response.json())

        return response_201

    if response.status_code == 400:
        response_400 = AppError.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = AppError.from_dict(response.json())

        return response_401

    if response.status_code == 500:
        response_500 = AppError.from_dict(response.json())

        return response_500

    if response.status_code == 501:
        response_501 = AppError.from_dict(response.json())

        return response_501

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, OutgoingOAuthConnectionGetItem]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: OutgoingOAuthConnectionPostItem,
    team_id: str,
) -> Response[Union[AppError, OutgoingOAuthConnectionGetItem]]:
    """Create a connection

     Create an outgoing OAuth connection.
    __Minimum server version__: 9.6

    Args:
        team_id (str):
        body (OutgoingOAuthConnectionPostItem):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, OutgoingOAuthConnectionGetItem]]
    """

    kwargs = _get_kwargs(
        body=body,
        team_id=team_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: OutgoingOAuthConnectionPostItem,
    team_id: str,
) -> Optional[Union[AppError, OutgoingOAuthConnectionGetItem]]:
    """Create a connection

     Create an outgoing OAuth connection.
    __Minimum server version__: 9.6

    Args:
        team_id (str):
        body (OutgoingOAuthConnectionPostItem):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, OutgoingOAuthConnectionGetItem]
    """

    return sync_detailed(
        client=client,
        body=body,
        team_id=team_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: OutgoingOAuthConnectionPostItem,
    team_id: str,
) -> Response[Union[AppError, OutgoingOAuthConnectionGetItem]]:
    """Create a connection

     Create an outgoing OAuth connection.
    __Minimum server version__: 9.6

    Args:
        team_id (str):
        body (OutgoingOAuthConnectionPostItem):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, OutgoingOAuthConnectionGetItem]]
    """

    kwargs = _get_kwargs(
        body=body,
        team_id=team_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: OutgoingOAuthConnectionPostItem,
    team_id: str,
) -> Optional[Union[AppError, OutgoingOAuthConnectionGetItem]]:
    """Create a connection

     Create an outgoing OAuth connection.
    __Minimum server version__: 9.6

    Args:
        team_id (str):
        body (OutgoingOAuthConnectionPostItem):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, OutgoingOAuthConnectionGetItem]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            team_id=team_id,
        )
    ).parsed
