from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.channel_search import ChannelSearch
from ...models.channels_with_count import ChannelsWithCount
from ...types import Response


def _get_kwargs(
    policy_id: str,
    *,
    body: ChannelSearch,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v4/access_control_policies/{policy_id}/resources/channels/search",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
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
    body: ChannelSearch,
) -> Response[Union[AppError, ChannelsWithCount]]:
    """Search channels for an access control policy

     Searches for channels associated with a specific access control policy based on search criteria.
    ##### Permissions
    Must have the `manage_system` permission.

    Args:
        policy_id (str):
        body (ChannelSearch):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, ChannelsWithCount]]
    """

    kwargs = _get_kwargs(
        policy_id=policy_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    policy_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ChannelSearch,
) -> Optional[Union[AppError, ChannelsWithCount]]:
    """Search channels for an access control policy

     Searches for channels associated with a specific access control policy based on search criteria.
    ##### Permissions
    Must have the `manage_system` permission.

    Args:
        policy_id (str):
        body (ChannelSearch):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, ChannelsWithCount]
    """

    return sync_detailed(
        policy_id=policy_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    policy_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ChannelSearch,
) -> Response[Union[AppError, ChannelsWithCount]]:
    """Search channels for an access control policy

     Searches for channels associated with a specific access control policy based on search criteria.
    ##### Permissions
    Must have the `manage_system` permission.

    Args:
        policy_id (str):
        body (ChannelSearch):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, ChannelsWithCount]]
    """

    kwargs = _get_kwargs(
        policy_id=policy_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    policy_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ChannelSearch,
) -> Optional[Union[AppError, ChannelsWithCount]]:
    """Search channels for an access control policy

     Searches for channels associated with a specific access control policy based on search criteria.
    ##### Permissions
    Must have the `manage_system` permission.

    Args:
        policy_id (str):
        body (ChannelSearch):

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
            body=body,
        )
    ).parsed
