from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.team_member import TeamMember
from ...types import UNSET, Response, Unset


def _get_kwargs(
    team_id: str,
    *,
    body: list["TeamMember"],
    graceful: Union[Unset, bool] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["graceful"] = graceful

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v4/teams/{team_id}/members/batch",
        "params": params,
    }

    _kwargs["json"] = []
    for body_item_data in body:
        body_item = body_item_data.to_dict()
        _kwargs["json"].append(body_item)

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, list["TeamMember"]]]:
    if response.status_code == 201:
        response_201 = []
        _response_201 = response.json()
        for response_201_item_data in _response_201:
            response_201_item = TeamMember.from_dict(response_201_item_data)

            response_201.append(response_201_item)

        return response_201

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
) -> Response[Union[AppError, list["TeamMember"]]]:
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
    body: list["TeamMember"],
    graceful: Union[Unset, bool] = UNSET,
) -> Response[Union[AppError, list["TeamMember"]]]:
    """Add multiple users to team

     Add a number of users to the team by user_id.
    ##### Permissions
    Must be authenticated. Authenticated user must have the `add_user_to_team` permission.

    Args:
        team_id (str):
        graceful (Union[Unset, bool]):
        body (list['TeamMember']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['TeamMember']]]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        body=body,
        graceful=graceful,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: list["TeamMember"],
    graceful: Union[Unset, bool] = UNSET,
) -> Optional[Union[AppError, list["TeamMember"]]]:
    """Add multiple users to team

     Add a number of users to the team by user_id.
    ##### Permissions
    Must be authenticated. Authenticated user must have the `add_user_to_team` permission.

    Args:
        team_id (str):
        graceful (Union[Unset, bool]):
        body (list['TeamMember']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['TeamMember']]
    """

    return sync_detailed(
        team_id=team_id,
        client=client,
        body=body,
        graceful=graceful,
    ).parsed


async def asyncio_detailed(
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: list["TeamMember"],
    graceful: Union[Unset, bool] = UNSET,
) -> Response[Union[AppError, list["TeamMember"]]]:
    """Add multiple users to team

     Add a number of users to the team by user_id.
    ##### Permissions
    Must be authenticated. Authenticated user must have the `add_user_to_team` permission.

    Args:
        team_id (str):
        graceful (Union[Unset, bool]):
        body (list['TeamMember']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['TeamMember']]]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        body=body,
        graceful=graceful,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: list["TeamMember"],
    graceful: Union[Unset, bool] = UNSET,
) -> Optional[Union[AppError, list["TeamMember"]]]:
    """Add multiple users to team

     Add a number of users to the team by user_id.
    ##### Permissions
    Must be authenticated. Authenticated user must have the `add_user_to_team` permission.

    Args:
        team_id (str):
        graceful (Union[Unset, bool]):
        body (list['TeamMember']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['TeamMember']]
    """

    return (
        await asyncio_detailed(
            team_id=team_id,
            client=client,
            body=body,
            graceful=graceful,
        )
    ).parsed
