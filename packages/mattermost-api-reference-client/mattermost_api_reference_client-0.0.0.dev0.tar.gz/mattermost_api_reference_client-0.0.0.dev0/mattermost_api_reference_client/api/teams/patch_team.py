from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.patch_team_body import PatchTeamBody
from ...models.team import Team
from ...types import Response


def _get_kwargs(
    team_id: str,
    *,
    body: PatchTeamBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/api/v4/teams/{team_id}/patch",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
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
    body: PatchTeamBody,
) -> Response[Union[AppError, Team]]:
    """Patch a team

     Partially update a team by providing only the fields you want to update. Omitted fields will not be
    updated. The fields that can be updated are defined in the request body, all other provided fields
    will be ignored.
    ##### Permissions
    Must have the `manage_team` permission.

    Args:
        team_id (str):
        body (PatchTeamBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, Team]]
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
    body: PatchTeamBody,
) -> Optional[Union[AppError, Team]]:
    """Patch a team

     Partially update a team by providing only the fields you want to update. Omitted fields will not be
    updated. The fields that can be updated are defined in the request body, all other provided fields
    will be ignored.
    ##### Permissions
    Must have the `manage_team` permission.

    Args:
        team_id (str):
        body (PatchTeamBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, Team]
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
    body: PatchTeamBody,
) -> Response[Union[AppError, Team]]:
    """Patch a team

     Partially update a team by providing only the fields you want to update. Omitted fields will not be
    updated. The fields that can be updated are defined in the request body, all other provided fields
    will be ignored.
    ##### Permissions
    Must have the `manage_team` permission.

    Args:
        team_id (str):
        body (PatchTeamBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, Team]]
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
    body: PatchTeamBody,
) -> Optional[Union[AppError, Team]]:
    """Patch a team

     Partially update a team by providing only the fields you want to update. Omitted fields will not be
    updated. The fields that can be updated are defined in the request body, all other provided fields
    will be ignored.
    ##### Permissions
    Must have the `manage_team` permission.

    Args:
        team_id (str):
        body (PatchTeamBody):

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
            body=body,
        )
    ).parsed
