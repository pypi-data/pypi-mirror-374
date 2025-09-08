from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.channel import Channel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    team_name: str,
    channel_name: str,
    *,
    include_deleted: Union[Unset, bool] = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["include_deleted"] = include_deleted

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v4/teams/name/{team_name}/channels/name/{channel_name}",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, Channel]]:
    if response.status_code == 200:
        response_200 = Channel.from_dict(response.json())

        return response_200

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
) -> Response[Union[AppError, Channel]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    team_name: str,
    channel_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_deleted: Union[Unset, bool] = False,
) -> Response[Union[AppError, Channel]]:
    """Get a channel by name and team name

     Gets a channel from the provided team name and channel name strings.
    ##### Permissions
    `read_channel` permission for the channel.

    Args:
        team_name (str):
        channel_name (str):
        include_deleted (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, Channel]]
    """

    kwargs = _get_kwargs(
        team_name=team_name,
        channel_name=channel_name,
        include_deleted=include_deleted,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    team_name: str,
    channel_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_deleted: Union[Unset, bool] = False,
) -> Optional[Union[AppError, Channel]]:
    """Get a channel by name and team name

     Gets a channel from the provided team name and channel name strings.
    ##### Permissions
    `read_channel` permission for the channel.

    Args:
        team_name (str):
        channel_name (str):
        include_deleted (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, Channel]
    """

    return sync_detailed(
        team_name=team_name,
        channel_name=channel_name,
        client=client,
        include_deleted=include_deleted,
    ).parsed


async def asyncio_detailed(
    team_name: str,
    channel_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_deleted: Union[Unset, bool] = False,
) -> Response[Union[AppError, Channel]]:
    """Get a channel by name and team name

     Gets a channel from the provided team name and channel name strings.
    ##### Permissions
    `read_channel` permission for the channel.

    Args:
        team_name (str):
        channel_name (str):
        include_deleted (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, Channel]]
    """

    kwargs = _get_kwargs(
        team_name=team_name,
        channel_name=channel_name,
        include_deleted=include_deleted,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    team_name: str,
    channel_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_deleted: Union[Unset, bool] = False,
) -> Optional[Union[AppError, Channel]]:
    """Get a channel by name and team name

     Gets a channel from the provided team name and channel name strings.
    ##### Permissions
    `read_channel` permission for the channel.

    Args:
        team_name (str):
        channel_name (str):
        include_deleted (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, Channel]
    """

    return (
        await asyncio_detailed(
            team_name=team_name,
            channel_name=channel_name,
            client=client,
            include_deleted=include_deleted,
        )
    ).parsed
