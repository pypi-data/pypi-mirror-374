from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.status_ok import StatusOK
from ...models.update_team_member_scheme_roles_body import UpdateTeamMemberSchemeRolesBody
from ...types import Response


def _get_kwargs(
    team_id: str,
    user_id: str,
    *,
    body: UpdateTeamMemberSchemeRolesBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/api/v4/teams/{team_id}/members/{user_id}/schemeRoles",
    }

    _kwargs["json"] = body.to_dict()

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

    if response.status_code == 404:
        response_404 = AppError.from_dict(response.json())

        return response_404

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
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateTeamMemberSchemeRolesBody,
) -> Response[Union[AppError, StatusOK]]:
    """Update the scheme-derived roles of a team member.

     Update a team member's scheme_admin/scheme_user properties. Typically this should either be
    `scheme_admin=false, scheme_user=true` for ordinary team member, or `scheme_admin=true,
    scheme_user=true` for a team admin.

    __Minimum server version__: 5.0

    ##### Permissions
    Must be authenticated and have the `manage_team_roles` permission.

    Args:
        team_id (str):
        user_id (str):
        body (UpdateTeamMemberSchemeRolesBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, StatusOK]]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        user_id=user_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    team_id: str,
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateTeamMemberSchemeRolesBody,
) -> Optional[Union[AppError, StatusOK]]:
    """Update the scheme-derived roles of a team member.

     Update a team member's scheme_admin/scheme_user properties. Typically this should either be
    `scheme_admin=false, scheme_user=true` for ordinary team member, or `scheme_admin=true,
    scheme_user=true` for a team admin.

    __Minimum server version__: 5.0

    ##### Permissions
    Must be authenticated and have the `manage_team_roles` permission.

    Args:
        team_id (str):
        user_id (str):
        body (UpdateTeamMemberSchemeRolesBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, StatusOK]
    """

    return sync_detailed(
        team_id=team_id,
        user_id=user_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    team_id: str,
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateTeamMemberSchemeRolesBody,
) -> Response[Union[AppError, StatusOK]]:
    """Update the scheme-derived roles of a team member.

     Update a team member's scheme_admin/scheme_user properties. Typically this should either be
    `scheme_admin=false, scheme_user=true` for ordinary team member, or `scheme_admin=true,
    scheme_user=true` for a team admin.

    __Minimum server version__: 5.0

    ##### Permissions
    Must be authenticated and have the `manage_team_roles` permission.

    Args:
        team_id (str):
        user_id (str):
        body (UpdateTeamMemberSchemeRolesBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, StatusOK]]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        user_id=user_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    team_id: str,
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateTeamMemberSchemeRolesBody,
) -> Optional[Union[AppError, StatusOK]]:
    """Update the scheme-derived roles of a team member.

     Update a team member's scheme_admin/scheme_user properties. Typically this should either be
    `scheme_admin=false, scheme_user=true` for ordinary team member, or `scheme_admin=true,
    scheme_user=true` for a team admin.

    __Minimum server version__: 5.0

    ##### Permissions
    Must be authenticated and have the `manage_team_roles` permission.

    Args:
        team_id (str):
        user_id (str):
        body (UpdateTeamMemberSchemeRolesBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, StatusOK]
    """

    return (
        await asyncio_detailed(
            team_id=team_id,
            user_id=user_id,
            client=client,
            body=body,
        )
    ).parsed
