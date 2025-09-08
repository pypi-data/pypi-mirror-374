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
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v4/users/{user_id}/preferences/{category}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, list["Preference"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Preference.from_dict(response_200_item_data)

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
) -> Response[Union[AppError, list["Preference"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    user_id: str,
    category: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, list["Preference"]]]:
    """List a user's preferences by category

     Lists the current user's stored preferences in the given category.
    ##### Permissions
    Must be logged in as the user being updated or have the `edit_other_users` permission.

    Args:
        user_id (str):
        category (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['Preference']]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        category=category,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    user_id: str,
    category: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, list["Preference"]]]:
    """List a user's preferences by category

     Lists the current user's stored preferences in the given category.
    ##### Permissions
    Must be logged in as the user being updated or have the `edit_other_users` permission.

    Args:
        user_id (str):
        category (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['Preference']]
    """

    return sync_detailed(
        user_id=user_id,
        category=category,
        client=client,
    ).parsed


async def asyncio_detailed(
    user_id: str,
    category: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, list["Preference"]]]:
    """List a user's preferences by category

     Lists the current user's stored preferences in the given category.
    ##### Permissions
    Must be logged in as the user being updated or have the `edit_other_users` permission.

    Args:
        user_id (str):
        category (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['Preference']]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        category=category,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    user_id: str,
    category: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, list["Preference"]]]:
    """List a user's preferences by category

     Lists the current user's stored preferences in the given category.
    ##### Permissions
    Must be logged in as the user being updated or have the `edit_other_users` permission.

    Args:
        user_id (str):
        category (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['Preference']]
    """

    return (
        await asyncio_detailed(
            user_id=user_id,
            category=category,
            client=client,
        )
    ).parsed
