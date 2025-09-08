from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.get_users_by_group_channel_ids_response_200 import GetUsersByGroupChannelIdsResponse200
from ...types import Response


def _get_kwargs(
    *,
    body: list[str],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v4/users/group_channels",
    }

    _kwargs["json"] = body

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, GetUsersByGroupChannelIdsResponse200]]:
    if response.status_code == 200:
        response_200 = GetUsersByGroupChannelIdsResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = AppError.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = AppError.from_dict(response.json())

        return response_401

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, GetUsersByGroupChannelIdsResponse200]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: list[str],
) -> Response[Union[AppError, GetUsersByGroupChannelIdsResponse200]]:
    """Get users by group channels ids

     Get an object containing a key per group channel id in the
    query and its value as a list of users members of that group
    channel.

    The user must be a member of the group ids in the query, or
    they will be omitted from the response.
    ##### Permissions
    Requires an active session but no other permissions.

    __Minimum server version__: 5.14

    Args:
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, GetUsersByGroupChannelIdsResponse200]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: list[str],
) -> Optional[Union[AppError, GetUsersByGroupChannelIdsResponse200]]:
    """Get users by group channels ids

     Get an object containing a key per group channel id in the
    query and its value as a list of users members of that group
    channel.

    The user must be a member of the group ids in the query, or
    they will be omitted from the response.
    ##### Permissions
    Requires an active session but no other permissions.

    __Minimum server version__: 5.14

    Args:
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, GetUsersByGroupChannelIdsResponse200]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: list[str],
) -> Response[Union[AppError, GetUsersByGroupChannelIdsResponse200]]:
    """Get users by group channels ids

     Get an object containing a key per group channel id in the
    query and its value as a list of users members of that group
    channel.

    The user must be a member of the group ids in the query, or
    they will be omitted from the response.
    ##### Permissions
    Requires an active session but no other permissions.

    __Minimum server version__: 5.14

    Args:
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, GetUsersByGroupChannelIdsResponse200]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: list[str],
) -> Optional[Union[AppError, GetUsersByGroupChannelIdsResponse200]]:
    """Get users by group channels ids

     Get an object containing a key per group channel id in the
    query and its value as a list of users members of that group
    channel.

    The user must be a member of the group ids in the query, or
    they will be omitted from the response.
    ##### Permissions
    Requires an active session but no other permissions.

    __Minimum server version__: 5.14

    Args:
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, GetUsersByGroupChannelIdsResponse200]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
