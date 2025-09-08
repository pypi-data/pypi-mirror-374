from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.users_stats import UsersStats
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    in_team: Union[Unset, str] = UNSET,
    in_channel: Union[Unset, str] = UNSET,
    include_deleted: Union[Unset, bool] = UNSET,
    include_bots: Union[Unset, bool] = UNSET,
    roles: Union[Unset, str] = UNSET,
    channel_roles: Union[Unset, str] = UNSET,
    team_roles: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["in_team"] = in_team

    params["in_channel"] = in_channel

    params["include_deleted"] = include_deleted

    params["include_bots"] = include_bots

    params["roles"] = roles

    params["channel_roles"] = channel_roles

    params["team_roles"] = team_roles

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v4/users/stats/filtered",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, UsersStats]]:
    if response.status_code == 200:
        response_200 = UsersStats.from_dict(response.json())

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

    if response.status_code == 404:
        response_404 = AppError.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, UsersStats]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    in_team: Union[Unset, str] = UNSET,
    in_channel: Union[Unset, str] = UNSET,
    include_deleted: Union[Unset, bool] = UNSET,
    include_bots: Union[Unset, bool] = UNSET,
    roles: Union[Unset, str] = UNSET,
    channel_roles: Union[Unset, str] = UNSET,
    team_roles: Union[Unset, str] = UNSET,
) -> Response[Union[AppError, UsersStats]]:
    """Get total count of users in the system matching the specified filters

     Get a count of users in the system matching the specified filters.

    __Minimum server version__: 5.26

    ##### Permissions
    Must have `manage_system` permission.

    Args:
        in_team (Union[Unset, str]):
        in_channel (Union[Unset, str]):
        include_deleted (Union[Unset, bool]):
        include_bots (Union[Unset, bool]):
        roles (Union[Unset, str]):
        channel_roles (Union[Unset, str]):
        team_roles (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, UsersStats]]
    """

    kwargs = _get_kwargs(
        in_team=in_team,
        in_channel=in_channel,
        include_deleted=include_deleted,
        include_bots=include_bots,
        roles=roles,
        channel_roles=channel_roles,
        team_roles=team_roles,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    in_team: Union[Unset, str] = UNSET,
    in_channel: Union[Unset, str] = UNSET,
    include_deleted: Union[Unset, bool] = UNSET,
    include_bots: Union[Unset, bool] = UNSET,
    roles: Union[Unset, str] = UNSET,
    channel_roles: Union[Unset, str] = UNSET,
    team_roles: Union[Unset, str] = UNSET,
) -> Optional[Union[AppError, UsersStats]]:
    """Get total count of users in the system matching the specified filters

     Get a count of users in the system matching the specified filters.

    __Minimum server version__: 5.26

    ##### Permissions
    Must have `manage_system` permission.

    Args:
        in_team (Union[Unset, str]):
        in_channel (Union[Unset, str]):
        include_deleted (Union[Unset, bool]):
        include_bots (Union[Unset, bool]):
        roles (Union[Unset, str]):
        channel_roles (Union[Unset, str]):
        team_roles (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, UsersStats]
    """

    return sync_detailed(
        client=client,
        in_team=in_team,
        in_channel=in_channel,
        include_deleted=include_deleted,
        include_bots=include_bots,
        roles=roles,
        channel_roles=channel_roles,
        team_roles=team_roles,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    in_team: Union[Unset, str] = UNSET,
    in_channel: Union[Unset, str] = UNSET,
    include_deleted: Union[Unset, bool] = UNSET,
    include_bots: Union[Unset, bool] = UNSET,
    roles: Union[Unset, str] = UNSET,
    channel_roles: Union[Unset, str] = UNSET,
    team_roles: Union[Unset, str] = UNSET,
) -> Response[Union[AppError, UsersStats]]:
    """Get total count of users in the system matching the specified filters

     Get a count of users in the system matching the specified filters.

    __Minimum server version__: 5.26

    ##### Permissions
    Must have `manage_system` permission.

    Args:
        in_team (Union[Unset, str]):
        in_channel (Union[Unset, str]):
        include_deleted (Union[Unset, bool]):
        include_bots (Union[Unset, bool]):
        roles (Union[Unset, str]):
        channel_roles (Union[Unset, str]):
        team_roles (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, UsersStats]]
    """

    kwargs = _get_kwargs(
        in_team=in_team,
        in_channel=in_channel,
        include_deleted=include_deleted,
        include_bots=include_bots,
        roles=roles,
        channel_roles=channel_roles,
        team_roles=team_roles,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    in_team: Union[Unset, str] = UNSET,
    in_channel: Union[Unset, str] = UNSET,
    include_deleted: Union[Unset, bool] = UNSET,
    include_bots: Union[Unset, bool] = UNSET,
    roles: Union[Unset, str] = UNSET,
    channel_roles: Union[Unset, str] = UNSET,
    team_roles: Union[Unset, str] = UNSET,
) -> Optional[Union[AppError, UsersStats]]:
    """Get total count of users in the system matching the specified filters

     Get a count of users in the system matching the specified filters.

    __Minimum server version__: 5.26

    ##### Permissions
    Must have `manage_system` permission.

    Args:
        in_team (Union[Unset, str]):
        in_channel (Union[Unset, str]):
        include_deleted (Union[Unset, bool]):
        include_bots (Union[Unset, bool]):
        roles (Union[Unset, str]):
        channel_roles (Union[Unset, str]):
        team_roles (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, UsersStats]
    """

    return (
        await asyncio_detailed(
            client=client,
            in_team=in_team,
            in_channel=in_channel,
            include_deleted=include_deleted,
            include_bots=include_bots,
            roles=roles,
            channel_roles=channel_roles,
            team_roles=team_roles,
        )
    ).parsed
