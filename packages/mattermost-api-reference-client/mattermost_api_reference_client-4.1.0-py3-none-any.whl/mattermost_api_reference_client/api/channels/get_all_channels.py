from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.channel_with_team_data import ChannelWithTeamData
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    not_associated_to_group: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 0,
    exclude_default_channels: Union[Unset, bool] = False,
    include_deleted: Union[Unset, bool] = False,
    include_total_count: Union[Unset, bool] = False,
    exclude_policy_constrained: Union[Unset, bool] = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["not_associated_to_group"] = not_associated_to_group

    params["page"] = page

    params["per_page"] = per_page

    params["exclude_default_channels"] = exclude_default_channels

    params["include_deleted"] = include_deleted

    params["include_total_count"] = include_total_count

    params["exclude_policy_constrained"] = exclude_policy_constrained

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v4/channels",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, list["ChannelWithTeamData"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for componentsschemas_channel_list_with_team_data_item_data in _response_200:
            componentsschemas_channel_list_with_team_data_item = ChannelWithTeamData.from_dict(
                componentsschemas_channel_list_with_team_data_item_data
            )

            response_200.append(componentsschemas_channel_list_with_team_data_item)

        return response_200

    if response.status_code == 400:
        response_400 = AppError.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = AppError.from_dict(response.json())

        return response_401

    if response.status_code == 404:
        response_404 = AppError.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, list["ChannelWithTeamData"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    not_associated_to_group: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 0,
    exclude_default_channels: Union[Unset, bool] = False,
    include_deleted: Union[Unset, bool] = False,
    include_total_count: Union[Unset, bool] = False,
    exclude_policy_constrained: Union[Unset, bool] = False,
) -> Response[Union[AppError, list["ChannelWithTeamData"]]]:
    """Get a list of all channels

     ##### Permissions
    `manage_system`

    Args:
        not_associated_to_group (Union[Unset, str]):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 0.
        exclude_default_channels (Union[Unset, bool]):  Default: False.
        include_deleted (Union[Unset, bool]):  Default: False.
        include_total_count (Union[Unset, bool]):  Default: False.
        exclude_policy_constrained (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['ChannelWithTeamData']]]
    """

    kwargs = _get_kwargs(
        not_associated_to_group=not_associated_to_group,
        page=page,
        per_page=per_page,
        exclude_default_channels=exclude_default_channels,
        include_deleted=include_deleted,
        include_total_count=include_total_count,
        exclude_policy_constrained=exclude_policy_constrained,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    not_associated_to_group: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 0,
    exclude_default_channels: Union[Unset, bool] = False,
    include_deleted: Union[Unset, bool] = False,
    include_total_count: Union[Unset, bool] = False,
    exclude_policy_constrained: Union[Unset, bool] = False,
) -> Optional[Union[AppError, list["ChannelWithTeamData"]]]:
    """Get a list of all channels

     ##### Permissions
    `manage_system`

    Args:
        not_associated_to_group (Union[Unset, str]):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 0.
        exclude_default_channels (Union[Unset, bool]):  Default: False.
        include_deleted (Union[Unset, bool]):  Default: False.
        include_total_count (Union[Unset, bool]):  Default: False.
        exclude_policy_constrained (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['ChannelWithTeamData']]
    """

    return sync_detailed(
        client=client,
        not_associated_to_group=not_associated_to_group,
        page=page,
        per_page=per_page,
        exclude_default_channels=exclude_default_channels,
        include_deleted=include_deleted,
        include_total_count=include_total_count,
        exclude_policy_constrained=exclude_policy_constrained,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    not_associated_to_group: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 0,
    exclude_default_channels: Union[Unset, bool] = False,
    include_deleted: Union[Unset, bool] = False,
    include_total_count: Union[Unset, bool] = False,
    exclude_policy_constrained: Union[Unset, bool] = False,
) -> Response[Union[AppError, list["ChannelWithTeamData"]]]:
    """Get a list of all channels

     ##### Permissions
    `manage_system`

    Args:
        not_associated_to_group (Union[Unset, str]):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 0.
        exclude_default_channels (Union[Unset, bool]):  Default: False.
        include_deleted (Union[Unset, bool]):  Default: False.
        include_total_count (Union[Unset, bool]):  Default: False.
        exclude_policy_constrained (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['ChannelWithTeamData']]]
    """

    kwargs = _get_kwargs(
        not_associated_to_group=not_associated_to_group,
        page=page,
        per_page=per_page,
        exclude_default_channels=exclude_default_channels,
        include_deleted=include_deleted,
        include_total_count=include_total_count,
        exclude_policy_constrained=exclude_policy_constrained,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    not_associated_to_group: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 0,
    exclude_default_channels: Union[Unset, bool] = False,
    include_deleted: Union[Unset, bool] = False,
    include_total_count: Union[Unset, bool] = False,
    exclude_policy_constrained: Union[Unset, bool] = False,
) -> Optional[Union[AppError, list["ChannelWithTeamData"]]]:
    """Get a list of all channels

     ##### Permissions
    `manage_system`

    Args:
        not_associated_to_group (Union[Unset, str]):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 0.
        exclude_default_channels (Union[Unset, bool]):  Default: False.
        include_deleted (Union[Unset, bool]):  Default: False.
        include_total_count (Union[Unset, bool]):  Default: False.
        exclude_policy_constrained (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['ChannelWithTeamData']]
    """

    return (
        await asyncio_detailed(
            client=client,
            not_associated_to_group=not_associated_to_group,
            page=page,
            per_page=per_page,
            exclude_default_channels=exclude_default_channels,
            include_deleted=include_deleted,
            include_total_count=include_total_count,
            exclude_policy_constrained=exclude_policy_constrained,
        )
    ).parsed
