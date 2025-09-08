from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.list_playbook_runs_direction import ListPlaybookRunsDirection
from ...models.list_playbook_runs_sort import ListPlaybookRunsSort
from ...models.list_playbook_runs_statuses_item import ListPlaybookRunsStatusesItem
from ...models.playbook_run_list import PlaybookRunList
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    team_id: str,
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 1000,
    sort: Union[Unset, ListPlaybookRunsSort] = ListPlaybookRunsSort.CREATE_AT,
    direction: Union[Unset, ListPlaybookRunsDirection] = ListPlaybookRunsDirection.DESC,
    statuses: Union[Unset, list[ListPlaybookRunsStatusesItem]] = UNSET,
    owner_user_id: Union[Unset, str] = UNSET,
    participant_id: Union[Unset, str] = UNSET,
    search_term: Union[Unset, str] = UNSET,
    channel_id: Union[Unset, str] = UNSET,
    omit_ended: Union[Unset, bool] = False,
    since: Union[Unset, int] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["team_id"] = team_id

    params["page"] = page

    params["per_page"] = per_page

    json_sort: Union[Unset, str] = UNSET
    if not isinstance(sort, Unset):
        json_sort = sort.value

    params["sort"] = json_sort

    json_direction: Union[Unset, str] = UNSET
    if not isinstance(direction, Unset):
        json_direction = direction.value

    params["direction"] = json_direction

    json_statuses: Union[Unset, list[str]] = UNSET
    if not isinstance(statuses, Unset):
        json_statuses = []
        for statuses_item_data in statuses:
            statuses_item = statuses_item_data.value
            json_statuses.append(statuses_item)

    params["statuses"] = json_statuses

    params["owner_user_id"] = owner_user_id

    params["participant_id"] = participant_id

    params["search_term"] = search_term

    params["channel_id"] = channel_id

    params["omit_ended"] = omit_ended

    params["since"] = since

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/plugins/playbooks/api/v0/runs",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Error, PlaybookRunList]]:
    if response.status_code == 200:
        response_200 = PlaybookRunList.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if response.status_code == 403:
        response_403 = Error.from_dict(response.json())

        return response_403

    if response.status_code == 500:
        response_500 = Error.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Error, PlaybookRunList]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    team_id: str,
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 1000,
    sort: Union[Unset, ListPlaybookRunsSort] = ListPlaybookRunsSort.CREATE_AT,
    direction: Union[Unset, ListPlaybookRunsDirection] = ListPlaybookRunsDirection.DESC,
    statuses: Union[Unset, list[ListPlaybookRunsStatusesItem]] = UNSET,
    owner_user_id: Union[Unset, str] = UNSET,
    participant_id: Union[Unset, str] = UNSET,
    search_term: Union[Unset, str] = UNSET,
    channel_id: Union[Unset, str] = UNSET,
    omit_ended: Union[Unset, bool] = False,
    since: Union[Unset, int] = UNSET,
) -> Response[Union[Error, PlaybookRunList]]:
    """List all playbook runs

     Retrieve a paged list of playbook runs, filtered by team, status, owner, name and/or members, and
    sorted by ID, name, status, creation date, end date, team or owner ID.

    Args:
        team_id (str):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 1000.
        sort (Union[Unset, ListPlaybookRunsSort]):  Default: ListPlaybookRunsSort.CREATE_AT.
        direction (Union[Unset, ListPlaybookRunsDirection]):  Default:
            ListPlaybookRunsDirection.DESC.
        statuses (Union[Unset, list[ListPlaybookRunsStatusesItem]]):
        owner_user_id (Union[Unset, str]):
        participant_id (Union[Unset, str]):
        search_term (Union[Unset, str]):
        channel_id (Union[Unset, str]):
        omit_ended (Union[Unset, bool]):  Default: False.
        since (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, PlaybookRunList]]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        page=page,
        per_page=per_page,
        sort=sort,
        direction=direction,
        statuses=statuses,
        owner_user_id=owner_user_id,
        participant_id=participant_id,
        search_term=search_term,
        channel_id=channel_id,
        omit_ended=omit_ended,
        since=since,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    team_id: str,
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 1000,
    sort: Union[Unset, ListPlaybookRunsSort] = ListPlaybookRunsSort.CREATE_AT,
    direction: Union[Unset, ListPlaybookRunsDirection] = ListPlaybookRunsDirection.DESC,
    statuses: Union[Unset, list[ListPlaybookRunsStatusesItem]] = UNSET,
    owner_user_id: Union[Unset, str] = UNSET,
    participant_id: Union[Unset, str] = UNSET,
    search_term: Union[Unset, str] = UNSET,
    channel_id: Union[Unset, str] = UNSET,
    omit_ended: Union[Unset, bool] = False,
    since: Union[Unset, int] = UNSET,
) -> Optional[Union[Error, PlaybookRunList]]:
    """List all playbook runs

     Retrieve a paged list of playbook runs, filtered by team, status, owner, name and/or members, and
    sorted by ID, name, status, creation date, end date, team or owner ID.

    Args:
        team_id (str):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 1000.
        sort (Union[Unset, ListPlaybookRunsSort]):  Default: ListPlaybookRunsSort.CREATE_AT.
        direction (Union[Unset, ListPlaybookRunsDirection]):  Default:
            ListPlaybookRunsDirection.DESC.
        statuses (Union[Unset, list[ListPlaybookRunsStatusesItem]]):
        owner_user_id (Union[Unset, str]):
        participant_id (Union[Unset, str]):
        search_term (Union[Unset, str]):
        channel_id (Union[Unset, str]):
        omit_ended (Union[Unset, bool]):  Default: False.
        since (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, PlaybookRunList]
    """

    return sync_detailed(
        client=client,
        team_id=team_id,
        page=page,
        per_page=per_page,
        sort=sort,
        direction=direction,
        statuses=statuses,
        owner_user_id=owner_user_id,
        participant_id=participant_id,
        search_term=search_term,
        channel_id=channel_id,
        omit_ended=omit_ended,
        since=since,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    team_id: str,
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 1000,
    sort: Union[Unset, ListPlaybookRunsSort] = ListPlaybookRunsSort.CREATE_AT,
    direction: Union[Unset, ListPlaybookRunsDirection] = ListPlaybookRunsDirection.DESC,
    statuses: Union[Unset, list[ListPlaybookRunsStatusesItem]] = UNSET,
    owner_user_id: Union[Unset, str] = UNSET,
    participant_id: Union[Unset, str] = UNSET,
    search_term: Union[Unset, str] = UNSET,
    channel_id: Union[Unset, str] = UNSET,
    omit_ended: Union[Unset, bool] = False,
    since: Union[Unset, int] = UNSET,
) -> Response[Union[Error, PlaybookRunList]]:
    """List all playbook runs

     Retrieve a paged list of playbook runs, filtered by team, status, owner, name and/or members, and
    sorted by ID, name, status, creation date, end date, team or owner ID.

    Args:
        team_id (str):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 1000.
        sort (Union[Unset, ListPlaybookRunsSort]):  Default: ListPlaybookRunsSort.CREATE_AT.
        direction (Union[Unset, ListPlaybookRunsDirection]):  Default:
            ListPlaybookRunsDirection.DESC.
        statuses (Union[Unset, list[ListPlaybookRunsStatusesItem]]):
        owner_user_id (Union[Unset, str]):
        participant_id (Union[Unset, str]):
        search_term (Union[Unset, str]):
        channel_id (Union[Unset, str]):
        omit_ended (Union[Unset, bool]):  Default: False.
        since (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, PlaybookRunList]]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        page=page,
        per_page=per_page,
        sort=sort,
        direction=direction,
        statuses=statuses,
        owner_user_id=owner_user_id,
        participant_id=participant_id,
        search_term=search_term,
        channel_id=channel_id,
        omit_ended=omit_ended,
        since=since,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    team_id: str,
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 1000,
    sort: Union[Unset, ListPlaybookRunsSort] = ListPlaybookRunsSort.CREATE_AT,
    direction: Union[Unset, ListPlaybookRunsDirection] = ListPlaybookRunsDirection.DESC,
    statuses: Union[Unset, list[ListPlaybookRunsStatusesItem]] = UNSET,
    owner_user_id: Union[Unset, str] = UNSET,
    participant_id: Union[Unset, str] = UNSET,
    search_term: Union[Unset, str] = UNSET,
    channel_id: Union[Unset, str] = UNSET,
    omit_ended: Union[Unset, bool] = False,
    since: Union[Unset, int] = UNSET,
) -> Optional[Union[Error, PlaybookRunList]]:
    """List all playbook runs

     Retrieve a paged list of playbook runs, filtered by team, status, owner, name and/or members, and
    sorted by ID, name, status, creation date, end date, team or owner ID.

    Args:
        team_id (str):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 1000.
        sort (Union[Unset, ListPlaybookRunsSort]):  Default: ListPlaybookRunsSort.CREATE_AT.
        direction (Union[Unset, ListPlaybookRunsDirection]):  Default:
            ListPlaybookRunsDirection.DESC.
        statuses (Union[Unset, list[ListPlaybookRunsStatusesItem]]):
        owner_user_id (Union[Unset, str]):
        participant_id (Union[Unset, str]):
        search_term (Union[Unset, str]):
        channel_id (Union[Unset, str]):
        omit_ended (Union[Unset, bool]):  Default: False.
        since (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, PlaybookRunList]
    """

    return (
        await asyncio_detailed(
            client=client,
            team_id=team_id,
            page=page,
            per_page=per_page,
            sort=sort,
            direction=direction,
            statuses=statuses,
            owner_user_id=owner_user_id,
            participant_id=participant_id,
            search_term=search_term,
            channel_id=channel_id,
            omit_ended=omit_ended,
            since=since,
        )
    ).parsed
