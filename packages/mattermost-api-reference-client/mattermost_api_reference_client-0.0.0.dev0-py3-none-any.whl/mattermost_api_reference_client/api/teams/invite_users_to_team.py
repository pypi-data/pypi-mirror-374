from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.status_ok import StatusOK
from ...types import Response


def _get_kwargs(
    team_id: str,
    *,
    body: list[str],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v4/teams/{team_id}/invite/email",
    }

    _kwargs["json"] = body

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, StatusOK]]:
    if response.status_code == 200:
        response_200 = StatusOK.from_dict(response.json())

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

    if response.status_code == 413:
        response_413 = AppError.from_dict(response.json())

        return response_413

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, StatusOK]]:
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
    body: list[str],
) -> Response[Union[AppError, StatusOK]]:
    """Invite users to the team by email

     Invite users to the existing team using the user's email.

    The number of emails that can be sent is rate limited to 20 per hour with a burst of 20 emails. If
    the rate limit exceeds, the error message contains details on when to retry and when the timer will
    be reset.
    ##### Permissions
    Must have `invite_user` and `add_user_to_team` permissions for the team.

    Args:
        team_id (str):
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, StatusOK]]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: list[str],
) -> Optional[Union[AppError, StatusOK]]:
    """Invite users to the team by email

     Invite users to the existing team using the user's email.

    The number of emails that can be sent is rate limited to 20 per hour with a burst of 20 emails. If
    the rate limit exceeds, the error message contains details on when to retry and when the timer will
    be reset.
    ##### Permissions
    Must have `invite_user` and `add_user_to_team` permissions for the team.

    Args:
        team_id (str):
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, StatusOK]
    """

    return sync_detailed(
        team_id=team_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: list[str],
) -> Response[Union[AppError, StatusOK]]:
    """Invite users to the team by email

     Invite users to the existing team using the user's email.

    The number of emails that can be sent is rate limited to 20 per hour with a burst of 20 emails. If
    the rate limit exceeds, the error message contains details on when to retry and when the timer will
    be reset.
    ##### Permissions
    Must have `invite_user` and `add_user_to_team` permissions for the team.

    Args:
        team_id (str):
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, StatusOK]]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: list[str],
) -> Optional[Union[AppError, StatusOK]]:
    """Invite users to the team by email

     Invite users to the existing team using the user's email.

    The number of emails that can be sent is rate limited to 20 per hour with a burst of 20 emails. If
    the rate limit exceeds, the error message contains details on when to retry and when the timer will
    be reset.
    ##### Permissions
    Must have `invite_user` and `add_user_to_team` permissions for the team.

    Args:
        team_id (str):
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, StatusOK]
    """

    return (
        await asyncio_detailed(
            team_id=team_id,
            client=client,
            body=body,
        )
    ).parsed
