from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.post_list import PostList
from ...types import UNSET, Response, Unset


def _get_kwargs(
    channel_id: str,
    *,
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
    since: Union[Unset, int] = UNSET,
    before: Union[Unset, str] = UNSET,
    after: Union[Unset, str] = UNSET,
    include_deleted: Union[Unset, bool] = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["per_page"] = per_page

    params["since"] = since

    params["before"] = before

    params["after"] = after

    params["include_deleted"] = include_deleted

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v4/channels/{channel_id}/posts",
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
    channel_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
    since: Union[Unset, int] = UNSET,
    before: Union[Unset, str] = UNSET,
    after: Union[Unset, str] = UNSET,
    include_deleted: Union[Unset, bool] = False,
) -> Response[Union[AppError, PostList]]:
    """Get posts for a channel

     Get a page of posts in a channel. Use the query parameters to modify the behaviour of this endpoint.
    The parameter `since` must not be used with any of `before`, `after`, `page`, and `per_page`
    parameters.
    If `since` is used, it will always return all posts modified since that time, ordered by their
    create time limited till 1000. A caveat with this parameter is that there is no guarantee that the
    returned posts will be consecutive. It is left to the clients to maintain state and fill any missing
    holes in the post order.
    ##### Permissions
    Must have `read_channel` permission for the channel.

    Args:
        channel_id (str):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.
        since (Union[Unset, int]):
        before (Union[Unset, str]):
        after (Union[Unset, str]):
        include_deleted (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, PostList]]
    """

    kwargs = _get_kwargs(
        channel_id=channel_id,
        page=page,
        per_page=per_page,
        since=since,
        before=before,
        after=after,
        include_deleted=include_deleted,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    channel_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
    since: Union[Unset, int] = UNSET,
    before: Union[Unset, str] = UNSET,
    after: Union[Unset, str] = UNSET,
    include_deleted: Union[Unset, bool] = False,
) -> Optional[Union[AppError, PostList]]:
    """Get posts for a channel

     Get a page of posts in a channel. Use the query parameters to modify the behaviour of this endpoint.
    The parameter `since` must not be used with any of `before`, `after`, `page`, and `per_page`
    parameters.
    If `since` is used, it will always return all posts modified since that time, ordered by their
    create time limited till 1000. A caveat with this parameter is that there is no guarantee that the
    returned posts will be consecutive. It is left to the clients to maintain state and fill any missing
    holes in the post order.
    ##### Permissions
    Must have `read_channel` permission for the channel.

    Args:
        channel_id (str):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.
        since (Union[Unset, int]):
        before (Union[Unset, str]):
        after (Union[Unset, str]):
        include_deleted (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, PostList]
    """

    return sync_detailed(
        channel_id=channel_id,
        client=client,
        page=page,
        per_page=per_page,
        since=since,
        before=before,
        after=after,
        include_deleted=include_deleted,
    ).parsed


async def asyncio_detailed(
    channel_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
    since: Union[Unset, int] = UNSET,
    before: Union[Unset, str] = UNSET,
    after: Union[Unset, str] = UNSET,
    include_deleted: Union[Unset, bool] = False,
) -> Response[Union[AppError, PostList]]:
    """Get posts for a channel

     Get a page of posts in a channel. Use the query parameters to modify the behaviour of this endpoint.
    The parameter `since` must not be used with any of `before`, `after`, `page`, and `per_page`
    parameters.
    If `since` is used, it will always return all posts modified since that time, ordered by their
    create time limited till 1000. A caveat with this parameter is that there is no guarantee that the
    returned posts will be consecutive. It is left to the clients to maintain state and fill any missing
    holes in the post order.
    ##### Permissions
    Must have `read_channel` permission for the channel.

    Args:
        channel_id (str):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.
        since (Union[Unset, int]):
        before (Union[Unset, str]):
        after (Union[Unset, str]):
        include_deleted (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, PostList]]
    """

    kwargs = _get_kwargs(
        channel_id=channel_id,
        page=page,
        per_page=per_page,
        since=since,
        before=before,
        after=after,
        include_deleted=include_deleted,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    channel_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
    since: Union[Unset, int] = UNSET,
    before: Union[Unset, str] = UNSET,
    after: Union[Unset, str] = UNSET,
    include_deleted: Union[Unset, bool] = False,
) -> Optional[Union[AppError, PostList]]:
    """Get posts for a channel

     Get a page of posts in a channel. Use the query parameters to modify the behaviour of this endpoint.
    The parameter `since` must not be used with any of `before`, `after`, `page`, and `per_page`
    parameters.
    If `since` is used, it will always return all posts modified since that time, ordered by their
    create time limited till 1000. A caveat with this parameter is that there is no guarantee that the
    returned posts will be consecutive. It is left to the clients to maintain state and fill any missing
    holes in the post order.
    ##### Permissions
    Must have `read_channel` permission for the channel.

    Args:
        channel_id (str):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.
        since (Union[Unset, int]):
        before (Union[Unset, str]):
        after (Union[Unset, str]):
        include_deleted (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, PostList]
    """

    return (
        await asyncio_detailed(
            channel_id=channel_id,
            client=client,
            page=page,
            per_page=per_page,
            since=since,
            before=before,
            after=after,
            include_deleted=include_deleted,
        )
    ).parsed
