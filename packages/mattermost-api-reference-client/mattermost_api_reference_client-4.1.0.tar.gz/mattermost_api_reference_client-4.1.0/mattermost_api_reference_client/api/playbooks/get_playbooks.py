from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.get_playbooks_direction import GetPlaybooksDirection
from ...models.get_playbooks_sort import GetPlaybooksSort
from ...models.playbook_list import PlaybookList
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    team_id: str,
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 1000,
    sort: Union[Unset, GetPlaybooksSort] = GetPlaybooksSort.TITLE,
    direction: Union[Unset, GetPlaybooksDirection] = GetPlaybooksDirection.ASC,
    with_archived: Union[Unset, bool] = False,
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

    params["with_archived"] = with_archived

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/plugins/playbooks/api/v0/playbooks",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Error, PlaybookList]]:
    if response.status_code == 200:
        response_200 = PlaybookList.from_dict(response.json())

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
) -> Response[Union[Error, PlaybookList]]:
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
    sort: Union[Unset, GetPlaybooksSort] = GetPlaybooksSort.TITLE,
    direction: Union[Unset, GetPlaybooksDirection] = GetPlaybooksDirection.ASC,
    with_archived: Union[Unset, bool] = False,
) -> Response[Union[Error, PlaybookList]]:
    """List all playbooks

     Retrieve a paged list of playbooks, filtered by team, and sorted by title, number of stages or
    number of steps.

    Args:
        team_id (str):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 1000.
        sort (Union[Unset, GetPlaybooksSort]):  Default: GetPlaybooksSort.TITLE.
        direction (Union[Unset, GetPlaybooksDirection]):  Default: GetPlaybooksDirection.ASC.
        with_archived (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, PlaybookList]]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        page=page,
        per_page=per_page,
        sort=sort,
        direction=direction,
        with_archived=with_archived,
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
    sort: Union[Unset, GetPlaybooksSort] = GetPlaybooksSort.TITLE,
    direction: Union[Unset, GetPlaybooksDirection] = GetPlaybooksDirection.ASC,
    with_archived: Union[Unset, bool] = False,
) -> Optional[Union[Error, PlaybookList]]:
    """List all playbooks

     Retrieve a paged list of playbooks, filtered by team, and sorted by title, number of stages or
    number of steps.

    Args:
        team_id (str):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 1000.
        sort (Union[Unset, GetPlaybooksSort]):  Default: GetPlaybooksSort.TITLE.
        direction (Union[Unset, GetPlaybooksDirection]):  Default: GetPlaybooksDirection.ASC.
        with_archived (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, PlaybookList]
    """

    return sync_detailed(
        client=client,
        team_id=team_id,
        page=page,
        per_page=per_page,
        sort=sort,
        direction=direction,
        with_archived=with_archived,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    team_id: str,
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 1000,
    sort: Union[Unset, GetPlaybooksSort] = GetPlaybooksSort.TITLE,
    direction: Union[Unset, GetPlaybooksDirection] = GetPlaybooksDirection.ASC,
    with_archived: Union[Unset, bool] = False,
) -> Response[Union[Error, PlaybookList]]:
    """List all playbooks

     Retrieve a paged list of playbooks, filtered by team, and sorted by title, number of stages or
    number of steps.

    Args:
        team_id (str):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 1000.
        sort (Union[Unset, GetPlaybooksSort]):  Default: GetPlaybooksSort.TITLE.
        direction (Union[Unset, GetPlaybooksDirection]):  Default: GetPlaybooksDirection.ASC.
        with_archived (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, PlaybookList]]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        page=page,
        per_page=per_page,
        sort=sort,
        direction=direction,
        with_archived=with_archived,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    team_id: str,
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 1000,
    sort: Union[Unset, GetPlaybooksSort] = GetPlaybooksSort.TITLE,
    direction: Union[Unset, GetPlaybooksDirection] = GetPlaybooksDirection.ASC,
    with_archived: Union[Unset, bool] = False,
) -> Optional[Union[Error, PlaybookList]]:
    """List all playbooks

     Retrieve a paged list of playbooks, filtered by team, and sorted by title, number of stages or
    number of steps.

    Args:
        team_id (str):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 1000.
        sort (Union[Unset, GetPlaybooksSort]):  Default: GetPlaybooksSort.TITLE.
        direction (Union[Unset, GetPlaybooksDirection]):  Default: GetPlaybooksDirection.ASC.
        with_archived (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, PlaybookList]
    """

    return (
        await asyncio_detailed(
            client=client,
            team_id=team_id,
            page=page,
            per_page=per_page,
            sort=sort,
            direction=direction,
            with_archived=with_archived,
        )
    ).parsed
