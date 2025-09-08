from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.get_group_stats_response_200 import GetGroupStatsResponse200
from ...types import Response


def _get_kwargs(
    group_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v4/groups/{group_id}/stats",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, GetGroupStatsResponse200]]:
    if response.status_code == 200:
        response_200 = GetGroupStatsResponse200.from_dict(response.json())

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

    if response.status_code == 500:
        response_500 = AppError.from_dict(response.json())

        return response_500

    if response.status_code == 501:
        response_501 = AppError.from_dict(response.json())

        return response_501

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, GetGroupStatsResponse200]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    group_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, GetGroupStatsResponse200]]:
    """Get group stats

     Retrieve the stats of a given group.

    ##### Permissions
    Must have `manage_system` permission.

    __Minimum server version__: 5.26

    Args:
        group_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, GetGroupStatsResponse200]]
    """

    kwargs = _get_kwargs(
        group_id=group_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    group_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, GetGroupStatsResponse200]]:
    """Get group stats

     Retrieve the stats of a given group.

    ##### Permissions
    Must have `manage_system` permission.

    __Minimum server version__: 5.26

    Args:
        group_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, GetGroupStatsResponse200]
    """

    return sync_detailed(
        group_id=group_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    group_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, GetGroupStatsResponse200]]:
    """Get group stats

     Retrieve the stats of a given group.

    ##### Permissions
    Must have `manage_system` permission.

    __Minimum server version__: 5.26

    Args:
        group_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, GetGroupStatsResponse200]]
    """

    kwargs = _get_kwargs(
        group_id=group_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    group_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, GetGroupStatsResponse200]]:
    """Get group stats

     Retrieve the stats of a given group.

    ##### Permissions
    Must have `manage_system` permission.

    __Minimum server version__: 5.26

    Args:
        group_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, GetGroupStatsResponse200]
    """

    return (
        await asyncio_detailed(
            group_id=group_id,
            client=client,
        )
    ).parsed
