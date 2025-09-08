from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.get_team_invite_info_response_200 import GetTeamInviteInfoResponse200
from ...types import Response


def _get_kwargs(
    invite_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v4/teams/invite/{invite_id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, GetTeamInviteInfoResponse200]]:
    if response.status_code == 200:
        response_200 = GetTeamInviteInfoResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = AppError.from_dict(response.json())

        return response_400

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, GetTeamInviteInfoResponse200]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    invite_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, GetTeamInviteInfoResponse200]]:
    """Get invite info for a team

     Get the `name`, `display_name`, `description` and `id` for a team from the invite id.

    __Minimum server version__: 4.0

    ##### Permissions
    No authentication required.

    Args:
        invite_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, GetTeamInviteInfoResponse200]]
    """

    kwargs = _get_kwargs(
        invite_id=invite_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    invite_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, GetTeamInviteInfoResponse200]]:
    """Get invite info for a team

     Get the `name`, `display_name`, `description` and `id` for a team from the invite id.

    __Minimum server version__: 4.0

    ##### Permissions
    No authentication required.

    Args:
        invite_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, GetTeamInviteInfoResponse200]
    """

    return sync_detailed(
        invite_id=invite_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    invite_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, GetTeamInviteInfoResponse200]]:
    """Get invite info for a team

     Get the `name`, `display_name`, `description` and `id` for a team from the invite id.

    __Minimum server version__: 4.0

    ##### Permissions
    No authentication required.

    Args:
        invite_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, GetTeamInviteInfoResponse200]]
    """

    kwargs = _get_kwargs(
        invite_id=invite_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    invite_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, GetTeamInviteInfoResponse200]]:
    """Get invite info for a team

     Get the `name`, `display_name`, `description` and `id` for a team from the invite id.

    __Minimum server version__: 4.0

    ##### Permissions
    No authentication required.

    Args:
        invite_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, GetTeamInviteInfoResponse200]
    """

    return (
        await asyncio_detailed(
            invite_id=invite_id,
            client=client,
        )
    ).parsed
