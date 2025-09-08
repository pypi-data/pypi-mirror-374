from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.channel import Channel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    user_id: str,
    team_id: str,
    *,
    include_deleted: Union[Unset, bool] = False,
    last_delete_at: Union[Unset, int] = 0,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["include_deleted"] = include_deleted

    params["last_delete_at"] = last_delete_at

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v4/users/{user_id}/teams/{team_id}/channels",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, list["Channel"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Channel.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[Union[AppError, list["Channel"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    user_id: str,
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_deleted: Union[Unset, bool] = False,
    last_delete_at: Union[Unset, int] = 0,
) -> Response[Union[AppError, list["Channel"]]]:
    """Get channels for user

     Get all the channels on a team for a user.
    ##### Permissions
    Logged in as the user, or have `edit_other_users` permission, and `view_team` permission for the
    team.

    Args:
        user_id (str):
        team_id (str):
        include_deleted (Union[Unset, bool]):  Default: False.
        last_delete_at (Union[Unset, int]):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['Channel']]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        team_id=team_id,
        include_deleted=include_deleted,
        last_delete_at=last_delete_at,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    user_id: str,
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_deleted: Union[Unset, bool] = False,
    last_delete_at: Union[Unset, int] = 0,
) -> Optional[Union[AppError, list["Channel"]]]:
    """Get channels for user

     Get all the channels on a team for a user.
    ##### Permissions
    Logged in as the user, or have `edit_other_users` permission, and `view_team` permission for the
    team.

    Args:
        user_id (str):
        team_id (str):
        include_deleted (Union[Unset, bool]):  Default: False.
        last_delete_at (Union[Unset, int]):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['Channel']]
    """

    return sync_detailed(
        user_id=user_id,
        team_id=team_id,
        client=client,
        include_deleted=include_deleted,
        last_delete_at=last_delete_at,
    ).parsed


async def asyncio_detailed(
    user_id: str,
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_deleted: Union[Unset, bool] = False,
    last_delete_at: Union[Unset, int] = 0,
) -> Response[Union[AppError, list["Channel"]]]:
    """Get channels for user

     Get all the channels on a team for a user.
    ##### Permissions
    Logged in as the user, or have `edit_other_users` permission, and `view_team` permission for the
    team.

    Args:
        user_id (str):
        team_id (str):
        include_deleted (Union[Unset, bool]):  Default: False.
        last_delete_at (Union[Unset, int]):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['Channel']]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        team_id=team_id,
        include_deleted=include_deleted,
        last_delete_at=last_delete_at,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    user_id: str,
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_deleted: Union[Unset, bool] = False,
    last_delete_at: Union[Unset, int] = 0,
) -> Optional[Union[AppError, list["Channel"]]]:
    """Get channels for user

     Get all the channels on a team for a user.
    ##### Permissions
    Logged in as the user, or have `edit_other_users` permission, and `view_team` permission for the
    team.

    Args:
        user_id (str):
        team_id (str):
        include_deleted (Union[Unset, bool]):  Default: False.
        last_delete_at (Union[Unset, int]):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['Channel']]
    """

    return (
        await asyncio_detailed(
            user_id=user_id,
            team_id=team_id,
            client=client,
            include_deleted=include_deleted,
            last_delete_at=last_delete_at,
        )
    ).parsed
