from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.post_list import PostList
from ...types import UNSET, Response, Unset


def _get_kwargs(
    user_id: str,
    channel_id: str,
    *,
    limit_before: Union[Unset, int] = 60,
    limit_after: Union[Unset, int] = 60,
    skip_fetch_threads: Union[Unset, bool] = False,
    collapsed_threads: Union[Unset, bool] = False,
    collapsed_threads_extended: Union[Unset, bool] = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["limit_before"] = limit_before

    params["limit_after"] = limit_after

    params["skipFetchThreads"] = skip_fetch_threads

    params["collapsedThreads"] = collapsed_threads

    params["collapsedThreadsExtended"] = collapsed_threads_extended

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v4/users/{user_id}/channels/{channel_id}/posts/unread",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, PostList]]:
    if response.status_code == 200:
        response_200 = PostList.from_dict(response.json())

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
) -> Response[Union[AppError, PostList]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    user_id: str,
    channel_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    limit_before: Union[Unset, int] = 60,
    limit_after: Union[Unset, int] = 60,
    skip_fetch_threads: Union[Unset, bool] = False,
    collapsed_threads: Union[Unset, bool] = False,
    collapsed_threads_extended: Union[Unset, bool] = False,
) -> Response[Union[AppError, PostList]]:
    """Get posts around oldest unread

     Get the oldest unread post in the channel for the given user as well as the posts around it. The
    returned list is sorted in descending order (most recent post first).
    ##### Permissions
    Must be logged in as the user or have `edit_other_users` permission, and must have `read_channel`
    permission for the channel.
    __Minimum server version__: 5.14

    Args:
        user_id (str):
        channel_id (str):
        limit_before (Union[Unset, int]):  Default: 60.
        limit_after (Union[Unset, int]):  Default: 60.
        skip_fetch_threads (Union[Unset, bool]):  Default: False.
        collapsed_threads (Union[Unset, bool]):  Default: False.
        collapsed_threads_extended (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, PostList]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        channel_id=channel_id,
        limit_before=limit_before,
        limit_after=limit_after,
        skip_fetch_threads=skip_fetch_threads,
        collapsed_threads=collapsed_threads,
        collapsed_threads_extended=collapsed_threads_extended,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    user_id: str,
    channel_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    limit_before: Union[Unset, int] = 60,
    limit_after: Union[Unset, int] = 60,
    skip_fetch_threads: Union[Unset, bool] = False,
    collapsed_threads: Union[Unset, bool] = False,
    collapsed_threads_extended: Union[Unset, bool] = False,
) -> Optional[Union[AppError, PostList]]:
    """Get posts around oldest unread

     Get the oldest unread post in the channel for the given user as well as the posts around it. The
    returned list is sorted in descending order (most recent post first).
    ##### Permissions
    Must be logged in as the user or have `edit_other_users` permission, and must have `read_channel`
    permission for the channel.
    __Minimum server version__: 5.14

    Args:
        user_id (str):
        channel_id (str):
        limit_before (Union[Unset, int]):  Default: 60.
        limit_after (Union[Unset, int]):  Default: 60.
        skip_fetch_threads (Union[Unset, bool]):  Default: False.
        collapsed_threads (Union[Unset, bool]):  Default: False.
        collapsed_threads_extended (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, PostList]
    """

    return sync_detailed(
        user_id=user_id,
        channel_id=channel_id,
        client=client,
        limit_before=limit_before,
        limit_after=limit_after,
        skip_fetch_threads=skip_fetch_threads,
        collapsed_threads=collapsed_threads,
        collapsed_threads_extended=collapsed_threads_extended,
    ).parsed


async def asyncio_detailed(
    user_id: str,
    channel_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    limit_before: Union[Unset, int] = 60,
    limit_after: Union[Unset, int] = 60,
    skip_fetch_threads: Union[Unset, bool] = False,
    collapsed_threads: Union[Unset, bool] = False,
    collapsed_threads_extended: Union[Unset, bool] = False,
) -> Response[Union[AppError, PostList]]:
    """Get posts around oldest unread

     Get the oldest unread post in the channel for the given user as well as the posts around it. The
    returned list is sorted in descending order (most recent post first).
    ##### Permissions
    Must be logged in as the user or have `edit_other_users` permission, and must have `read_channel`
    permission for the channel.
    __Minimum server version__: 5.14

    Args:
        user_id (str):
        channel_id (str):
        limit_before (Union[Unset, int]):  Default: 60.
        limit_after (Union[Unset, int]):  Default: 60.
        skip_fetch_threads (Union[Unset, bool]):  Default: False.
        collapsed_threads (Union[Unset, bool]):  Default: False.
        collapsed_threads_extended (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, PostList]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        channel_id=channel_id,
        limit_before=limit_before,
        limit_after=limit_after,
        skip_fetch_threads=skip_fetch_threads,
        collapsed_threads=collapsed_threads,
        collapsed_threads_extended=collapsed_threads_extended,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    user_id: str,
    channel_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    limit_before: Union[Unset, int] = 60,
    limit_after: Union[Unset, int] = 60,
    skip_fetch_threads: Union[Unset, bool] = False,
    collapsed_threads: Union[Unset, bool] = False,
    collapsed_threads_extended: Union[Unset, bool] = False,
) -> Optional[Union[AppError, PostList]]:
    """Get posts around oldest unread

     Get the oldest unread post in the channel for the given user as well as the posts around it. The
    returned list is sorted in descending order (most recent post first).
    ##### Permissions
    Must be logged in as the user or have `edit_other_users` permission, and must have `read_channel`
    permission for the channel.
    __Minimum server version__: 5.14

    Args:
        user_id (str):
        channel_id (str):
        limit_before (Union[Unset, int]):  Default: 60.
        limit_after (Union[Unset, int]):  Default: 60.
        skip_fetch_threads (Union[Unset, bool]):  Default: False.
        collapsed_threads (Union[Unset, bool]):  Default: False.
        collapsed_threads_extended (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, PostList]
    """

    return (
        await asyncio_detailed(
            user_id=user_id,
            channel_id=channel_id,
            client=client,
            limit_before=limit_before,
            limit_after=limit_after,
            skip_fetch_threads=skip_fetch_threads,
            collapsed_threads=collapsed_threads,
            collapsed_threads_extended=collapsed_threads_extended,
        )
    ).parsed
