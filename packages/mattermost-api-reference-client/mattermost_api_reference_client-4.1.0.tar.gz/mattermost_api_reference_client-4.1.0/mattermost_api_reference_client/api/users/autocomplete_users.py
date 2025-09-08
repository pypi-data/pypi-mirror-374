from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.user_autocomplete import UserAutocomplete
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    team_id: Union[Unset, str] = UNSET,
    channel_id: Union[Unset, str] = UNSET,
    name: str,
    limit: Union[Unset, int] = 100,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["team_id"] = team_id

    params["channel_id"] = channel_id

    params["name"] = name

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v4/users/autocomplete",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, UserAutocomplete]]:
    if response.status_code == 200:
        response_200 = UserAutocomplete.from_dict(response.json())

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

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, UserAutocomplete]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    team_id: Union[Unset, str] = UNSET,
    channel_id: Union[Unset, str] = UNSET,
    name: str,
    limit: Union[Unset, int] = 100,
) -> Response[Union[AppError, UserAutocomplete]]:
    """Autocomplete users

     Get a list of users for the purpose of autocompleting based on the provided search term. Specify a
    combination of `team_id` and `channel_id` to filter results further.
    ##### Permissions
    Requires an active session and `view_team` and `read_channel` on any teams or channels used to
    filter the results further.

    Args:
        team_id (Union[Unset, str]):
        channel_id (Union[Unset, str]):
        name (str):
        limit (Union[Unset, int]):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, UserAutocomplete]]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        channel_id=channel_id,
        name=name,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    team_id: Union[Unset, str] = UNSET,
    channel_id: Union[Unset, str] = UNSET,
    name: str,
    limit: Union[Unset, int] = 100,
) -> Optional[Union[AppError, UserAutocomplete]]:
    """Autocomplete users

     Get a list of users for the purpose of autocompleting based on the provided search term. Specify a
    combination of `team_id` and `channel_id` to filter results further.
    ##### Permissions
    Requires an active session and `view_team` and `read_channel` on any teams or channels used to
    filter the results further.

    Args:
        team_id (Union[Unset, str]):
        channel_id (Union[Unset, str]):
        name (str):
        limit (Union[Unset, int]):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, UserAutocomplete]
    """

    return sync_detailed(
        client=client,
        team_id=team_id,
        channel_id=channel_id,
        name=name,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    team_id: Union[Unset, str] = UNSET,
    channel_id: Union[Unset, str] = UNSET,
    name: str,
    limit: Union[Unset, int] = 100,
) -> Response[Union[AppError, UserAutocomplete]]:
    """Autocomplete users

     Get a list of users for the purpose of autocompleting based on the provided search term. Specify a
    combination of `team_id` and `channel_id` to filter results further.
    ##### Permissions
    Requires an active session and `view_team` and `read_channel` on any teams or channels used to
    filter the results further.

    Args:
        team_id (Union[Unset, str]):
        channel_id (Union[Unset, str]):
        name (str):
        limit (Union[Unset, int]):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, UserAutocomplete]]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        channel_id=channel_id,
        name=name,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    team_id: Union[Unset, str] = UNSET,
    channel_id: Union[Unset, str] = UNSET,
    name: str,
    limit: Union[Unset, int] = 100,
) -> Optional[Union[AppError, UserAutocomplete]]:
    """Autocomplete users

     Get a list of users for the purpose of autocompleting based on the provided search term. Specify a
    combination of `team_id` and `channel_id` to filter results further.
    ##### Permissions
    Requires an active session and `view_team` and `read_channel` on any teams or channels used to
    filter the results further.

    Args:
        team_id (Union[Unset, str]):
        channel_id (Union[Unset, str]):
        name (str):
        limit (Union[Unset, int]):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, UserAutocomplete]
    """

    return (
        await asyncio_detailed(
            client=client,
            team_id=team_id,
            channel_id=channel_id,
            name=name,
            limit=limit,
        )
    ).parsed
