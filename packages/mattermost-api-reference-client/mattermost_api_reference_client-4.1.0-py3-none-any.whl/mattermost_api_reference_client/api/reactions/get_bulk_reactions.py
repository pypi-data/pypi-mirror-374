from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.post_id_to_reactions_map import PostIdToReactionsMap
from ...types import Response


def _get_kwargs(
    *,
    body: list[str],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v4/posts/ids/reactions",
    }

    _kwargs["json"] = body

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, PostIdToReactionsMap]]:
    if response.status_code == 200:
        response_200 = PostIdToReactionsMap.from_dict(response.json())

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
) -> Response[Union[AppError, PostIdToReactionsMap]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: list[str],
) -> Response[Union[AppError, PostIdToReactionsMap]]:
    """Bulk get the reaction for posts

     Get a list of reactions made by all users to a given post.
    ##### Permissions
    Must have `read_channel` permission for the channel the post is in.

    __Minimum server version__: 5.8

    Args:
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, PostIdToReactionsMap]]
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
    body: list[str],
) -> Optional[Union[AppError, PostIdToReactionsMap]]:
    """Bulk get the reaction for posts

     Get a list of reactions made by all users to a given post.
    ##### Permissions
    Must have `read_channel` permission for the channel the post is in.

    __Minimum server version__: 5.8

    Args:
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, PostIdToReactionsMap]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: list[str],
) -> Response[Union[AppError, PostIdToReactionsMap]]:
    """Bulk get the reaction for posts

     Get a list of reactions made by all users to a given post.
    ##### Permissions
    Must have `read_channel` permission for the channel the post is in.

    __Minimum server version__: 5.8

    Args:
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, PostIdToReactionsMap]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: list[str],
) -> Optional[Union[AppError, PostIdToReactionsMap]]:
    """Bulk get the reaction for posts

     Get a list of reactions made by all users to a given post.
    ##### Permissions
    Must have `read_channel` permission for the channel the post is in.

    __Minimum server version__: 5.8

    Args:
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, PostIdToReactionsMap]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
