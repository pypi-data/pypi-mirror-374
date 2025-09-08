from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.team import Team
from ...types import Response


def _get_kwargs(
    team_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v4/teams/{team_id}/regenerate_invite_id",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, Team]]:
    if response.status_code == 200:
        response_200 = Team.from_dict(response.json())

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

    if response.status_code == 404:
        response_404 = AppError.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, Team]]:
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
) -> Response[Union[AppError, Team]]:
    """Regenerate the Invite ID from a Team

     Regenerates the invite ID used in invite links of a team
    ##### Permissions
    Must be authenticated and have the `manage_team` permission.

    Args:
        team_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, Team]]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, Team]]:
    """Regenerate the Invite ID from a Team

     Regenerates the invite ID used in invite links of a team
    ##### Permissions
    Must be authenticated and have the `manage_team` permission.

    Args:
        team_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, Team]
    """

    return sync_detailed(
        team_id=team_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, Team]]:
    """Regenerate the Invite ID from a Team

     Regenerates the invite ID used in invite links of a team
    ##### Permissions
    Must be authenticated and have the `manage_team` permission.

    Args:
        team_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, Team]]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, Team]]:
    """Regenerate the Invite ID from a Team

     Regenerates the invite ID used in invite links of a team
    ##### Permissions
    Must be authenticated and have the `manage_team` permission.

    Args:
        team_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, Team]
    """

    return (
        await asyncio_detailed(
            team_id=team_id,
            client=client,
        )
    ).parsed
