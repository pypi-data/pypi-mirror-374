from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.user_threads import UserThreads
from ...types import UNSET, Response, Unset


def _get_kwargs(
    user_id: str,
    team_id: str,
    *,
    since: Union[Unset, int] = UNSET,
    deleted: Union[Unset, bool] = False,
    extended: Union[Unset, bool] = False,
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
    totals_only: Union[Unset, bool] = False,
    threads_only: Union[Unset, bool] = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["since"] = since

    params["deleted"] = deleted

    params["extended"] = extended

    params["page"] = page

    params["per_page"] = per_page

    params["totalsOnly"] = totals_only

    params["threadsOnly"] = threads_only

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v4/users/{user_id}/teams/{team_id}/threads",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, UserThreads]]:
    if response.status_code == 200:
        response_200 = UserThreads.from_dict(response.json())

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
) -> Response[Union[AppError, UserThreads]]:
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
    since: Union[Unset, int] = UNSET,
    deleted: Union[Unset, bool] = False,
    extended: Union[Unset, bool] = False,
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
    totals_only: Union[Unset, bool] = False,
    threads_only: Union[Unset, bool] = False,
) -> Response[Union[AppError, UserThreads]]:
    """Get all threads that user is following

     Get all threads that user is following

    __Minimum server version__: 5.29

    ##### Permissions
    Must be logged in as the user or have `edit_other_users` permission.

    Args:
        user_id (str):
        team_id (str):
        since (Union[Unset, int]):
        deleted (Union[Unset, bool]):  Default: False.
        extended (Union[Unset, bool]):  Default: False.
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.
        totals_only (Union[Unset, bool]):  Default: False.
        threads_only (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, UserThreads]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        team_id=team_id,
        since=since,
        deleted=deleted,
        extended=extended,
        page=page,
        per_page=per_page,
        totals_only=totals_only,
        threads_only=threads_only,
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
    since: Union[Unset, int] = UNSET,
    deleted: Union[Unset, bool] = False,
    extended: Union[Unset, bool] = False,
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
    totals_only: Union[Unset, bool] = False,
    threads_only: Union[Unset, bool] = False,
) -> Optional[Union[AppError, UserThreads]]:
    """Get all threads that user is following

     Get all threads that user is following

    __Minimum server version__: 5.29

    ##### Permissions
    Must be logged in as the user or have `edit_other_users` permission.

    Args:
        user_id (str):
        team_id (str):
        since (Union[Unset, int]):
        deleted (Union[Unset, bool]):  Default: False.
        extended (Union[Unset, bool]):  Default: False.
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.
        totals_only (Union[Unset, bool]):  Default: False.
        threads_only (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, UserThreads]
    """

    return sync_detailed(
        user_id=user_id,
        team_id=team_id,
        client=client,
        since=since,
        deleted=deleted,
        extended=extended,
        page=page,
        per_page=per_page,
        totals_only=totals_only,
        threads_only=threads_only,
    ).parsed


async def asyncio_detailed(
    user_id: str,
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    since: Union[Unset, int] = UNSET,
    deleted: Union[Unset, bool] = False,
    extended: Union[Unset, bool] = False,
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
    totals_only: Union[Unset, bool] = False,
    threads_only: Union[Unset, bool] = False,
) -> Response[Union[AppError, UserThreads]]:
    """Get all threads that user is following

     Get all threads that user is following

    __Minimum server version__: 5.29

    ##### Permissions
    Must be logged in as the user or have `edit_other_users` permission.

    Args:
        user_id (str):
        team_id (str):
        since (Union[Unset, int]):
        deleted (Union[Unset, bool]):  Default: False.
        extended (Union[Unset, bool]):  Default: False.
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.
        totals_only (Union[Unset, bool]):  Default: False.
        threads_only (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, UserThreads]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        team_id=team_id,
        since=since,
        deleted=deleted,
        extended=extended,
        page=page,
        per_page=per_page,
        totals_only=totals_only,
        threads_only=threads_only,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    user_id: str,
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    since: Union[Unset, int] = UNSET,
    deleted: Union[Unset, bool] = False,
    extended: Union[Unset, bool] = False,
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
    totals_only: Union[Unset, bool] = False,
    threads_only: Union[Unset, bool] = False,
) -> Optional[Union[AppError, UserThreads]]:
    """Get all threads that user is following

     Get all threads that user is following

    __Minimum server version__: 5.29

    ##### Permissions
    Must be logged in as the user or have `edit_other_users` permission.

    Args:
        user_id (str):
        team_id (str):
        since (Union[Unset, int]):
        deleted (Union[Unset, bool]):  Default: False.
        extended (Union[Unset, bool]):  Default: False.
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.
        totals_only (Union[Unset, bool]):  Default: False.
        threads_only (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, UserThreads]
    """

    return (
        await asyncio_detailed(
            user_id=user_id,
            team_id=team_id,
            client=client,
            since=since,
            deleted=deleted,
            extended=extended,
            page=page,
            per_page=per_page,
            totals_only=totals_only,
            threads_only=threads_only,
        )
    ).parsed
