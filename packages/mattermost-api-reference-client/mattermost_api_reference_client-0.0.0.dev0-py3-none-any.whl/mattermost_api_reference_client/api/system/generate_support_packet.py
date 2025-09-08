from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    basic_server_logs: Union[Unset, bool] = UNSET,
    plugin_packets: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["basic_server_logs"] = basic_server_logs

    params["plugin_packets"] = plugin_packets

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v4/system/support_packet",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[AppError]:
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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[AppError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    basic_server_logs: Union[Unset, bool] = UNSET,
    plugin_packets: Union[Unset, str] = UNSET,
) -> Response[AppError]:
    """Download a zip file which contains helpful and useful information for troubleshooting your
    mattermost instance.

     Download a zip file which contains helpful and useful information for troubleshooting your
    mattermost instance.
    __Minimum server version: 5.32__
    ##### Permissions
    Must have any of the system console read permissions.
    ##### License
    Requires either a E10 or E20 license.

    Args:
        basic_server_logs (Union[Unset, bool]):
        plugin_packets (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AppError]
    """

    kwargs = _get_kwargs(
        basic_server_logs=basic_server_logs,
        plugin_packets=plugin_packets,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    basic_server_logs: Union[Unset, bool] = UNSET,
    plugin_packets: Union[Unset, str] = UNSET,
) -> Optional[AppError]:
    """Download a zip file which contains helpful and useful information for troubleshooting your
    mattermost instance.

     Download a zip file which contains helpful and useful information for troubleshooting your
    mattermost instance.
    __Minimum server version: 5.32__
    ##### Permissions
    Must have any of the system console read permissions.
    ##### License
    Requires either a E10 or E20 license.

    Args:
        basic_server_logs (Union[Unset, bool]):
        plugin_packets (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AppError
    """

    return sync_detailed(
        client=client,
        basic_server_logs=basic_server_logs,
        plugin_packets=plugin_packets,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    basic_server_logs: Union[Unset, bool] = UNSET,
    plugin_packets: Union[Unset, str] = UNSET,
) -> Response[AppError]:
    """Download a zip file which contains helpful and useful information for troubleshooting your
    mattermost instance.

     Download a zip file which contains helpful and useful information for troubleshooting your
    mattermost instance.
    __Minimum server version: 5.32__
    ##### Permissions
    Must have any of the system console read permissions.
    ##### License
    Requires either a E10 or E20 license.

    Args:
        basic_server_logs (Union[Unset, bool]):
        plugin_packets (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AppError]
    """

    kwargs = _get_kwargs(
        basic_server_logs=basic_server_logs,
        plugin_packets=plugin_packets,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    basic_server_logs: Union[Unset, bool] = UNSET,
    plugin_packets: Union[Unset, str] = UNSET,
) -> Optional[AppError]:
    """Download a zip file which contains helpful and useful information for troubleshooting your
    mattermost instance.

     Download a zip file which contains helpful and useful information for troubleshooting your
    mattermost instance.
    __Minimum server version: 5.32__
    ##### Permissions
    Must have any of the system console read permissions.
    ##### License
    Requires either a E10 or E20 license.

    Args:
        basic_server_logs (Union[Unset, bool]):
        plugin_packets (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AppError
    """

    return (
        await asyncio_detailed(
            client=client,
            basic_server_logs=basic_server_logs,
            plugin_packets=plugin_packets,
        )
    ).parsed
