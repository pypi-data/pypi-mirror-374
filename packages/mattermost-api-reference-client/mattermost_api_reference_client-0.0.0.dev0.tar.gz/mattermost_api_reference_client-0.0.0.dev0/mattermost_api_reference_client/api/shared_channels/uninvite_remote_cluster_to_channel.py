from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.status_ok import StatusOK
from ...types import Response


def _get_kwargs(
    remote_id: str,
    channel_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v4/remotecluster/{remote_id}/channels/{channel_id}/uninvite",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, StatusOK]]:
    if response.status_code == 200:
        response_200 = StatusOK.from_dict(response.json())

        return response_200

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
) -> Response[Union[AppError, StatusOK]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    remote_id: str,
    channel_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, StatusOK]]:
    """Uninvites a remote cluster to a channel.

     Stops sharing a channel with a remote cluster. If the channel
    was not shared with the remote, calling this endpoint will
    have no effect.

    ##### Permissions
    `manage_shared_channels`

    Args:
        remote_id (str):
        channel_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, StatusOK]]
    """

    kwargs = _get_kwargs(
        remote_id=remote_id,
        channel_id=channel_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    remote_id: str,
    channel_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, StatusOK]]:
    """Uninvites a remote cluster to a channel.

     Stops sharing a channel with a remote cluster. If the channel
    was not shared with the remote, calling this endpoint will
    have no effect.

    ##### Permissions
    `manage_shared_channels`

    Args:
        remote_id (str):
        channel_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, StatusOK]
    """

    return sync_detailed(
        remote_id=remote_id,
        channel_id=channel_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    remote_id: str,
    channel_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, StatusOK]]:
    """Uninvites a remote cluster to a channel.

     Stops sharing a channel with a remote cluster. If the channel
    was not shared with the remote, calling this endpoint will
    have no effect.

    ##### Permissions
    `manage_shared_channels`

    Args:
        remote_id (str):
        channel_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, StatusOK]]
    """

    kwargs = _get_kwargs(
        remote_id=remote_id,
        channel_id=channel_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    remote_id: str,
    channel_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, StatusOK]]:
    """Uninvites a remote cluster to a channel.

     Stops sharing a channel with a remote cluster. If the channel
    was not shared with the remote, calling this endpoint will
    have no effect.

    ##### Permissions
    `manage_shared_channels`

    Args:
        remote_id (str):
        channel_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, StatusOK]
    """

    return (
        await asyncio_detailed(
            remote_id=remote_id,
            channel_id=channel_id,
            client=client,
        )
    ).parsed
