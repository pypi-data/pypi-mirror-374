from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.group_syncable_team import GroupSyncableTeam
from ...types import Response


def _get_kwargs(
    group_id: str,
    team_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v4/groups/{group_id}/teams/{team_id}/link",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, GroupSyncableTeam]]:
    if response.status_code == 201:
        response_201 = GroupSyncableTeam.from_dict(response.json())

        return response_201

    if response.status_code == 400:
        response_400 = AppError.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = AppError.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = AppError.from_dict(response.json())

        return response_403

    if response.status_code == 501:
        response_501 = AppError.from_dict(response.json())

        return response_501

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, GroupSyncableTeam]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    group_id: str,
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, GroupSyncableTeam]]:
    """Link a team to a group

     Link a team to a group
    ##### Permissions
    Must have `manage_team` permission.

    __Minimum server version__: 5.11

    Args:
        group_id (str):
        team_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, GroupSyncableTeam]]
    """

    kwargs = _get_kwargs(
        group_id=group_id,
        team_id=team_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    group_id: str,
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, GroupSyncableTeam]]:
    """Link a team to a group

     Link a team to a group
    ##### Permissions
    Must have `manage_team` permission.

    __Minimum server version__: 5.11

    Args:
        group_id (str):
        team_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, GroupSyncableTeam]
    """

    return sync_detailed(
        group_id=group_id,
        team_id=team_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    group_id: str,
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, GroupSyncableTeam]]:
    """Link a team to a group

     Link a team to a group
    ##### Permissions
    Must have `manage_team` permission.

    __Minimum server version__: 5.11

    Args:
        group_id (str):
        team_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, GroupSyncableTeam]]
    """

    kwargs = _get_kwargs(
        group_id=group_id,
        team_id=team_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    group_id: str,
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, GroupSyncableTeam]]:
    """Link a team to a group

     Link a team to a group
    ##### Permissions
    Must have `manage_team` permission.

    __Minimum server version__: 5.11

    Args:
        group_id (str):
        team_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, GroupSyncableTeam]
    """

    return (
        await asyncio_detailed(
            group_id=group_id,
            team_id=team_id,
            client=client,
        )
    ).parsed
