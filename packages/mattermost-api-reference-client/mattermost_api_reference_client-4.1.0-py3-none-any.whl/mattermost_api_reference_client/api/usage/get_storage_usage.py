from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.storage_usage import StorageUsage
from ...types import Response


def _get_kwargs() -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v4/usage/storage",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, StorageUsage]]:
    if response.status_code == 200:
        response_200 = StorageUsage.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = AppError.from_dict(response.json())

        return response_401

    if response.status_code == 500:
        response_500 = AppError.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, StorageUsage]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, StorageUsage]]:
    """Get the total file storage usage for the instance in bytes.

     Get the total file storage usage for the instance in bytes rounded down to the most significant
    digit. Example: returns 4000 instead of 4321
    ##### Permissions
    Must be authenticated.
    __Minimum server version__: 7.1

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, StorageUsage]]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, StorageUsage]]:
    """Get the total file storage usage for the instance in bytes.

     Get the total file storage usage for the instance in bytes rounded down to the most significant
    digit. Example: returns 4000 instead of 4321
    ##### Permissions
    Must be authenticated.
    __Minimum server version__: 7.1

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, StorageUsage]
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, StorageUsage]]:
    """Get the total file storage usage for the instance in bytes.

     Get the total file storage usage for the instance in bytes rounded down to the most significant
    digit. Example: returns 4000 instead of 4321
    ##### Permissions
    Must be authenticated.
    __Minimum server version__: 7.1

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, StorageUsage]]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, StorageUsage]]:
    """Get the total file storage usage for the instance in bytes.

     Get the total file storage usage for the instance in bytes rounded down to the most significant
    digit. Example: returns 4000 instead of 4321
    ##### Permissions
    Must be authenticated.
    __Minimum server version__: 7.1

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, StorageUsage]
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
