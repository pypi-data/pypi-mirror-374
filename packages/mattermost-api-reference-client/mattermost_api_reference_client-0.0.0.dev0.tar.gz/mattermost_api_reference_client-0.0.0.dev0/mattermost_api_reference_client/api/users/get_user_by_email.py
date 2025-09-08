from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.user import User
from ...types import Response


def _get_kwargs(
    email: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v4/users/email/{email}",
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
) -> Response[Union[AppError, User]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    email: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, User]]:
    """Get a user by email

     Get a user object by providing a user email. Sensitive information will be sanitized out.
    ##### Permissions
    Requires an active session and for the current session to be able to view another user's email based
    on the server's privacy settings.

    Args:
        email (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, User]]
    """

    kwargs = _get_kwargs(
        email=email,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    email: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, User]]:
    """Get a user by email

     Get a user object by providing a user email. Sensitive information will be sanitized out.
    ##### Permissions
    Requires an active session and for the current session to be able to view another user's email based
    on the server's privacy settings.

    Args:
        email (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, User]
    """

    return sync_detailed(
        email=email,
        client=client,
    ).parsed


async def asyncio_detailed(
    email: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, User]]:
    """Get a user by email

     Get a user object by providing a user email. Sensitive information will be sanitized out.
    ##### Permissions
    Requires an active session and for the current session to be able to view another user's email based
    on the server's privacy settings.

    Args:
        email (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, User]]
    """

    kwargs = _get_kwargs(
        email=email,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    email: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, User]]:
    """Get a user by email

     Get a user object by providing a user email. Sensitive information will be sanitized out.
    ##### Permissions
    Requires an active session and for the current session to be able to view another user's email based
    on the server's privacy settings.

    Args:
        email (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, User]
    """

    return (
        await asyncio_detailed(
            email=email,
            client=client,
        )
    ).parsed
