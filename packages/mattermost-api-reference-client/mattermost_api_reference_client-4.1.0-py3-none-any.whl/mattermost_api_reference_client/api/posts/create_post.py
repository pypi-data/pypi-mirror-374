from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.create_post_body import CreatePostBody
from ...models.post import Post
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: CreatePostBody,
    set_online: Union[Unset, bool] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["set_online"] = set_online

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v4/posts",
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, Post]]:
    if response.status_code == 201:
        response_201 = Post.from_dict(response.json())

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
) -> Response[Union[AppError, Post]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CreatePostBody,
    set_online: Union[Unset, bool] = UNSET,
) -> Response[Union[AppError, Post]]:
    """Create a post

     Create a new post in a channel. To create the post as a comment on another post, provide `root_id`.
    ##### Permissions
    Must have `create_post` permission for the channel the post is being created in.

    Args:
        set_online (Union[Unset, bool]):
        body (CreatePostBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, Post]]
    """

    kwargs = _get_kwargs(
        body=body,
        set_online=set_online,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CreatePostBody,
    set_online: Union[Unset, bool] = UNSET,
) -> Optional[Union[AppError, Post]]:
    """Create a post

     Create a new post in a channel. To create the post as a comment on another post, provide `root_id`.
    ##### Permissions
    Must have `create_post` permission for the channel the post is being created in.

    Args:
        set_online (Union[Unset, bool]):
        body (CreatePostBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, Post]
    """

    return sync_detailed(
        client=client,
        body=body,
        set_online=set_online,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CreatePostBody,
    set_online: Union[Unset, bool] = UNSET,
) -> Response[Union[AppError, Post]]:
    """Create a post

     Create a new post in a channel. To create the post as a comment on another post, provide `root_id`.
    ##### Permissions
    Must have `create_post` permission for the channel the post is being created in.

    Args:
        set_online (Union[Unset, bool]):
        body (CreatePostBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, Post]]
    """

    kwargs = _get_kwargs(
        body=body,
        set_online=set_online,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CreatePostBody,
    set_online: Union[Unset, bool] = UNSET,
) -> Optional[Union[AppError, Post]]:
    """Create a post

     Create a new post in a channel. To create the post as a comment on another post, provide `root_id`.
    ##### Permissions
    Must have `create_post` permission for the channel the post is being created in.

    Args:
        set_online (Union[Unset, bool]):
        body (CreatePostBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, Post]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            set_online=set_online,
        )
    ).parsed
