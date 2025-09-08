from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.status_ok import StatusOK
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    seconds: Union[Unset, str] = "3600",
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["seconds"] = seconds

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v4/server_busy",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, StatusOK]]:
    if response.status_code == 200:
        response_200 = StatusOK.from_dict(response.json())

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
) -> Response[Union[AppError, StatusOK]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    seconds: Union[Unset, str] = "3600",
) -> Response[Union[AppError, StatusOK]]:
    """Set the server busy (high load) flag

     Marks the server as currently having high load which disables non-critical services such as search,
    statuses and typing notifications.

    __Minimum server version__: 5.20

    ##### Permissions
    Must have `manage_system` permission.

    Args:
        seconds (Union[Unset, str]):  Default: '3600'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, StatusOK]]
    """

    kwargs = _get_kwargs(
        seconds=seconds,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    seconds: Union[Unset, str] = "3600",
) -> Optional[Union[AppError, StatusOK]]:
    """Set the server busy (high load) flag

     Marks the server as currently having high load which disables non-critical services such as search,
    statuses and typing notifications.

    __Minimum server version__: 5.20

    ##### Permissions
    Must have `manage_system` permission.

    Args:
        seconds (Union[Unset, str]):  Default: '3600'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, StatusOK]
    """

    return sync_detailed(
        client=client,
        seconds=seconds,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    seconds: Union[Unset, str] = "3600",
) -> Response[Union[AppError, StatusOK]]:
    """Set the server busy (high load) flag

     Marks the server as currently having high load which disables non-critical services such as search,
    statuses and typing notifications.

    __Minimum server version__: 5.20

    ##### Permissions
    Must have `manage_system` permission.

    Args:
        seconds (Union[Unset, str]):  Default: '3600'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, StatusOK]]
    """

    kwargs = _get_kwargs(
        seconds=seconds,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    seconds: Union[Unset, str] = "3600",
) -> Optional[Union[AppError, StatusOK]]:
    """Set the server busy (high load) flag

     Marks the server as currently having high load which disables non-critical services such as search,
    statuses and typing notifications.

    __Minimum server version__: 5.20

    ##### Permissions
    Must have `manage_system` permission.

    Args:
        seconds (Union[Unset, str]):  Default: '3600'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, StatusOK]
    """

    return (
        await asyncio_detailed(
            client=client,
            seconds=seconds,
        )
    ).parsed
