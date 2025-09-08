from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.channels_with_count import ChannelsWithCount
from ...types import UNSET, Response, Unset


def _get_kwargs(
    policy_id: str,
    *,
    after: Union[Unset, str] = UNSET,
    limit: int = 60,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["after"] = after

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v4/access_control_policies/{policy_id}/resources/channels",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, ChannelsWithCount]]:
    if response.status_code == 200:
        response_200 = ChannelsWithCount.from_dict(response.json())

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

    if response.status_code == 500:
        response_500 = AppError.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, ChannelsWithCount]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    policy_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    after: Union[Unset, str] = UNSET,
    limit: int = 60,
) -> Response[Union[AppError, ChannelsWithCount]]:
    """Get channels for an access control policy

     Retrieves a paginated list of channels to which a specific access control policy is applied.
    ##### Permissions
    Must have the `manage_system` permission.

    Args:
        policy_id (str):
        after (Union[Unset, str]):
        limit (int):  Default: 60.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, ChannelsWithCount]]
    """

    kwargs = _get_kwargs(
        policy_id=policy_id,
        after=after,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    policy_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    after: Union[Unset, str] = UNSET,
    limit: int = 60,
) -> Optional[Union[AppError, ChannelsWithCount]]:
    """Get channels for an access control policy

     Retrieves a paginated list of channels to which a specific access control policy is applied.
    ##### Permissions
    Must have the `manage_system` permission.

    Args:
        policy_id (str):
        after (Union[Unset, str]):
        limit (int):  Default: 60.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, ChannelsWithCount]
    """

    return sync_detailed(
        policy_id=policy_id,
        client=client,
        after=after,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    policy_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    after: Union[Unset, str] = UNSET,
    limit: int = 60,
) -> Response[Union[AppError, ChannelsWithCount]]:
    """Get channels for an access control policy

     Retrieves a paginated list of channels to which a specific access control policy is applied.
    ##### Permissions
    Must have the `manage_system` permission.

    Args:
        policy_id (str):
        after (Union[Unset, str]):
        limit (int):  Default: 60.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, ChannelsWithCount]]
    """

    kwargs = _get_kwargs(
        policy_id=policy_id,
        after=after,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    policy_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    after: Union[Unset, str] = UNSET,
    limit: int = 60,
) -> Optional[Union[AppError, ChannelsWithCount]]:
    """Get channels for an access control policy

     Retrieves a paginated list of channels to which a specific access control policy is applied.
    ##### Permissions
    Must have the `manage_system` permission.

    Args:
        policy_id (str):
        after (Union[Unset, str]):
        limit (int):  Default: 60.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, ChannelsWithCount]
    """

    return (
        await asyncio_detailed(
            policy_id=policy_id,
            client=client,
            after=after,
            limit=limit,
        )
    ).parsed
