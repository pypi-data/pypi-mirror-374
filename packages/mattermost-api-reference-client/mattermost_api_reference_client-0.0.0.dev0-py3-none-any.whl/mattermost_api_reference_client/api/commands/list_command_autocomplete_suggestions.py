from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.autocomplete_suggestion import AutocompleteSuggestion
from ...types import UNSET, Response


def _get_kwargs(
    team_id: str,
    *,
    user_input: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["user_input"] = user_input

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v4/teams/{team_id}/commands/autocomplete_suggestions",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, list["AutocompleteSuggestion"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = AutocompleteSuggestion.from_dict(response_200_item_data)

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

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, list["AutocompleteSuggestion"]]]:
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
    user_input: str,
) -> Response[Union[AppError, list["AutocompleteSuggestion"]]]:
    """List commands' autocomplete data

     List commands' autocomplete data for the team.
    ##### Permissions
    `view_team` for the team.
    __Minimum server version__: 5.24

    Args:
        team_id (str):
        user_input (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['AutocompleteSuggestion']]]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        user_input=user_input,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    user_input: str,
) -> Optional[Union[AppError, list["AutocompleteSuggestion"]]]:
    """List commands' autocomplete data

     List commands' autocomplete data for the team.
    ##### Permissions
    `view_team` for the team.
    __Minimum server version__: 5.24

    Args:
        team_id (str):
        user_input (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['AutocompleteSuggestion']]
    """

    return sync_detailed(
        team_id=team_id,
        client=client,
        user_input=user_input,
    ).parsed


async def asyncio_detailed(
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    user_input: str,
) -> Response[Union[AppError, list["AutocompleteSuggestion"]]]:
    """List commands' autocomplete data

     List commands' autocomplete data for the team.
    ##### Permissions
    `view_team` for the team.
    __Minimum server version__: 5.24

    Args:
        team_id (str):
        user_input (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['AutocompleteSuggestion']]]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        user_input=user_input,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    user_input: str,
) -> Optional[Union[AppError, list["AutocompleteSuggestion"]]]:
    """List commands' autocomplete data

     List commands' autocomplete data for the team.
    ##### Permissions
    `view_team` for the team.
    __Minimum server version__: 5.24

    Args:
        team_id (str):
        user_input (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['AutocompleteSuggestion']]
    """

    return (
        await asyncio_detailed(
            team_id=team_id,
            client=client,
            user_input=user_input,
        )
    ).parsed
