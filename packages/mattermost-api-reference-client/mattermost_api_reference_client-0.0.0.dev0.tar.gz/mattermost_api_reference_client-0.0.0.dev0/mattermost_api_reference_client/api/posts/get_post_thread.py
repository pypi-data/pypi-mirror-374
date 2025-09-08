from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.post_list import PostList
from ...types import UNSET, Response, Unset


def _get_kwargs(
    post_id: str,
    *,
    per_page: Union[Unset, int] = 0,
    from_post: Union[Unset, str] = "",
    from_create_at: Union[Unset, int] = 0,
    from_update_at: Union[Unset, int] = 0,
    direction: Union[Unset, str] = "",
    skip_fetch_threads: Union[Unset, bool] = False,
    collapsed_threads: Union[Unset, bool] = False,
    collapsed_threads_extended: Union[Unset, bool] = False,
    updates_only: Union[Unset, bool] = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["perPage"] = per_page

    params["fromPost"] = from_post

    params["fromCreateAt"] = from_create_at

    params["fromUpdateAt"] = from_update_at

    params["direction"] = direction

    params["skipFetchThreads"] = skip_fetch_threads

    params["collapsedThreads"] = collapsed_threads

    params["collapsedThreadsExtended"] = collapsed_threads_extended

    params["updatesOnly"] = updates_only

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v4/posts/{post_id}/thread",
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
    post_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    per_page: Union[Unset, int] = 0,
    from_post: Union[Unset, str] = "",
    from_create_at: Union[Unset, int] = 0,
    from_update_at: Union[Unset, int] = 0,
    direction: Union[Unset, str] = "",
    skip_fetch_threads: Union[Unset, bool] = False,
    collapsed_threads: Union[Unset, bool] = False,
    collapsed_threads_extended: Union[Unset, bool] = False,
    updates_only: Union[Unset, bool] = False,
) -> Response[Union[AppError, PostList]]:
    """Get a thread

     Get a post and the rest of the posts in the same thread.
    ##### Permissions
    Must have `read_channel` permission for the channel the post is in or if the channel is public, have
    the `read_public_channels` permission for the team.

    Args:
        post_id (str):
        per_page (Union[Unset, int]):  Default: 0.
        from_post (Union[Unset, str]):  Default: ''.
        from_create_at (Union[Unset, int]):  Default: 0.
        from_update_at (Union[Unset, int]):  Default: 0.
        direction (Union[Unset, str]):  Default: ''.
        skip_fetch_threads (Union[Unset, bool]):  Default: False.
        collapsed_threads (Union[Unset, bool]):  Default: False.
        collapsed_threads_extended (Union[Unset, bool]):  Default: False.
        updates_only (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, PostList]]
    """

    kwargs = _get_kwargs(
        post_id=post_id,
        per_page=per_page,
        from_post=from_post,
        from_create_at=from_create_at,
        from_update_at=from_update_at,
        direction=direction,
        skip_fetch_threads=skip_fetch_threads,
        collapsed_threads=collapsed_threads,
        collapsed_threads_extended=collapsed_threads_extended,
        updates_only=updates_only,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    post_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    per_page: Union[Unset, int] = 0,
    from_post: Union[Unset, str] = "",
    from_create_at: Union[Unset, int] = 0,
    from_update_at: Union[Unset, int] = 0,
    direction: Union[Unset, str] = "",
    skip_fetch_threads: Union[Unset, bool] = False,
    collapsed_threads: Union[Unset, bool] = False,
    collapsed_threads_extended: Union[Unset, bool] = False,
    updates_only: Union[Unset, bool] = False,
) -> Optional[Union[AppError, PostList]]:
    """Get a thread

     Get a post and the rest of the posts in the same thread.
    ##### Permissions
    Must have `read_channel` permission for the channel the post is in or if the channel is public, have
    the `read_public_channels` permission for the team.

    Args:
        post_id (str):
        per_page (Union[Unset, int]):  Default: 0.
        from_post (Union[Unset, str]):  Default: ''.
        from_create_at (Union[Unset, int]):  Default: 0.
        from_update_at (Union[Unset, int]):  Default: 0.
        direction (Union[Unset, str]):  Default: ''.
        skip_fetch_threads (Union[Unset, bool]):  Default: False.
        collapsed_threads (Union[Unset, bool]):  Default: False.
        collapsed_threads_extended (Union[Unset, bool]):  Default: False.
        updates_only (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, PostList]
    """

    return sync_detailed(
        post_id=post_id,
        client=client,
        per_page=per_page,
        from_post=from_post,
        from_create_at=from_create_at,
        from_update_at=from_update_at,
        direction=direction,
        skip_fetch_threads=skip_fetch_threads,
        collapsed_threads=collapsed_threads,
        collapsed_threads_extended=collapsed_threads_extended,
        updates_only=updates_only,
    ).parsed


async def asyncio_detailed(
    post_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    per_page: Union[Unset, int] = 0,
    from_post: Union[Unset, str] = "",
    from_create_at: Union[Unset, int] = 0,
    from_update_at: Union[Unset, int] = 0,
    direction: Union[Unset, str] = "",
    skip_fetch_threads: Union[Unset, bool] = False,
    collapsed_threads: Union[Unset, bool] = False,
    collapsed_threads_extended: Union[Unset, bool] = False,
    updates_only: Union[Unset, bool] = False,
) -> Response[Union[AppError, PostList]]:
    """Get a thread

     Get a post and the rest of the posts in the same thread.
    ##### Permissions
    Must have `read_channel` permission for the channel the post is in or if the channel is public, have
    the `read_public_channels` permission for the team.

    Args:
        post_id (str):
        per_page (Union[Unset, int]):  Default: 0.
        from_post (Union[Unset, str]):  Default: ''.
        from_create_at (Union[Unset, int]):  Default: 0.
        from_update_at (Union[Unset, int]):  Default: 0.
        direction (Union[Unset, str]):  Default: ''.
        skip_fetch_threads (Union[Unset, bool]):  Default: False.
        collapsed_threads (Union[Unset, bool]):  Default: False.
        collapsed_threads_extended (Union[Unset, bool]):  Default: False.
        updates_only (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, PostList]]
    """

    kwargs = _get_kwargs(
        post_id=post_id,
        per_page=per_page,
        from_post=from_post,
        from_create_at=from_create_at,
        from_update_at=from_update_at,
        direction=direction,
        skip_fetch_threads=skip_fetch_threads,
        collapsed_threads=collapsed_threads,
        collapsed_threads_extended=collapsed_threads_extended,
        updates_only=updates_only,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    post_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    per_page: Union[Unset, int] = 0,
    from_post: Union[Unset, str] = "",
    from_create_at: Union[Unset, int] = 0,
    from_update_at: Union[Unset, int] = 0,
    direction: Union[Unset, str] = "",
    skip_fetch_threads: Union[Unset, bool] = False,
    collapsed_threads: Union[Unset, bool] = False,
    collapsed_threads_extended: Union[Unset, bool] = False,
    updates_only: Union[Unset, bool] = False,
) -> Optional[Union[AppError, PostList]]:
    """Get a thread

     Get a post and the rest of the posts in the same thread.
    ##### Permissions
    Must have `read_channel` permission for the channel the post is in or if the channel is public, have
    the `read_public_channels` permission for the team.

    Args:
        post_id (str):
        per_page (Union[Unset, int]):  Default: 0.
        from_post (Union[Unset, str]):  Default: ''.
        from_create_at (Union[Unset, int]):  Default: 0.
        from_update_at (Union[Unset, int]):  Default: 0.
        direction (Union[Unset, str]):  Default: ''.
        skip_fetch_threads (Union[Unset, bool]):  Default: False.
        collapsed_threads (Union[Unset, bool]):  Default: False.
        collapsed_threads_extended (Union[Unset, bool]):  Default: False.
        updates_only (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, PostList]
    """

    return (
        await asyncio_detailed(
            post_id=post_id,
            client=client,
            per_page=per_page,
            from_post=from_post,
            from_create_at=from_create_at,
            from_update_at=from_update_at,
            direction=direction,
            skip_fetch_threads=skip_fetch_threads,
            collapsed_threads=collapsed_threads,
            collapsed_threads_extended=collapsed_threads_extended,
            updates_only=updates_only,
        )
    ).parsed
