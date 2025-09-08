from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.post import Post
from ...types import UNSET, Response, Unset


def _get_kwargs(
    post_id: str,
    *,
    include_deleted: Union[Unset, bool] = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["include_deleted"] = include_deleted

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v4/posts/{post_id}",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, Post]]:
    if response.status_code == 200:
        response_200 = Post.from_dict(response.json())

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
) -> Response[Union[AppError, Post]]:
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
    include_deleted: Union[Unset, bool] = False,
) -> Response[Union[AppError, Post]]:
    """Get a post

     Get a single post.
    ##### Permissions
    Must have `read_channel` permission for the channel the post is in or if the channel is public, have
    the `read_public_channels` permission for the team.

    Args:
        post_id (str):
        include_deleted (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, Post]]
    """

    kwargs = _get_kwargs(
        post_id=post_id,
        include_deleted=include_deleted,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    post_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_deleted: Union[Unset, bool] = False,
) -> Optional[Union[AppError, Post]]:
    """Get a post

     Get a single post.
    ##### Permissions
    Must have `read_channel` permission for the channel the post is in or if the channel is public, have
    the `read_public_channels` permission for the team.

    Args:
        post_id (str):
        include_deleted (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, Post]
    """

    return sync_detailed(
        post_id=post_id,
        client=client,
        include_deleted=include_deleted,
    ).parsed


async def asyncio_detailed(
    post_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_deleted: Union[Unset, bool] = False,
) -> Response[Union[AppError, Post]]:
    """Get a post

     Get a single post.
    ##### Permissions
    Must have `read_channel` permission for the channel the post is in or if the channel is public, have
    the `read_public_channels` permission for the team.

    Args:
        post_id (str):
        include_deleted (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, Post]]
    """

    kwargs = _get_kwargs(
        post_id=post_id,
        include_deleted=include_deleted,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    post_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_deleted: Union[Unset, bool] = False,
) -> Optional[Union[AppError, Post]]:
    """Get a post

     Get a single post.
    ##### Permissions
    Must have `read_channel` permission for the channel the post is in or if the channel is public, have
    the `read_public_channels` permission for the team.

    Args:
        post_id (str):
        include_deleted (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, Post]
    """

    return (
        await asyncio_detailed(
            post_id=post_id,
            client=client,
            include_deleted=include_deleted,
        )
    ).parsed
