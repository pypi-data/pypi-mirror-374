from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    role_filter: Union[Unset, str] = UNSET,
    team_filter: Union[Unset, str] = UNSET,
    has_no_team: Union[Unset, bool] = UNSET,
    hide_active: Union[Unset, bool] = UNSET,
    hide_inactive: Union[Unset, bool] = UNSET,
    search_term: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["role_filter"] = role_filter

    params["team_filter"] = team_filter

    params["has_no_team"] = has_no_team

    params["hide_active"] = hide_active

    params["hide_inactive"] = hide_inactive

    params["search_term"] = search_term

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v4/reports/users/count",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[float]:
    if response.status_code == 200:
        response_200 = cast(float, response.json())
        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[float]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    role_filter: Union[Unset, str] = UNSET,
    team_filter: Union[Unset, str] = UNSET,
    has_no_team: Union[Unset, bool] = UNSET,
    hide_active: Union[Unset, bool] = UNSET,
    hide_inactive: Union[Unset, bool] = UNSET,
    search_term: Union[Unset, str] = UNSET,
) -> Response[float]:
    """Gets the full count of users that match the filter.

     Get the full count of users admin reporting purposes, based on provided parameters.
    ##### Permissions
    Requires `sysconsole_read_user_management_users`.

    Args:
        role_filter (Union[Unset, str]):
        team_filter (Union[Unset, str]):
        has_no_team (Union[Unset, bool]):
        hide_active (Union[Unset, bool]):
        hide_inactive (Union[Unset, bool]):
        search_term (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[float]
    """

    kwargs = _get_kwargs(
        role_filter=role_filter,
        team_filter=team_filter,
        has_no_team=has_no_team,
        hide_active=hide_active,
        hide_inactive=hide_inactive,
        search_term=search_term,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    role_filter: Union[Unset, str] = UNSET,
    team_filter: Union[Unset, str] = UNSET,
    has_no_team: Union[Unset, bool] = UNSET,
    hide_active: Union[Unset, bool] = UNSET,
    hide_inactive: Union[Unset, bool] = UNSET,
    search_term: Union[Unset, str] = UNSET,
) -> Optional[float]:
    """Gets the full count of users that match the filter.

     Get the full count of users admin reporting purposes, based on provided parameters.
    ##### Permissions
    Requires `sysconsole_read_user_management_users`.

    Args:
        role_filter (Union[Unset, str]):
        team_filter (Union[Unset, str]):
        has_no_team (Union[Unset, bool]):
        hide_active (Union[Unset, bool]):
        hide_inactive (Union[Unset, bool]):
        search_term (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        float
    """

    return sync_detailed(
        client=client,
        role_filter=role_filter,
        team_filter=team_filter,
        has_no_team=has_no_team,
        hide_active=hide_active,
        hide_inactive=hide_inactive,
        search_term=search_term,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    role_filter: Union[Unset, str] = UNSET,
    team_filter: Union[Unset, str] = UNSET,
    has_no_team: Union[Unset, bool] = UNSET,
    hide_active: Union[Unset, bool] = UNSET,
    hide_inactive: Union[Unset, bool] = UNSET,
    search_term: Union[Unset, str] = UNSET,
) -> Response[float]:
    """Gets the full count of users that match the filter.

     Get the full count of users admin reporting purposes, based on provided parameters.
    ##### Permissions
    Requires `sysconsole_read_user_management_users`.

    Args:
        role_filter (Union[Unset, str]):
        team_filter (Union[Unset, str]):
        has_no_team (Union[Unset, bool]):
        hide_active (Union[Unset, bool]):
        hide_inactive (Union[Unset, bool]):
        search_term (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[float]
    """

    kwargs = _get_kwargs(
        role_filter=role_filter,
        team_filter=team_filter,
        has_no_team=has_no_team,
        hide_active=hide_active,
        hide_inactive=hide_inactive,
        search_term=search_term,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    role_filter: Union[Unset, str] = UNSET,
    team_filter: Union[Unset, str] = UNSET,
    has_no_team: Union[Unset, bool] = UNSET,
    hide_active: Union[Unset, bool] = UNSET,
    hide_inactive: Union[Unset, bool] = UNSET,
    search_term: Union[Unset, str] = UNSET,
) -> Optional[float]:
    """Gets the full count of users that match the filter.

     Get the full count of users admin reporting purposes, based on provided parameters.
    ##### Permissions
    Requires `sysconsole_read_user_management_users`.

    Args:
        role_filter (Union[Unset, str]):
        team_filter (Union[Unset, str]):
        has_no_team (Union[Unset, bool]):
        hide_active (Union[Unset, bool]):
        hide_inactive (Union[Unset, bool]):
        search_term (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        float
    """

    return (
        await asyncio_detailed(
            client=client,
            role_filter=role_filter,
            team_filter=team_filter,
            has_no_team=has_no_team,
            hide_active=hide_active,
            hide_inactive=hide_inactive,
            search_term=search_term,
        )
    ).parsed
