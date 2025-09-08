from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.get_groups_associated_to_channels_by_team_response_200 import (
    GetGroupsAssociatedToChannelsByTeamResponse200,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    team_id: str,
    *,
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
    filter_allow_reference: Union[Unset, bool] = False,
    paginate: Union[Unset, bool] = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["per_page"] = per_page

    params["filter_allow_reference"] = filter_allow_reference

    params["paginate"] = paginate

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v4/teams/{team_id}/groups_by_channels",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, GetGroupsAssociatedToChannelsByTeamResponse200]]:
    if response.status_code == 200:
        response_200 = GetGroupsAssociatedToChannelsByTeamResponse200.from_dict(response.json())

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

    if response.status_code == 500:
        response_500 = AppError.from_dict(response.json())

        return response_500

    if response.status_code == 501:
        response_501 = AppError.from_dict(response.json())

        return response_501

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, GetGroupsAssociatedToChannelsByTeamResponse200]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
    filter_allow_reference: Union[Unset, bool] = False,
    paginate: Union[Unset, bool] = False,
) -> Response[Union[AppError, GetGroupsAssociatedToChannelsByTeamResponse200]]:
    """Get team groups by channels

     Retrieve the set of groups associated with the channels in the given team grouped by channel.

    ##### Permissions
    Must have the `list_team_channels` permission.

    __Minimum server version__: 5.11

    Args:
        team_id (str):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.
        filter_allow_reference (Union[Unset, bool]):  Default: False.
        paginate (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, GetGroupsAssociatedToChannelsByTeamResponse200]]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        page=page,
        per_page=per_page,
        filter_allow_reference=filter_allow_reference,
        paginate=paginate,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
    filter_allow_reference: Union[Unset, bool] = False,
    paginate: Union[Unset, bool] = False,
) -> Optional[Union[AppError, GetGroupsAssociatedToChannelsByTeamResponse200]]:
    """Get team groups by channels

     Retrieve the set of groups associated with the channels in the given team grouped by channel.

    ##### Permissions
    Must have the `list_team_channels` permission.

    __Minimum server version__: 5.11

    Args:
        team_id (str):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.
        filter_allow_reference (Union[Unset, bool]):  Default: False.
        paginate (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, GetGroupsAssociatedToChannelsByTeamResponse200]
    """

    return sync_detailed(
        team_id=team_id,
        client=client,
        page=page,
        per_page=per_page,
        filter_allow_reference=filter_allow_reference,
        paginate=paginate,
    ).parsed


async def asyncio_detailed(
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
    filter_allow_reference: Union[Unset, bool] = False,
    paginate: Union[Unset, bool] = False,
) -> Response[Union[AppError, GetGroupsAssociatedToChannelsByTeamResponse200]]:
    """Get team groups by channels

     Retrieve the set of groups associated with the channels in the given team grouped by channel.

    ##### Permissions
    Must have the `list_team_channels` permission.

    __Minimum server version__: 5.11

    Args:
        team_id (str):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.
        filter_allow_reference (Union[Unset, bool]):  Default: False.
        paginate (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, GetGroupsAssociatedToChannelsByTeamResponse200]]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        page=page,
        per_page=per_page,
        filter_allow_reference=filter_allow_reference,
        paginate=paginate,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
    filter_allow_reference: Union[Unset, bool] = False,
    paginate: Union[Unset, bool] = False,
) -> Optional[Union[AppError, GetGroupsAssociatedToChannelsByTeamResponse200]]:
    """Get team groups by channels

     Retrieve the set of groups associated with the channels in the given team grouped by channel.

    ##### Permissions
    Must have the `list_team_channels` permission.

    __Minimum server version__: 5.11

    Args:
        team_id (str):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.
        filter_allow_reference (Union[Unset, bool]):  Default: False.
        paginate (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, GetGroupsAssociatedToChannelsByTeamResponse200]
    """

    return (
        await asyncio_detailed(
            team_id=team_id,
            client=client,
            page=page,
            per_page=per_page,
            filter_allow_reference=filter_allow_reference,
            paginate=paginate,
        )
    ).parsed
