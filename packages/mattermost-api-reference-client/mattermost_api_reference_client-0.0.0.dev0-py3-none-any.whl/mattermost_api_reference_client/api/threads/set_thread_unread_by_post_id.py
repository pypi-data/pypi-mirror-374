from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...types import Response


def _get_kwargs(
    user_id: str,
    team_id: str,
    thread_id: str,
    post_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v4/users/{user_id}/teams/{team_id}/threads/{thread_id}/set_unread/{post_id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, AppError]]:
    if response.status_code == 200:
        response_200 = cast(Any, None)
        return response_200

    if response.status_code == 400:
        response_400 = AppError.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = AppError.from_dict(response.json())

        return response_401

    if response.status_code == 404:
        response_404 = AppError.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, AppError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    user_id: str,
    team_id: str,
    thread_id: str,
    post_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[Any, AppError]]:
    """Mark a thread that user is following as unread based on a post id

     Mark a thread that user is following as unread

    __Minimum server version__: 6.7

    ##### Permissions
    Must have `read_channel` permission for the channel the thread is in or if the channel is public,
    have the `read_public_channels` permission for the team.

    Must have `edit_other_users` permission if the user is not the one marking the thread for himself.

    Args:
        user_id (str):
        team_id (str):
        thread_id (str):
        post_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, AppError]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        team_id=team_id,
        thread_id=thread_id,
        post_id=post_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    user_id: str,
    team_id: str,
    thread_id: str,
    post_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[Any, AppError]]:
    """Mark a thread that user is following as unread based on a post id

     Mark a thread that user is following as unread

    __Minimum server version__: 6.7

    ##### Permissions
    Must have `read_channel` permission for the channel the thread is in or if the channel is public,
    have the `read_public_channels` permission for the team.

    Must have `edit_other_users` permission if the user is not the one marking the thread for himself.

    Args:
        user_id (str):
        team_id (str):
        thread_id (str):
        post_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, AppError]
    """

    return sync_detailed(
        user_id=user_id,
        team_id=team_id,
        thread_id=thread_id,
        post_id=post_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    user_id: str,
    team_id: str,
    thread_id: str,
    post_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[Any, AppError]]:
    """Mark a thread that user is following as unread based on a post id

     Mark a thread that user is following as unread

    __Minimum server version__: 6.7

    ##### Permissions
    Must have `read_channel` permission for the channel the thread is in or if the channel is public,
    have the `read_public_channels` permission for the team.

    Must have `edit_other_users` permission if the user is not the one marking the thread for himself.

    Args:
        user_id (str):
        team_id (str):
        thread_id (str):
        post_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, AppError]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        team_id=team_id,
        thread_id=thread_id,
        post_id=post_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    user_id: str,
    team_id: str,
    thread_id: str,
    post_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[Any, AppError]]:
    """Mark a thread that user is following as unread based on a post id

     Mark a thread that user is following as unread

    __Minimum server version__: 6.7

    ##### Permissions
    Must have `read_channel` permission for the channel the thread is in or if the channel is public,
    have the `read_public_channels` permission for the team.

    Must have `edit_other_users` permission if the user is not the one marking the thread for himself.

    Args:
        user_id (str):
        team_id (str):
        thread_id (str):
        post_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, AppError]
    """

    return (
        await asyncio_detailed(
            user_id=user_id,
            team_id=team_id,
            thread_id=thread_id,
            post_id=post_id,
            client=client,
        )
    ).parsed
