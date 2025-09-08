from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.channel_member import ChannelMember
from ...types import Response


def _get_kwargs(
    channel_id: str,
    user_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v4/channels/{channel_id}/members/{user_id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, ChannelMember]]:
    if response.status_code == 200:
        response_200 = ChannelMember.from_dict(response.json())

        return response_200

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
) -> Response[Union[AppError, ChannelMember]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    channel_id: str,
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, ChannelMember]]:
    """Get channel member

     Get a channel member.
    ##### Permissions
    `read_channel` permission for the channel.

    Args:
        channel_id (str):
        user_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, ChannelMember]]
    """

    kwargs = _get_kwargs(
        channel_id=channel_id,
        user_id=user_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    channel_id: str,
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, ChannelMember]]:
    """Get channel member

     Get a channel member.
    ##### Permissions
    `read_channel` permission for the channel.

    Args:
        channel_id (str):
        user_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, ChannelMember]
    """

    return sync_detailed(
        channel_id=channel_id,
        user_id=user_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    channel_id: str,
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, ChannelMember]]:
    """Get channel member

     Get a channel member.
    ##### Permissions
    `read_channel` permission for the channel.

    Args:
        channel_id (str):
        user_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, ChannelMember]]
    """

    kwargs = _get_kwargs(
        channel_id=channel_id,
        user_id=user_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    channel_id: str,
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, ChannelMember]]:
    """Get channel member

     Get a channel member.
    ##### Permissions
    `read_channel` permission for the channel.

    Args:
        channel_id (str):
        user_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, ChannelMember]
    """

    return (
        await asyncio_detailed(
            channel_id=channel_id,
            user_id=user_id,
            client=client,
        )
    ).parsed
