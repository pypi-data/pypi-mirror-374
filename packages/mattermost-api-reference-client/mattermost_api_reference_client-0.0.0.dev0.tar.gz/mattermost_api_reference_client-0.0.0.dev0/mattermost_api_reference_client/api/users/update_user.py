from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.update_user_body import UpdateUserBody
from ...models.user import User
from ...types import Response


def _get_kwargs(
    user_id: str,
    *,
    body: UpdateUserBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/api/v4/users/{user_id}",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
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
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateUserBody,
) -> Response[Union[AppError, User]]:
    """Update a user

     Update a user by providing the user object. The fields that can be updated are defined in the
    request body, all other provided fields will be ignored. Any fields not included in the request body
    will be set to null or reverted to default values.
    ##### Permissions
    Must be logged in as the user being updated or have the `edit_other_users` permission.

    Args:
        user_id (str):
        body (UpdateUserBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, User]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateUserBody,
) -> Optional[Union[AppError, User]]:
    """Update a user

     Update a user by providing the user object. The fields that can be updated are defined in the
    request body, all other provided fields will be ignored. Any fields not included in the request body
    will be set to null or reverted to default values.
    ##### Permissions
    Must be logged in as the user being updated or have the `edit_other_users` permission.

    Args:
        user_id (str):
        body (UpdateUserBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, User]
    """

    return sync_detailed(
        user_id=user_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateUserBody,
) -> Response[Union[AppError, User]]:
    """Update a user

     Update a user by providing the user object. The fields that can be updated are defined in the
    request body, all other provided fields will be ignored. Any fields not included in the request body
    will be set to null or reverted to default values.
    ##### Permissions
    Must be logged in as the user being updated or have the `edit_other_users` permission.

    Args:
        user_id (str):
        body (UpdateUserBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, User]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateUserBody,
) -> Optional[Union[AppError, User]]:
    """Update a user

     Update a user by providing the user object. The fields that can be updated are defined in the
    request body, all other provided fields will be ignored. Any fields not included in the request body
    will be set to null or reverted to default values.
    ##### Permissions
    Must be logged in as the user being updated or have the `edit_other_users` permission.

    Args:
        user_id (str):
        body (UpdateUserBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, User]
    """

    return (
        await asyncio_detailed(
            user_id=user_id,
            client=client,
            body=body,
        )
    ).parsed
