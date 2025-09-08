from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.channel_bookmark_with_file_info import ChannelBookmarkWithFileInfo
from ...types import Response


def _get_kwargs(
    channel_id: str,
    bookmark_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": f"/api/v4/channels/{channel_id}/bookmarks/{bookmark_id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, ChannelBookmarkWithFileInfo]]:
    if response.status_code == 200:
        response_200 = ChannelBookmarkWithFileInfo.from_dict(response.json())

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

    if response.status_code == 404:
        response_404 = AppError.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, ChannelBookmarkWithFileInfo]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    channel_id: str,
    bookmark_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, ChannelBookmarkWithFileInfo]]:
    """Delete channel bookmark

     Archives a channel bookmark. This will set the `deleteAt` to
    the current timestamp in the database.

    __Minimum server version__: 9.5

    ##### Permissions
    Must have the `delete_bookmark_public_channel` or
    `delete_bookmark_private_channel` depending on the channel
    type. If the channel is a DM or GM, must be a non-guest
    member.

    Args:
        channel_id (str):
        bookmark_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, ChannelBookmarkWithFileInfo]]
    """

    kwargs = _get_kwargs(
        channel_id=channel_id,
        bookmark_id=bookmark_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    channel_id: str,
    bookmark_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, ChannelBookmarkWithFileInfo]]:
    """Delete channel bookmark

     Archives a channel bookmark. This will set the `deleteAt` to
    the current timestamp in the database.

    __Minimum server version__: 9.5

    ##### Permissions
    Must have the `delete_bookmark_public_channel` or
    `delete_bookmark_private_channel` depending on the channel
    type. If the channel is a DM or GM, must be a non-guest
    member.

    Args:
        channel_id (str):
        bookmark_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, ChannelBookmarkWithFileInfo]
    """

    return sync_detailed(
        channel_id=channel_id,
        bookmark_id=bookmark_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    channel_id: str,
    bookmark_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, ChannelBookmarkWithFileInfo]]:
    """Delete channel bookmark

     Archives a channel bookmark. This will set the `deleteAt` to
    the current timestamp in the database.

    __Minimum server version__: 9.5

    ##### Permissions
    Must have the `delete_bookmark_public_channel` or
    `delete_bookmark_private_channel` depending on the channel
    type. If the channel is a DM or GM, must be a non-guest
    member.

    Args:
        channel_id (str):
        bookmark_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, ChannelBookmarkWithFileInfo]]
    """

    kwargs = _get_kwargs(
        channel_id=channel_id,
        bookmark_id=bookmark_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    channel_id: str,
    bookmark_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, ChannelBookmarkWithFileInfo]]:
    """Delete channel bookmark

     Archives a channel bookmark. This will set the `deleteAt` to
    the current timestamp in the database.

    __Minimum server version__: 9.5

    ##### Permissions
    Must have the `delete_bookmark_public_channel` or
    `delete_bookmark_private_channel` depending on the channel
    type. If the channel is a DM or GM, must be a non-guest
    member.

    Args:
        channel_id (str):
        bookmark_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, ChannelBookmarkWithFileInfo]
    """

    return (
        await asyncio_detailed(
            channel_id=channel_id,
            bookmark_id=bookmark_id,
            client=client,
        )
    ).parsed
