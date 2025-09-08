from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.create_post_ephemeral_body import CreatePostEphemeralBody
from ...models.post import Post
from ...types import Response


def _get_kwargs(
    *,
    body: CreatePostEphemeralBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v4/posts/ephemeral",
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
    body: CreatePostEphemeralBody,
) -> Response[Union[AppError, Post]]:
    """Create a ephemeral post

     Create a new ephemeral post in a channel.
    ##### Permissions
    Must have `create_post_ephemeral` permission (currently only given to system admin)

    Args:
        body (CreatePostEphemeralBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, Post]]
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
    body: CreatePostEphemeralBody,
) -> Optional[Union[AppError, Post]]:
    """Create a ephemeral post

     Create a new ephemeral post in a channel.
    ##### Permissions
    Must have `create_post_ephemeral` permission (currently only given to system admin)

    Args:
        body (CreatePostEphemeralBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, Post]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CreatePostEphemeralBody,
) -> Response[Union[AppError, Post]]:
    """Create a ephemeral post

     Create a new ephemeral post in a channel.
    ##### Permissions
    Must have `create_post_ephemeral` permission (currently only given to system admin)

    Args:
        body (CreatePostEphemeralBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, Post]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CreatePostEphemeralBody,
) -> Optional[Union[AppError, Post]]:
    """Create a ephemeral post

     Create a new ephemeral post in a channel.
    ##### Permissions
    Must have `create_post_ephemeral` permission (currently only given to system admin)

    Args:
        body (CreatePostEphemeralBody):

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
        )
    ).parsed
