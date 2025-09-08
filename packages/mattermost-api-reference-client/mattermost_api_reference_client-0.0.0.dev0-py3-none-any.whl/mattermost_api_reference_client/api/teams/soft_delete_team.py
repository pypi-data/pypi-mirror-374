from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.status_ok import StatusOK
from ...types import UNSET, Response, Unset


def _get_kwargs(
    team_id: str,
    *,
    permanent: Union[Unset, bool] = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["permanent"] = permanent

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": f"/api/v4/teams/{team_id}",
        "params": params,
    }

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
    *,
    client: Union[AuthenticatedClient, Client],
    permanent: Union[Unset, bool] = False,
) -> Response[Union[AppError, StatusOK]]:
    """Delete a team

     Soft deletes a team, by marking the team as deleted in the database. Soft deleted teams will not be
    accessible in the user interface.

    Optionally use the permanent query parameter to hard delete the team for compliance reasons. As of
    server version 5.0, to use this feature `ServiceSettings.EnableAPITeamDeletion` must be set to
    `true` in the server's configuration.
    ##### Permissions
    Must have the `manage_team` permission.

    Args:
        team_id (str):
        permanent (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, StatusOK]]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        permanent=permanent,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    permanent: Union[Unset, bool] = False,
) -> Optional[Union[AppError, StatusOK]]:
    """Delete a team

     Soft deletes a team, by marking the team as deleted in the database. Soft deleted teams will not be
    accessible in the user interface.

    Optionally use the permanent query parameter to hard delete the team for compliance reasons. As of
    server version 5.0, to use this feature `ServiceSettings.EnableAPITeamDeletion` must be set to
    `true` in the server's configuration.
    ##### Permissions
    Must have the `manage_team` permission.

    Args:
        team_id (str):
        permanent (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, StatusOK]
    """

    return sync_detailed(
        team_id=team_id,
        client=client,
        permanent=permanent,
    ).parsed


async def asyncio_detailed(
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    permanent: Union[Unset, bool] = False,
) -> Response[Union[AppError, StatusOK]]:
    """Delete a team

     Soft deletes a team, by marking the team as deleted in the database. Soft deleted teams will not be
    accessible in the user interface.

    Optionally use the permanent query parameter to hard delete the team for compliance reasons. As of
    server version 5.0, to use this feature `ServiceSettings.EnableAPITeamDeletion` must be set to
    `true` in the server's configuration.
    ##### Permissions
    Must have the `manage_team` permission.

    Args:
        team_id (str):
        permanent (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, StatusOK]]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        permanent=permanent,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    permanent: Union[Unset, bool] = False,
) -> Optional[Union[AppError, StatusOK]]:
    """Delete a team

     Soft deletes a team, by marking the team as deleted in the database. Soft deleted teams will not be
    accessible in the user interface.

    Optionally use the permanent query parameter to hard delete the team for compliance reasons. As of
    server version 5.0, to use this feature `ServiceSettings.EnableAPITeamDeletion` must be set to
    `true` in the server's configuration.
    ##### Permissions
    Must have the `manage_team` permission.

    Args:
        team_id (str):
        permanent (Union[Unset, bool]):  Default: False.

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
            permanent=permanent,
        )
    ).parsed
