from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.channel_member_with_team_data import ChannelMemberWithTeamData
from ...types import UNSET, Response, Unset


def _get_kwargs(
    user_id: str,
    *,
    page: Union[Unset, int] = UNSET,
    per_page: Union[Unset, int] = 60,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["per_page"] = per_page

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v4/users/{user_id}/channel_members",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, list["ChannelMemberWithTeamData"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ChannelMemberWithTeamData.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    if response.status_code == 400:
        response_400 = AppError.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = AppError.from_dict(response.json())

        return response_401

    if response.status_code == 404:
        response_404 = AppError.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, list["ChannelMemberWithTeamData"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = UNSET,
    per_page: Union[Unset, int] = 60,
) -> Response[Union[AppError, list["ChannelMemberWithTeamData"]]]:
    """Get all channel members from all teams for a user

     Get all channel members from all teams for a user.

    __Minimum server version__: 6.2.0

    ##### Permissions
    Logged in as the user, or have `edit_other_users` permission.

    Args:
        user_id (str):
        page (Union[Unset, int]):
        per_page (Union[Unset, int]):  Default: 60.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['ChannelMemberWithTeamData']]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        page=page,
        per_page=per_page,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = UNSET,
    per_page: Union[Unset, int] = 60,
) -> Optional[Union[AppError, list["ChannelMemberWithTeamData"]]]:
    """Get all channel members from all teams for a user

     Get all channel members from all teams for a user.

    __Minimum server version__: 6.2.0

    ##### Permissions
    Logged in as the user, or have `edit_other_users` permission.

    Args:
        user_id (str):
        page (Union[Unset, int]):
        per_page (Union[Unset, int]):  Default: 60.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['ChannelMemberWithTeamData']]
    """

    return sync_detailed(
        user_id=user_id,
        client=client,
        page=page,
        per_page=per_page,
    ).parsed


async def asyncio_detailed(
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = UNSET,
    per_page: Union[Unset, int] = 60,
) -> Response[Union[AppError, list["ChannelMemberWithTeamData"]]]:
    """Get all channel members from all teams for a user

     Get all channel members from all teams for a user.

    __Minimum server version__: 6.2.0

    ##### Permissions
    Logged in as the user, or have `edit_other_users` permission.

    Args:
        user_id (str):
        page (Union[Unset, int]):
        per_page (Union[Unset, int]):  Default: 60.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['ChannelMemberWithTeamData']]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        page=page,
        per_page=per_page,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = UNSET,
    per_page: Union[Unset, int] = 60,
) -> Optional[Union[AppError, list["ChannelMemberWithTeamData"]]]:
    """Get all channel members from all teams for a user

     Get all channel members from all teams for a user.

    __Minimum server version__: 6.2.0

    ##### Permissions
    Logged in as the user, or have `edit_other_users` permission.

    Args:
        user_id (str):
        page (Union[Unset, int]):
        per_page (Union[Unset, int]):  Default: 60.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['ChannelMemberWithTeamData']]
    """

    return (
        await asyncio_detailed(
            user_id=user_id,
            client=client,
            page=page,
            per_page=per_page,
        )
    ).parsed
