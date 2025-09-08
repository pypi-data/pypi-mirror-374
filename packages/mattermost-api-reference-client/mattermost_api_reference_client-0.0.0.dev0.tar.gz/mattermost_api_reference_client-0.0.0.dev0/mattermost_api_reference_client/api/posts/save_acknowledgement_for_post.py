from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.post_acknowledgement import PostAcknowledgement
from ...types import Response


def _get_kwargs(
    user_id: str,
    post_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v4/users/{user_id}/posts/{post_id}/ack",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, PostAcknowledgement]]:
    if response.status_code == 200:
        response_200 = PostAcknowledgement.from_dict(response.json())

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

    if response.status_code == 404:
        response_404 = AppError.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, PostAcknowledgement]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    user_id: str,
    post_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, PostAcknowledgement]]:
    """Acknowledge a post

     Acknowledge a post that has a request for acknowledgements.
    ##### Permissions
    Must have `read_channel` permission for the channel the post is in.<br/> Must be logged in as the
    user or have `edit_other_users` permission.

    __Minimum server version__: 7.7

    Args:
        user_id (str):
        post_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, PostAcknowledgement]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        post_id=post_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    user_id: str,
    post_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, PostAcknowledgement]]:
    """Acknowledge a post

     Acknowledge a post that has a request for acknowledgements.
    ##### Permissions
    Must have `read_channel` permission for the channel the post is in.<br/> Must be logged in as the
    user or have `edit_other_users` permission.

    __Minimum server version__: 7.7

    Args:
        user_id (str):
        post_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, PostAcknowledgement]
    """

    return sync_detailed(
        user_id=user_id,
        post_id=post_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    user_id: str,
    post_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, PostAcknowledgement]]:
    """Acknowledge a post

     Acknowledge a post that has a request for acknowledgements.
    ##### Permissions
    Must have `read_channel` permission for the channel the post is in.<br/> Must be logged in as the
    user or have `edit_other_users` permission.

    __Minimum server version__: 7.7

    Args:
        user_id (str):
        post_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, PostAcknowledgement]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        post_id=post_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    user_id: str,
    post_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, PostAcknowledgement]]:
    """Acknowledge a post

     Acknowledge a post that has a request for acknowledgements.
    ##### Permissions
    Must have `read_channel` permission for the channel the post is in.<br/> Must be logged in as the
    user or have `edit_other_users` permission.

    __Minimum server version__: 7.7

    Args:
        user_id (str):
        post_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, PostAcknowledgement]
    """

    return (
        await asyncio_detailed(
            user_id=user_id,
            post_id=post_id,
            client=client,
        )
    ).parsed
