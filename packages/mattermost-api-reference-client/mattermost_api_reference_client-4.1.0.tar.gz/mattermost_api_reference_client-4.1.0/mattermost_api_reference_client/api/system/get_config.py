from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.config import Config
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    remove_masked: Union[Unset, bool] = False,
    remove_defaults: Union[Unset, str] = "False",
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["remove_masked"] = remove_masked

    params["remove_defaults"] = remove_defaults

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v4/config",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, Config]]:
    if response.status_code == 200:
        response_200 = Config.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = AppError.from_dict(response.json())

        return response_400

    if response.status_code == 403:
        response_403 = AppError.from_dict(response.json())

        return response_403

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, Config]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    remove_masked: Union[Unset, bool] = False,
    remove_defaults: Union[Unset, str] = "False",
) -> Response[Union[AppError, Config]]:
    """Get configuration

     Retrieve the current server configuration
    ##### Permissions
    Must have `manage_system` permission.

    Args:
        remove_masked (Union[Unset, bool]):  Default: False.
        remove_defaults (Union[Unset, str]):  Default: 'False'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, Config]]
    """

    kwargs = _get_kwargs(
        remove_masked=remove_masked,
        remove_defaults=remove_defaults,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    remove_masked: Union[Unset, bool] = False,
    remove_defaults: Union[Unset, str] = "False",
) -> Optional[Union[AppError, Config]]:
    """Get configuration

     Retrieve the current server configuration
    ##### Permissions
    Must have `manage_system` permission.

    Args:
        remove_masked (Union[Unset, bool]):  Default: False.
        remove_defaults (Union[Unset, str]):  Default: 'False'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, Config]
    """

    return sync_detailed(
        client=client,
        remove_masked=remove_masked,
        remove_defaults=remove_defaults,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    remove_masked: Union[Unset, bool] = False,
    remove_defaults: Union[Unset, str] = "False",
) -> Response[Union[AppError, Config]]:
    """Get configuration

     Retrieve the current server configuration
    ##### Permissions
    Must have `manage_system` permission.

    Args:
        remove_masked (Union[Unset, bool]):  Default: False.
        remove_defaults (Union[Unset, str]):  Default: 'False'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, Config]]
    """

    kwargs = _get_kwargs(
        remove_masked=remove_masked,
        remove_defaults=remove_defaults,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    remove_masked: Union[Unset, bool] = False,
    remove_defaults: Union[Unset, str] = "False",
) -> Optional[Union[AppError, Config]]:
    """Get configuration

     Retrieve the current server configuration
    ##### Permissions
    Must have `manage_system` permission.

    Args:
        remove_masked (Union[Unset, bool]):  Default: False.
        remove_defaults (Union[Unset, str]):  Default: 'False'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, Config]
    """

    return (
        await asyncio_detailed(
            client=client,
            remove_masked=remove_masked,
            remove_defaults=remove_defaults,
        )
    ).parsed
