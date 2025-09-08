from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.channel import Channel
from ...models.create_channel_body import CreateChannelBody
from ...types import Response


def _get_kwargs(
    *,
    body: CreateChannelBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v4/channels",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, Channel]]:
    if response.status_code == 201:
        response_201 = Channel.from_dict(response.json())

        return response_201

    if response.status_code == 400:
        response_400 = AppError.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = AppError.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = AppError.from_dict(response.json())

        return response_403

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, Channel]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CreateChannelBody,
) -> Response[Union[AppError, Channel]]:
    """Create a channel

     Create a new channel.
    ##### Permissions
    If creating a public channel, `create_public_channel` permission is required. If creating a private
    channel, `create_private_channel` permission is required.

    Args:
        body (CreateChannelBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, Channel]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CreateChannelBody,
) -> Optional[Union[AppError, Channel]]:
    """Create a channel

     Create a new channel.
    ##### Permissions
    If creating a public channel, `create_public_channel` permission is required. If creating a private
    channel, `create_private_channel` permission is required.

    Args:
        body (CreateChannelBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, Channel]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CreateChannelBody,
) -> Response[Union[AppError, Channel]]:
    """Create a channel

     Create a new channel.
    ##### Permissions
    If creating a public channel, `create_public_channel` permission is required. If creating a private
    channel, `create_private_channel` permission is required.

    Args:
        body (CreateChannelBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, Channel]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CreateChannelBody,
) -> Optional[Union[AppError, Channel]]:
    """Create a channel

     Create a new channel.
    ##### Permissions
    If creating a public channel, `create_public_channel` permission is required. If creating a private
    channel, `create_private_channel` permission is required.

    Args:
        body (CreateChannelBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, Channel]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
