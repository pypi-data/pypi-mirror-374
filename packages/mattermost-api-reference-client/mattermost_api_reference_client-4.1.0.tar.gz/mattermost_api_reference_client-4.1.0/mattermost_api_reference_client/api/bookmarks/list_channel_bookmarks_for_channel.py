from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.channel_bookmark_with_file_info import ChannelBookmarkWithFileInfo
from ...types import UNSET, Response, Unset


def _get_kwargs(
    channel_id: str,
    *,
    bookmarks_since: Union[Unset, float] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["bookmarks_since"] = bookmarks_since

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v4/channels/{channel_id}/bookmarks",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, list["ChannelBookmarkWithFileInfo"]]]:
    if response.status_code == 201:
        response_201 = []
        _response_201 = response.json()
        for response_201_item_data in _response_201:
            response_201_item = ChannelBookmarkWithFileInfo.from_dict(response_201_item_data)

            response_201.append(response_201_item)

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
) -> Response[Union[AppError, list["ChannelBookmarkWithFileInfo"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    channel_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    bookmarks_since: Union[Unset, float] = UNSET,
) -> Response[Union[AppError, list["ChannelBookmarkWithFileInfo"]]]:
    """Get channel bookmarks for Channel

     __Minimum server version__: 9.5

    Args:
        channel_id (str):
        bookmarks_since (Union[Unset, float]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['ChannelBookmarkWithFileInfo']]]
    """

    kwargs = _get_kwargs(
        channel_id=channel_id,
        bookmarks_since=bookmarks_since,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    channel_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    bookmarks_since: Union[Unset, float] = UNSET,
) -> Optional[Union[AppError, list["ChannelBookmarkWithFileInfo"]]]:
    """Get channel bookmarks for Channel

     __Minimum server version__: 9.5

    Args:
        channel_id (str):
        bookmarks_since (Union[Unset, float]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['ChannelBookmarkWithFileInfo']]
    """

    return sync_detailed(
        channel_id=channel_id,
        client=client,
        bookmarks_since=bookmarks_since,
    ).parsed


async def asyncio_detailed(
    channel_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    bookmarks_since: Union[Unset, float] = UNSET,
) -> Response[Union[AppError, list["ChannelBookmarkWithFileInfo"]]]:
    """Get channel bookmarks for Channel

     __Minimum server version__: 9.5

    Args:
        channel_id (str):
        bookmarks_since (Union[Unset, float]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['ChannelBookmarkWithFileInfo']]]
    """

    kwargs = _get_kwargs(
        channel_id=channel_id,
        bookmarks_since=bookmarks_since,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    channel_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    bookmarks_since: Union[Unset, float] = UNSET,
) -> Optional[Union[AppError, list["ChannelBookmarkWithFileInfo"]]]:
    """Get channel bookmarks for Channel

     __Minimum server version__: 9.5

    Args:
        channel_id (str):
        bookmarks_since (Union[Unset, float]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['ChannelBookmarkWithFileInfo']]
    """

    return (
        await asyncio_detailed(
            channel_id=channel_id,
            client=client,
            bookmarks_since=bookmarks_since,
        )
    ).parsed
