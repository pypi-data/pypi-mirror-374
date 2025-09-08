from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.preference import Preference
from ...types import Response


def _get_kwargs(
    user_id: str,
    category: str,
    preference_name: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v4/users/{user_id}/preferences/{category}/name/{preference_name}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, Preference]]:
    if response.status_code == 200:
        response_200 = Preference.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = AppError.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = AppError.from_dict(response.json())

        return response_401

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, Preference]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    user_id: str,
    category: str,
    preference_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, Preference]]:
    """Get a specific user preference

     Gets a single preference for the current user with the given category and name.
    ##### Permissions
    Must be logged in as the user being updated or have the `edit_other_users` permission.

    Args:
        user_id (str):
        category (str):
        preference_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, Preference]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        category=category,
        preference_name=preference_name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    user_id: str,
    category: str,
    preference_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, Preference]]:
    """Get a specific user preference

     Gets a single preference for the current user with the given category and name.
    ##### Permissions
    Must be logged in as the user being updated or have the `edit_other_users` permission.

    Args:
        user_id (str):
        category (str):
        preference_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, Preference]
    """

    return sync_detailed(
        user_id=user_id,
        category=category,
        preference_name=preference_name,
        client=client,
    ).parsed


async def asyncio_detailed(
    user_id: str,
    category: str,
    preference_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, Preference]]:
    """Get a specific user preference

     Gets a single preference for the current user with the given category and name.
    ##### Permissions
    Must be logged in as the user being updated or have the `edit_other_users` permission.

    Args:
        user_id (str):
        category (str):
        preference_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, Preference]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        category=category,
        preference_name=preference_name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    user_id: str,
    category: str,
    preference_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, Preference]]:
    """Get a specific user preference

     Gets a single preference for the current user with the given category and name.
    ##### Permissions
    Must be logged in as the user being updated or have the `edit_other_users` permission.

    Args:
        user_id (str):
        category (str):
        preference_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, Preference]
    """

    return (
        await asyncio_detailed(
            user_id=user_id,
            category=category,
            preference_name=preference_name,
            client=client,
        )
    ).parsed
