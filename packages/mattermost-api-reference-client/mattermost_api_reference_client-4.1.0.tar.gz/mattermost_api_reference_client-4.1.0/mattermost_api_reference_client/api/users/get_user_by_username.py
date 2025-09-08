from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.user import User
from ...types import Response


def _get_kwargs(
    username: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v4/users/username/{username}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, User]]:
    if response.status_code == 200:
        response_200 = User.from_dict(response.json())

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
) -> Response[Union[AppError, User]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    username: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, User]]:
    """Get a user by username

     Get a user object by providing a username. Sensitive information will be sanitized out.
    ##### Permissions
    Requires an active session but no other permissions.

    Args:
        username (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, User]]
    """

    kwargs = _get_kwargs(
        username=username,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    username: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, User]]:
    """Get a user by username

     Get a user object by providing a username. Sensitive information will be sanitized out.
    ##### Permissions
    Requires an active session but no other permissions.

    Args:
        username (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, User]
    """

    return sync_detailed(
        username=username,
        client=client,
    ).parsed


async def asyncio_detailed(
    username: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, User]]:
    """Get a user by username

     Get a user object by providing a username. Sensitive information will be sanitized out.
    ##### Permissions
    Requires an active session but no other permissions.

    Args:
        username (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, User]]
    """

    kwargs = _get_kwargs(
        username=username,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    username: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, User]]:
    """Get a user by username

     Get a user object by providing a username. Sensitive information will be sanitized out.
    ##### Permissions
    Requires an active session but no other permissions.

    Args:
        username (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, User]
    """

    return (
        await asyncio_detailed(
            username=username,
            client=client,
        )
    ).parsed
