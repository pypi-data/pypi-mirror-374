from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.regen_command_token_response_200 import RegenCommandTokenResponse200
from ...types import Response


def _get_kwargs(
    command_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/api/v4/commands/{command_id}/regen_token",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, RegenCommandTokenResponse200]]:
    if response.status_code == 200:
        response_200 = RegenCommandTokenResponse200.from_dict(response.json())

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
) -> Response[Union[AppError, RegenCommandTokenResponse200]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    command_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, RegenCommandTokenResponse200]]:
    """Generate a new token

     Generate a new token for the command based on command id string.
    ##### Permissions
    Must have `manage_slash_commands` permission for the team the command is in.

    Args:
        command_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, RegenCommandTokenResponse200]]
    """

    kwargs = _get_kwargs(
        command_id=command_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    command_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, RegenCommandTokenResponse200]]:
    """Generate a new token

     Generate a new token for the command based on command id string.
    ##### Permissions
    Must have `manage_slash_commands` permission for the team the command is in.

    Args:
        command_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, RegenCommandTokenResponse200]
    """

    return sync_detailed(
        command_id=command_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    command_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, RegenCommandTokenResponse200]]:
    """Generate a new token

     Generate a new token for the command based on command id string.
    ##### Permissions
    Must have `manage_slash_commands` permission for the team the command is in.

    Args:
        command_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, RegenCommandTokenResponse200]]
    """

    kwargs = _get_kwargs(
        command_id=command_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    command_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, RegenCommandTokenResponse200]]:
    """Generate a new token

     Generate a new token for the command based on command id string.
    ##### Permissions
    Must have `manage_slash_commands` permission for the team the command is in.

    Args:
        command_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, RegenCommandTokenResponse200]
    """

    return (
        await asyncio_detailed(
            command_id=command_id,
            client=client,
        )
    ).parsed
