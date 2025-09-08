from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.group import Group
from ...types import UNSET, Response, Unset


def _get_kwargs(
    team_id: str,
    *,
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
    filter_allow_reference: Union[Unset, bool] = False,
    include_member_count: Union[Unset, bool] = False,
    include_timezones: Union[Unset, bool] = False,
    include_total_count: Union[Unset, bool] = False,
    include_archived: Union[Unset, bool] = False,
    filter_archived: Union[Unset, bool] = False,
    filter_parent_team_permitted: Union[Unset, bool] = False,
    filter_has_member: Union[Unset, str] = UNSET,
    include_member_ids: Union[Unset, bool] = False,
    only_syncable_sources: Union[Unset, bool] = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["per_page"] = per_page

    params["filter_allow_reference"] = filter_allow_reference

    params["include_member_count"] = include_member_count

    params["include_timezones"] = include_timezones

    params["include_total_count"] = include_total_count

    params["include_archived"] = include_archived

    params["filter_archived"] = filter_archived

    params["filter_parent_team_permitted"] = filter_parent_team_permitted

    params["filter_has_member"] = filter_has_member

    params["include_member_ids"] = include_member_ids

    params["only_syncable_sources"] = only_syncable_sources

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v4/teams/{team_id}/groups",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, list["Group"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Group.from_dict(response_200_item_data)

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
) -> Response[Union[AppError, list["Group"]]]:
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
    include_member_count: Union[Unset, bool] = False,
    include_timezones: Union[Unset, bool] = False,
    include_total_count: Union[Unset, bool] = False,
    include_archived: Union[Unset, bool] = False,
    filter_archived: Union[Unset, bool] = False,
    filter_parent_team_permitted: Union[Unset, bool] = False,
    filter_has_member: Union[Unset, str] = UNSET,
    include_member_ids: Union[Unset, bool] = False,
    only_syncable_sources: Union[Unset, bool] = False,
) -> Response[Union[AppError, list["Group"]]]:
    """Get team groups

     Retrieve the list of groups associated with a given team.

    ##### Permissions
    Must have the `list_team_channels` permission.

    __Minimum server version__: 5.11

    Args:
        team_id (str):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.
        filter_allow_reference (Union[Unset, bool]):  Default: False.
        include_member_count (Union[Unset, bool]):  Default: False.
        include_timezones (Union[Unset, bool]):  Default: False.
        include_total_count (Union[Unset, bool]):  Default: False.
        include_archived (Union[Unset, bool]):  Default: False.
        filter_archived (Union[Unset, bool]):  Default: False.
        filter_parent_team_permitted (Union[Unset, bool]):  Default: False.
        filter_has_member (Union[Unset, str]):
        include_member_ids (Union[Unset, bool]):  Default: False.
        only_syncable_sources (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['Group']]]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        page=page,
        per_page=per_page,
        filter_allow_reference=filter_allow_reference,
        include_member_count=include_member_count,
        include_timezones=include_timezones,
        include_total_count=include_total_count,
        include_archived=include_archived,
        filter_archived=filter_archived,
        filter_parent_team_permitted=filter_parent_team_permitted,
        filter_has_member=filter_has_member,
        include_member_ids=include_member_ids,
        only_syncable_sources=only_syncable_sources,
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
    include_member_count: Union[Unset, bool] = False,
    include_timezones: Union[Unset, bool] = False,
    include_total_count: Union[Unset, bool] = False,
    include_archived: Union[Unset, bool] = False,
    filter_archived: Union[Unset, bool] = False,
    filter_parent_team_permitted: Union[Unset, bool] = False,
    filter_has_member: Union[Unset, str] = UNSET,
    include_member_ids: Union[Unset, bool] = False,
    only_syncable_sources: Union[Unset, bool] = False,
) -> Optional[Union[AppError, list["Group"]]]:
    """Get team groups

     Retrieve the list of groups associated with a given team.

    ##### Permissions
    Must have the `list_team_channels` permission.

    __Minimum server version__: 5.11

    Args:
        team_id (str):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.
        filter_allow_reference (Union[Unset, bool]):  Default: False.
        include_member_count (Union[Unset, bool]):  Default: False.
        include_timezones (Union[Unset, bool]):  Default: False.
        include_total_count (Union[Unset, bool]):  Default: False.
        include_archived (Union[Unset, bool]):  Default: False.
        filter_archived (Union[Unset, bool]):  Default: False.
        filter_parent_team_permitted (Union[Unset, bool]):  Default: False.
        filter_has_member (Union[Unset, str]):
        include_member_ids (Union[Unset, bool]):  Default: False.
        only_syncable_sources (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['Group']]
    """

    return sync_detailed(
        team_id=team_id,
        client=client,
        page=page,
        per_page=per_page,
        filter_allow_reference=filter_allow_reference,
        include_member_count=include_member_count,
        include_timezones=include_timezones,
        include_total_count=include_total_count,
        include_archived=include_archived,
        filter_archived=filter_archived,
        filter_parent_team_permitted=filter_parent_team_permitted,
        filter_has_member=filter_has_member,
        include_member_ids=include_member_ids,
        only_syncable_sources=only_syncable_sources,
    ).parsed


async def asyncio_detailed(
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
    filter_allow_reference: Union[Unset, bool] = False,
    include_member_count: Union[Unset, bool] = False,
    include_timezones: Union[Unset, bool] = False,
    include_total_count: Union[Unset, bool] = False,
    include_archived: Union[Unset, bool] = False,
    filter_archived: Union[Unset, bool] = False,
    filter_parent_team_permitted: Union[Unset, bool] = False,
    filter_has_member: Union[Unset, str] = UNSET,
    include_member_ids: Union[Unset, bool] = False,
    only_syncable_sources: Union[Unset, bool] = False,
) -> Response[Union[AppError, list["Group"]]]:
    """Get team groups

     Retrieve the list of groups associated with a given team.

    ##### Permissions
    Must have the `list_team_channels` permission.

    __Minimum server version__: 5.11

    Args:
        team_id (str):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.
        filter_allow_reference (Union[Unset, bool]):  Default: False.
        include_member_count (Union[Unset, bool]):  Default: False.
        include_timezones (Union[Unset, bool]):  Default: False.
        include_total_count (Union[Unset, bool]):  Default: False.
        include_archived (Union[Unset, bool]):  Default: False.
        filter_archived (Union[Unset, bool]):  Default: False.
        filter_parent_team_permitted (Union[Unset, bool]):  Default: False.
        filter_has_member (Union[Unset, str]):
        include_member_ids (Union[Unset, bool]):  Default: False.
        only_syncable_sources (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['Group']]]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        page=page,
        per_page=per_page,
        filter_allow_reference=filter_allow_reference,
        include_member_count=include_member_count,
        include_timezones=include_timezones,
        include_total_count=include_total_count,
        include_archived=include_archived,
        filter_archived=filter_archived,
        filter_parent_team_permitted=filter_parent_team_permitted,
        filter_has_member=filter_has_member,
        include_member_ids=include_member_ids,
        only_syncable_sources=only_syncable_sources,
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
    include_member_count: Union[Unset, bool] = False,
    include_timezones: Union[Unset, bool] = False,
    include_total_count: Union[Unset, bool] = False,
    include_archived: Union[Unset, bool] = False,
    filter_archived: Union[Unset, bool] = False,
    filter_parent_team_permitted: Union[Unset, bool] = False,
    filter_has_member: Union[Unset, str] = UNSET,
    include_member_ids: Union[Unset, bool] = False,
    only_syncable_sources: Union[Unset, bool] = False,
) -> Optional[Union[AppError, list["Group"]]]:
    """Get team groups

     Retrieve the list of groups associated with a given team.

    ##### Permissions
    Must have the `list_team_channels` permission.

    __Minimum server version__: 5.11

    Args:
        team_id (str):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.
        filter_allow_reference (Union[Unset, bool]):  Default: False.
        include_member_count (Union[Unset, bool]):  Default: False.
        include_timezones (Union[Unset, bool]):  Default: False.
        include_total_count (Union[Unset, bool]):  Default: False.
        include_archived (Union[Unset, bool]):  Default: False.
        filter_archived (Union[Unset, bool]):  Default: False.
        filter_parent_team_permitted (Union[Unset, bool]):  Default: False.
        filter_has_member (Union[Unset, str]):
        include_member_ids (Union[Unset, bool]):  Default: False.
        only_syncable_sources (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['Group']]
    """

    return (
        await asyncio_detailed(
            team_id=team_id,
            client=client,
            page=page,
            per_page=per_page,
            filter_allow_reference=filter_allow_reference,
            include_member_count=include_member_count,
            include_timezones=include_timezones,
            include_total_count=include_total_count,
            include_archived=include_archived,
            filter_archived=filter_archived,
            filter_parent_team_permitted=filter_parent_team_permitted,
            filter_has_member=filter_has_member,
            include_member_ids=include_member_ids,
            only_syncable_sources=only_syncable_sources,
        )
    ).parsed
