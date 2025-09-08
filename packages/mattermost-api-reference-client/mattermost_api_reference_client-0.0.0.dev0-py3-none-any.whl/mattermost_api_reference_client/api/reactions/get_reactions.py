from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.reaction import Reaction
from ...types import Response


def _get_kwargs(
    post_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v4/posts/{post_id}/reactions",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, list["Reaction"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Reaction.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[Union[AppError, list["Reaction"]]]:
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
) -> Response[Union[AppError, list["Reaction"]]]:
    """Get a list of reactions to a post

     Get a list of reactions made by all users to a given post.
    ##### Permissions
    Must have `read_channel` permission for the channel the post is in.

    Args:
        post_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['Reaction']]]
    """

    kwargs = _get_kwargs(
        post_id=post_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    post_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, list["Reaction"]]]:
    """Get a list of reactions to a post

     Get a list of reactions made by all users to a given post.
    ##### Permissions
    Must have `read_channel` permission for the channel the post is in.

    Args:
        post_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['Reaction']]
    """

    return sync_detailed(
        post_id=post_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    post_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, list["Reaction"]]]:
    """Get a list of reactions to a post

     Get a list of reactions made by all users to a given post.
    ##### Permissions
    Must have `read_channel` permission for the channel the post is in.

    Args:
        post_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['Reaction']]]
    """

    kwargs = _get_kwargs(
        post_id=post_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    post_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, list["Reaction"]]]:
    """Get a list of reactions to a post

     Get a list of reactions made by all users to a given post.
    ##### Permissions
    Must have `read_channel` permission for the channel the post is in.

    Args:
        post_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['Reaction']]
    """

    return (
        await asyncio_detailed(
            post_id=post_id,
            client=client,
        )
    ).parsed
