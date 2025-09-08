from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.user_report import UserReport
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    sort_column: Union[Unset, str] = "Username",
    direction: Union[Unset, str] = "next",
    sort_direction: Union[Unset, str] = "asc",
    page_size: Union[Unset, int] = 50,
    from_column_value: Union[Unset, str] = UNSET,
    from_id: Union[Unset, str] = UNSET,
    date_range: Union[Unset, str] = "alltime",
    role_filter: Union[Unset, str] = UNSET,
    team_filter: Union[Unset, str] = UNSET,
    has_no_team: Union[Unset, bool] = UNSET,
    hide_active: Union[Unset, bool] = UNSET,
    hide_inactive: Union[Unset, bool] = UNSET,
    search_term: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["sort_column"] = sort_column

    params["direction"] = direction

    params["sort_direction"] = sort_direction

    params["page_size"] = page_size

    params["from_column_value"] = from_column_value

    params["from_id"] = from_id

    params["date_range"] = date_range

    params["role_filter"] = role_filter

    params["team_filter"] = team_filter

    params["has_no_team"] = has_no_team

    params["hide_active"] = hide_active

    params["hide_inactive"] = hide_inactive

    params["search_term"] = search_term

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v4/reports/users",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, list["UserReport"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = UserReport.from_dict(response_200_item_data)

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

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, list["UserReport"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    sort_column: Union[Unset, str] = "Username",
    direction: Union[Unset, str] = "next",
    sort_direction: Union[Unset, str] = "asc",
    page_size: Union[Unset, int] = 50,
    from_column_value: Union[Unset, str] = UNSET,
    from_id: Union[Unset, str] = UNSET,
    date_range: Union[Unset, str] = "alltime",
    role_filter: Union[Unset, str] = UNSET,
    team_filter: Union[Unset, str] = UNSET,
    has_no_team: Union[Unset, bool] = UNSET,
    hide_active: Union[Unset, bool] = UNSET,
    hide_inactive: Union[Unset, bool] = UNSET,
    search_term: Union[Unset, str] = UNSET,
) -> Response[Union[AppError, list["UserReport"]]]:
    """Get a list of paged and sorted users for admin reporting purposes

     Get a list of paged users for admin reporting purposes, based on provided parameters.
    ##### Permissions
    Requires `sysconsole_read_user_management_users`.

    Args:
        sort_column (Union[Unset, str]):  Default: 'Username'.
        direction (Union[Unset, str]):  Default: 'next'.
        sort_direction (Union[Unset, str]):  Default: 'asc'.
        page_size (Union[Unset, int]):  Default: 50.
        from_column_value (Union[Unset, str]):
        from_id (Union[Unset, str]):
        date_range (Union[Unset, str]):  Default: 'alltime'.
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
        Response[Union[AppError, list['UserReport']]]
    """

    kwargs = _get_kwargs(
        sort_column=sort_column,
        direction=direction,
        sort_direction=sort_direction,
        page_size=page_size,
        from_column_value=from_column_value,
        from_id=from_id,
        date_range=date_range,
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
    sort_column: Union[Unset, str] = "Username",
    direction: Union[Unset, str] = "next",
    sort_direction: Union[Unset, str] = "asc",
    page_size: Union[Unset, int] = 50,
    from_column_value: Union[Unset, str] = UNSET,
    from_id: Union[Unset, str] = UNSET,
    date_range: Union[Unset, str] = "alltime",
    role_filter: Union[Unset, str] = UNSET,
    team_filter: Union[Unset, str] = UNSET,
    has_no_team: Union[Unset, bool] = UNSET,
    hide_active: Union[Unset, bool] = UNSET,
    hide_inactive: Union[Unset, bool] = UNSET,
    search_term: Union[Unset, str] = UNSET,
) -> Optional[Union[AppError, list["UserReport"]]]:
    """Get a list of paged and sorted users for admin reporting purposes

     Get a list of paged users for admin reporting purposes, based on provided parameters.
    ##### Permissions
    Requires `sysconsole_read_user_management_users`.

    Args:
        sort_column (Union[Unset, str]):  Default: 'Username'.
        direction (Union[Unset, str]):  Default: 'next'.
        sort_direction (Union[Unset, str]):  Default: 'asc'.
        page_size (Union[Unset, int]):  Default: 50.
        from_column_value (Union[Unset, str]):
        from_id (Union[Unset, str]):
        date_range (Union[Unset, str]):  Default: 'alltime'.
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
        Union[AppError, list['UserReport']]
    """

    return sync_detailed(
        client=client,
        sort_column=sort_column,
        direction=direction,
        sort_direction=sort_direction,
        page_size=page_size,
        from_column_value=from_column_value,
        from_id=from_id,
        date_range=date_range,
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
    sort_column: Union[Unset, str] = "Username",
    direction: Union[Unset, str] = "next",
    sort_direction: Union[Unset, str] = "asc",
    page_size: Union[Unset, int] = 50,
    from_column_value: Union[Unset, str] = UNSET,
    from_id: Union[Unset, str] = UNSET,
    date_range: Union[Unset, str] = "alltime",
    role_filter: Union[Unset, str] = UNSET,
    team_filter: Union[Unset, str] = UNSET,
    has_no_team: Union[Unset, bool] = UNSET,
    hide_active: Union[Unset, bool] = UNSET,
    hide_inactive: Union[Unset, bool] = UNSET,
    search_term: Union[Unset, str] = UNSET,
) -> Response[Union[AppError, list["UserReport"]]]:
    """Get a list of paged and sorted users for admin reporting purposes

     Get a list of paged users for admin reporting purposes, based on provided parameters.
    ##### Permissions
    Requires `sysconsole_read_user_management_users`.

    Args:
        sort_column (Union[Unset, str]):  Default: 'Username'.
        direction (Union[Unset, str]):  Default: 'next'.
        sort_direction (Union[Unset, str]):  Default: 'asc'.
        page_size (Union[Unset, int]):  Default: 50.
        from_column_value (Union[Unset, str]):
        from_id (Union[Unset, str]):
        date_range (Union[Unset, str]):  Default: 'alltime'.
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
        Response[Union[AppError, list['UserReport']]]
    """

    kwargs = _get_kwargs(
        sort_column=sort_column,
        direction=direction,
        sort_direction=sort_direction,
        page_size=page_size,
        from_column_value=from_column_value,
        from_id=from_id,
        date_range=date_range,
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
    sort_column: Union[Unset, str] = "Username",
    direction: Union[Unset, str] = "next",
    sort_direction: Union[Unset, str] = "asc",
    page_size: Union[Unset, int] = 50,
    from_column_value: Union[Unset, str] = UNSET,
    from_id: Union[Unset, str] = UNSET,
    date_range: Union[Unset, str] = "alltime",
    role_filter: Union[Unset, str] = UNSET,
    team_filter: Union[Unset, str] = UNSET,
    has_no_team: Union[Unset, bool] = UNSET,
    hide_active: Union[Unset, bool] = UNSET,
    hide_inactive: Union[Unset, bool] = UNSET,
    search_term: Union[Unset, str] = UNSET,
) -> Optional[Union[AppError, list["UserReport"]]]:
    """Get a list of paged and sorted users for admin reporting purposes

     Get a list of paged users for admin reporting purposes, based on provided parameters.
    ##### Permissions
    Requires `sysconsole_read_user_management_users`.

    Args:
        sort_column (Union[Unset, str]):  Default: 'Username'.
        direction (Union[Unset, str]):  Default: 'next'.
        sort_direction (Union[Unset, str]):  Default: 'asc'.
        page_size (Union[Unset, int]):  Default: 50.
        from_column_value (Union[Unset, str]):
        from_id (Union[Unset, str]):
        date_range (Union[Unset, str]):  Default: 'alltime'.
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
        Union[AppError, list['UserReport']]
    """

    return (
        await asyncio_detailed(
            client=client,
            sort_column=sort_column,
            direction=direction,
            sort_direction=sort_direction,
            page_size=page_size,
            from_column_value=from_column_value,
            from_id=from_id,
            date_range=date_range,
            role_filter=role_filter,
            team_filter=team_filter,
            has_no_team=has_no_team,
            hide_active=hide_active,
            hide_inactive=hide_inactive,
            search_term=search_term,
        )
    ).parsed
