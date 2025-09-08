from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.get_channels_direction import GetChannelsDirection
from ...models.get_channels_sort import GetChannelsSort
from ...models.get_channels_status import GetChannelsStatus
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    team_id: str,
    sort: Union[Unset, GetChannelsSort] = GetChannelsSort.CREATE_AT,
    direction: Union[Unset, GetChannelsDirection] = GetChannelsDirection.DESC,
    status: Union[Unset, GetChannelsStatus] = GetChannelsStatus.ALL,
    owner_user_id: Union[Unset, str] = UNSET,
    search_term: Union[Unset, str] = UNSET,
    participant_id: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["team_id"] = team_id

    json_sort: Union[Unset, str] = UNSET
    if not isinstance(sort, Unset):
        json_sort = sort.value

    params["sort"] = json_sort

    json_direction: Union[Unset, str] = UNSET
    if not isinstance(direction, Unset):
        json_direction = direction.value

    params["direction"] = json_direction

    json_status: Union[Unset, str] = UNSET
    if not isinstance(status, Unset):
        json_status = status.value

    params["status"] = json_status

    params["owner_user_id"] = owner_user_id

    params["search_term"] = search_term

    params["participant_id"] = participant_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/plugins/playbooks/api/v0/runs/channels",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Error, list[str]]]:
    if response.status_code == 200:
        response_200 = cast(list[str], response.json())

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
) -> Response[Union[Error, list[str]]]:
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
    sort: Union[Unset, GetChannelsSort] = GetChannelsSort.CREATE_AT,
    direction: Union[Unset, GetChannelsDirection] = GetChannelsDirection.DESC,
    status: Union[Unset, GetChannelsStatus] = GetChannelsStatus.ALL,
    owner_user_id: Union[Unset, str] = UNSET,
    search_term: Union[Unset, str] = UNSET,
    participant_id: Union[Unset, str] = UNSET,
) -> Response[Union[Error, list[str]]]:
    """Get playbook run channels

     Get all channels associated with a playbook run, filtered by team, status, owner, name and/or
    members, and sorted by ID, name, status, creation date, end date, team, or owner ID.

    Args:
        team_id (str):
        sort (Union[Unset, GetChannelsSort]):  Default: GetChannelsSort.CREATE_AT.
        direction (Union[Unset, GetChannelsDirection]):  Default: GetChannelsDirection.DESC.
        status (Union[Unset, GetChannelsStatus]):  Default: GetChannelsStatus.ALL.
        owner_user_id (Union[Unset, str]):
        search_term (Union[Unset, str]):
        participant_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, list[str]]]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        sort=sort,
        direction=direction,
        status=status,
        owner_user_id=owner_user_id,
        search_term=search_term,
        participant_id=participant_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    team_id: str,
    sort: Union[Unset, GetChannelsSort] = GetChannelsSort.CREATE_AT,
    direction: Union[Unset, GetChannelsDirection] = GetChannelsDirection.DESC,
    status: Union[Unset, GetChannelsStatus] = GetChannelsStatus.ALL,
    owner_user_id: Union[Unset, str] = UNSET,
    search_term: Union[Unset, str] = UNSET,
    participant_id: Union[Unset, str] = UNSET,
) -> Optional[Union[Error, list[str]]]:
    """Get playbook run channels

     Get all channels associated with a playbook run, filtered by team, status, owner, name and/or
    members, and sorted by ID, name, status, creation date, end date, team, or owner ID.

    Args:
        team_id (str):
        sort (Union[Unset, GetChannelsSort]):  Default: GetChannelsSort.CREATE_AT.
        direction (Union[Unset, GetChannelsDirection]):  Default: GetChannelsDirection.DESC.
        status (Union[Unset, GetChannelsStatus]):  Default: GetChannelsStatus.ALL.
        owner_user_id (Union[Unset, str]):
        search_term (Union[Unset, str]):
        participant_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, list[str]]
    """

    return sync_detailed(
        client=client,
        team_id=team_id,
        sort=sort,
        direction=direction,
        status=status,
        owner_user_id=owner_user_id,
        search_term=search_term,
        participant_id=participant_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    team_id: str,
    sort: Union[Unset, GetChannelsSort] = GetChannelsSort.CREATE_AT,
    direction: Union[Unset, GetChannelsDirection] = GetChannelsDirection.DESC,
    status: Union[Unset, GetChannelsStatus] = GetChannelsStatus.ALL,
    owner_user_id: Union[Unset, str] = UNSET,
    search_term: Union[Unset, str] = UNSET,
    participant_id: Union[Unset, str] = UNSET,
) -> Response[Union[Error, list[str]]]:
    """Get playbook run channels

     Get all channels associated with a playbook run, filtered by team, status, owner, name and/or
    members, and sorted by ID, name, status, creation date, end date, team, or owner ID.

    Args:
        team_id (str):
        sort (Union[Unset, GetChannelsSort]):  Default: GetChannelsSort.CREATE_AT.
        direction (Union[Unset, GetChannelsDirection]):  Default: GetChannelsDirection.DESC.
        status (Union[Unset, GetChannelsStatus]):  Default: GetChannelsStatus.ALL.
        owner_user_id (Union[Unset, str]):
        search_term (Union[Unset, str]):
        participant_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, list[str]]]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        sort=sort,
        direction=direction,
        status=status,
        owner_user_id=owner_user_id,
        search_term=search_term,
        participant_id=participant_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    team_id: str,
    sort: Union[Unset, GetChannelsSort] = GetChannelsSort.CREATE_AT,
    direction: Union[Unset, GetChannelsDirection] = GetChannelsDirection.DESC,
    status: Union[Unset, GetChannelsStatus] = GetChannelsStatus.ALL,
    owner_user_id: Union[Unset, str] = UNSET,
    search_term: Union[Unset, str] = UNSET,
    participant_id: Union[Unset, str] = UNSET,
) -> Optional[Union[Error, list[str]]]:
    """Get playbook run channels

     Get all channels associated with a playbook run, filtered by team, status, owner, name and/or
    members, and sorted by ID, name, status, creation date, end date, team, or owner ID.

    Args:
        team_id (str):
        sort (Union[Unset, GetChannelsSort]):  Default: GetChannelsSort.CREATE_AT.
        direction (Union[Unset, GetChannelsDirection]):  Default: GetChannelsDirection.DESC.
        status (Union[Unset, GetChannelsStatus]):  Default: GetChannelsStatus.ALL.
        owner_user_id (Union[Unset, str]):
        search_term (Union[Unset, str]):
        participant_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, list[str]]
    """

    return (
        await asyncio_detailed(
            client=client,
            team_id=team_id,
            sort=sort,
            direction=direction,
            status=status,
            owner_user_id=owner_user_id,
            search_term=search_term,
            participant_id=participant_id,
        )
    ).parsed
