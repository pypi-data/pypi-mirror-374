from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.can_user_direct_message_response_200 import CanUserDirectMessageResponse200
from ...types import Response


def _get_kwargs(
    user_id: str,
    other_user_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v4/sharedchannels/users/{user_id}/can_dm/{other_user_id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, CanUserDirectMessageResponse200]]:
    if response.status_code == 200:
        response_200 = CanUserDirectMessageResponse200.from_dict(response.json())

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
) -> Response[Union[AppError, CanUserDirectMessageResponse200]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    user_id: str,
    other_user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, CanUserDirectMessageResponse200]]:
    """Check if user can DM another user in shared channels context

     Checks if a user can send direct messages to another user, considering shared channel restrictions.
    This is specifically for shared channels where DMs require direct connections between clusters.

    __Minimum server version__: 10.11

    ##### Permissions
    Must be authenticated and have permission to view the user.

    Args:
        user_id (str):
        other_user_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, CanUserDirectMessageResponse200]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        other_user_id=other_user_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    user_id: str,
    other_user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, CanUserDirectMessageResponse200]]:
    """Check if user can DM another user in shared channels context

     Checks if a user can send direct messages to another user, considering shared channel restrictions.
    This is specifically for shared channels where DMs require direct connections between clusters.

    __Minimum server version__: 10.11

    ##### Permissions
    Must be authenticated and have permission to view the user.

    Args:
        user_id (str):
        other_user_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, CanUserDirectMessageResponse200]
    """

    return sync_detailed(
        user_id=user_id,
        other_user_id=other_user_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    user_id: str,
    other_user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, CanUserDirectMessageResponse200]]:
    """Check if user can DM another user in shared channels context

     Checks if a user can send direct messages to another user, considering shared channel restrictions.
    This is specifically for shared channels where DMs require direct connections between clusters.

    __Minimum server version__: 10.11

    ##### Permissions
    Must be authenticated and have permission to view the user.

    Args:
        user_id (str):
        other_user_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, CanUserDirectMessageResponse200]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        other_user_id=other_user_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    user_id: str,
    other_user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, CanUserDirectMessageResponse200]]:
    """Check if user can DM another user in shared channels context

     Checks if a user can send direct messages to another user, considering shared channel restrictions.
    This is specifically for shared channels where DMs require direct connections between clusters.

    __Minimum server version__: 10.11

    ##### Permissions
    Must be authenticated and have permission to view the user.

    Args:
        user_id (str):
        other_user_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, CanUserDirectMessageResponse200]
    """

    return (
        await asyncio_detailed(
            user_id=user_id,
            other_user_id=other_user_id,
            client=client,
        )
    ).parsed
