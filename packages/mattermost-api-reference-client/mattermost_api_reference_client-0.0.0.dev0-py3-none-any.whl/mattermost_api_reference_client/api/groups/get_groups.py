from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.group import Group
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
    q: Union[Unset, str] = UNSET,
    include_member_count: Union[Unset, bool] = UNSET,
    not_associated_to_team: Union[Unset, str] = UNSET,
    not_associated_to_channel: Union[Unset, str] = UNSET,
    since: Union[Unset, int] = UNSET,
    filter_allow_reference: Union[Unset, bool] = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["per_page"] = per_page

    params["q"] = q

    params["include_member_count"] = include_member_count

    params["not_associated_to_team"] = not_associated_to_team

    params["not_associated_to_channel"] = not_associated_to_channel

    params["since"] = since

    params["filter_allow_reference"] = filter_allow_reference

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v4/groups",
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
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
    q: Union[Unset, str] = UNSET,
    include_member_count: Union[Unset, bool] = UNSET,
    not_associated_to_team: Union[Unset, str] = UNSET,
    not_associated_to_channel: Union[Unset, str] = UNSET,
    since: Union[Unset, int] = UNSET,
    filter_allow_reference: Union[Unset, bool] = False,
) -> Response[Union[AppError, list["Group"]]]:
    """Get groups

     Retrieve a list of all groups not associated to a particular channel or team.

    If you use `not_associated_to_team`, you must be a team admin for that particular team (permission
    to manage that team).

    If you use `not_associated_to_channel`, you must be a channel admin for that particular channel
    (permission to manage that channel).

    __Minimum server version__: 5.11

    Args:
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.
        q (Union[Unset, str]):
        include_member_count (Union[Unset, bool]):
        not_associated_to_team (Union[Unset, str]):
        not_associated_to_channel (Union[Unset, str]):
        since (Union[Unset, int]):
        filter_allow_reference (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['Group']]]
    """

    kwargs = _get_kwargs(
        page=page,
        per_page=per_page,
        q=q,
        include_member_count=include_member_count,
        not_associated_to_team=not_associated_to_team,
        not_associated_to_channel=not_associated_to_channel,
        since=since,
        filter_allow_reference=filter_allow_reference,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
    q: Union[Unset, str] = UNSET,
    include_member_count: Union[Unset, bool] = UNSET,
    not_associated_to_team: Union[Unset, str] = UNSET,
    not_associated_to_channel: Union[Unset, str] = UNSET,
    since: Union[Unset, int] = UNSET,
    filter_allow_reference: Union[Unset, bool] = False,
) -> Optional[Union[AppError, list["Group"]]]:
    """Get groups

     Retrieve a list of all groups not associated to a particular channel or team.

    If you use `not_associated_to_team`, you must be a team admin for that particular team (permission
    to manage that team).

    If you use `not_associated_to_channel`, you must be a channel admin for that particular channel
    (permission to manage that channel).

    __Minimum server version__: 5.11

    Args:
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.
        q (Union[Unset, str]):
        include_member_count (Union[Unset, bool]):
        not_associated_to_team (Union[Unset, str]):
        not_associated_to_channel (Union[Unset, str]):
        since (Union[Unset, int]):
        filter_allow_reference (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['Group']]
    """

    return sync_detailed(
        client=client,
        page=page,
        per_page=per_page,
        q=q,
        include_member_count=include_member_count,
        not_associated_to_team=not_associated_to_team,
        not_associated_to_channel=not_associated_to_channel,
        since=since,
        filter_allow_reference=filter_allow_reference,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
    q: Union[Unset, str] = UNSET,
    include_member_count: Union[Unset, bool] = UNSET,
    not_associated_to_team: Union[Unset, str] = UNSET,
    not_associated_to_channel: Union[Unset, str] = UNSET,
    since: Union[Unset, int] = UNSET,
    filter_allow_reference: Union[Unset, bool] = False,
) -> Response[Union[AppError, list["Group"]]]:
    """Get groups

     Retrieve a list of all groups not associated to a particular channel or team.

    If you use `not_associated_to_team`, you must be a team admin for that particular team (permission
    to manage that team).

    If you use `not_associated_to_channel`, you must be a channel admin for that particular channel
    (permission to manage that channel).

    __Minimum server version__: 5.11

    Args:
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.
        q (Union[Unset, str]):
        include_member_count (Union[Unset, bool]):
        not_associated_to_team (Union[Unset, str]):
        not_associated_to_channel (Union[Unset, str]):
        since (Union[Unset, int]):
        filter_allow_reference (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['Group']]]
    """

    kwargs = _get_kwargs(
        page=page,
        per_page=per_page,
        q=q,
        include_member_count=include_member_count,
        not_associated_to_team=not_associated_to_team,
        not_associated_to_channel=not_associated_to_channel,
        since=since,
        filter_allow_reference=filter_allow_reference,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
    q: Union[Unset, str] = UNSET,
    include_member_count: Union[Unset, bool] = UNSET,
    not_associated_to_team: Union[Unset, str] = UNSET,
    not_associated_to_channel: Union[Unset, str] = UNSET,
    since: Union[Unset, int] = UNSET,
    filter_allow_reference: Union[Unset, bool] = False,
) -> Optional[Union[AppError, list["Group"]]]:
    """Get groups

     Retrieve a list of all groups not associated to a particular channel or team.

    If you use `not_associated_to_team`, you must be a team admin for that particular team (permission
    to manage that team).

    If you use `not_associated_to_channel`, you must be a channel admin for that particular channel
    (permission to manage that channel).

    __Minimum server version__: 5.11

    Args:
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.
        q (Union[Unset, str]):
        include_member_count (Union[Unset, bool]):
        not_associated_to_team (Union[Unset, str]):
        not_associated_to_channel (Union[Unset, str]):
        since (Union[Unset, int]):
        filter_allow_reference (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['Group']]
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            per_page=per_page,
            q=q,
            include_member_count=include_member_count,
            not_associated_to_team=not_associated_to_team,
            not_associated_to_channel=not_associated_to_channel,
            since=since,
            filter_allow_reference=filter_allow_reference,
        )
    ).parsed
