from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    channel_id: str,
    *,
    include_timezones: Union[Unset, bool] = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["include_timezones"] = include_timezones

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v4/channels/{channel_id}/member_counts_by_group",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, AppError]]:
    if response.status_code == 200:
        response_200 = cast(Any, None)
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
) -> Response[Union[Any, AppError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    channel_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_timezones: Union[Unset, bool] = False,
) -> Response[Union[Any, AppError]]:
    """Channel members counts for each group that has atleast one member in the channel

     Returns a set of ChannelMemberCountByGroup objects which contain a `group_id`,
    `channel_member_count` and a `channel_member_timezones_count`.
    ##### Permissions
    Must have `read_channel` permission for the given channel.
    __Minimum server version__: 5.24

    Args:
        channel_id (str):
        include_timezones (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, AppError]]
    """

    kwargs = _get_kwargs(
        channel_id=channel_id,
        include_timezones=include_timezones,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    channel_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_timezones: Union[Unset, bool] = False,
) -> Optional[Union[Any, AppError]]:
    """Channel members counts for each group that has atleast one member in the channel

     Returns a set of ChannelMemberCountByGroup objects which contain a `group_id`,
    `channel_member_count` and a `channel_member_timezones_count`.
    ##### Permissions
    Must have `read_channel` permission for the given channel.
    __Minimum server version__: 5.24

    Args:
        channel_id (str):
        include_timezones (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, AppError]
    """

    return sync_detailed(
        channel_id=channel_id,
        client=client,
        include_timezones=include_timezones,
    ).parsed


async def asyncio_detailed(
    channel_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_timezones: Union[Unset, bool] = False,
) -> Response[Union[Any, AppError]]:
    """Channel members counts for each group that has atleast one member in the channel

     Returns a set of ChannelMemberCountByGroup objects which contain a `group_id`,
    `channel_member_count` and a `channel_member_timezones_count`.
    ##### Permissions
    Must have `read_channel` permission for the given channel.
    __Minimum server version__: 5.24

    Args:
        channel_id (str):
        include_timezones (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, AppError]]
    """

    kwargs = _get_kwargs(
        channel_id=channel_id,
        include_timezones=include_timezones,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    channel_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_timezones: Union[Unset, bool] = False,
) -> Optional[Union[Any, AppError]]:
    """Channel members counts for each group that has atleast one member in the channel

     Returns a set of ChannelMemberCountByGroup objects which contain a `group_id`,
    `channel_member_count` and a `channel_member_timezones_count`.
    ##### Permissions
    Must have `read_channel` permission for the given channel.
    __Minimum server version__: 5.24

    Args:
        channel_id (str):
        include_timezones (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, AppError]
    """

    return (
        await asyncio_detailed(
            channel_id=channel_id,
            client=client,
            include_timezones=include_timezones,
        )
    ).parsed
