from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.sidebar_category import SidebarCategory
from ...types import Response


def _get_kwargs(
    user_id: str,
    team_id: str,
    category_id: str,
    *,
    body: SidebarCategory,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/api/v4/users/{user_id}/teams/{team_id}/channels/categories/{category_id}",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, SidebarCategory]]:
    if response.status_code == 200:
        response_200 = SidebarCategory.from_dict(response.json())

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
) -> Response[Union[AppError, SidebarCategory]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    user_id: str,
    team_id: str,
    category_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: SidebarCategory,
) -> Response[Union[AppError, SidebarCategory]]:
    """Update sidebar category

     Updates a single sidebar category for the user on the given team.
    __Minimum server version__: 5.26
    ##### Permissions
    Must be authenticated and have the `list_team_channels` permission.

    Args:
        user_id (str):
        team_id (str):
        category_id (str):
        body (SidebarCategory): User's sidebar category

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, SidebarCategory]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        team_id=team_id,
        category_id=category_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    user_id: str,
    team_id: str,
    category_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: SidebarCategory,
) -> Optional[Union[AppError, SidebarCategory]]:
    """Update sidebar category

     Updates a single sidebar category for the user on the given team.
    __Minimum server version__: 5.26
    ##### Permissions
    Must be authenticated and have the `list_team_channels` permission.

    Args:
        user_id (str):
        team_id (str):
        category_id (str):
        body (SidebarCategory): User's sidebar category

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, SidebarCategory]
    """

    return sync_detailed(
        user_id=user_id,
        team_id=team_id,
        category_id=category_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    user_id: str,
    team_id: str,
    category_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: SidebarCategory,
) -> Response[Union[AppError, SidebarCategory]]:
    """Update sidebar category

     Updates a single sidebar category for the user on the given team.
    __Minimum server version__: 5.26
    ##### Permissions
    Must be authenticated and have the `list_team_channels` permission.

    Args:
        user_id (str):
        team_id (str):
        category_id (str):
        body (SidebarCategory): User's sidebar category

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, SidebarCategory]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        team_id=team_id,
        category_id=category_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    user_id: str,
    team_id: str,
    category_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: SidebarCategory,
) -> Optional[Union[AppError, SidebarCategory]]:
    """Update sidebar category

     Updates a single sidebar category for the user on the given team.
    __Minimum server version__: 5.26
    ##### Permissions
    Must be authenticated and have the `list_team_channels` permission.

    Args:
        user_id (str):
        team_id (str):
        category_id (str):
        body (SidebarCategory): User's sidebar category

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, SidebarCategory]
    """

    return (
        await asyncio_detailed(
            user_id=user_id,
            team_id=team_id,
            category_id=category_id,
            client=client,
            body=body,
        )
    ).parsed
