from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.remote_cluster import RemoteCluster
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page: Union[Unset, int] = UNSET,
    per_page: Union[Unset, int] = UNSET,
    exclude_offline: Union[Unset, bool] = UNSET,
    in_channel: Union[Unset, str] = UNSET,
    not_in_channel: Union[Unset, str] = UNSET,
    only_confirmed: Union[Unset, bool] = UNSET,
    only_plugins: Union[Unset, bool] = UNSET,
    exclude_plugins: Union[Unset, bool] = UNSET,
    include_deleted: Union[Unset, bool] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["per_page"] = per_page

    params["exclude_offline"] = exclude_offline

    params["in_channel"] = in_channel

    params["not_in_channel"] = not_in_channel

    params["only_confirmed"] = only_confirmed

    params["only_plugins"] = only_plugins

    params["exclude_plugins"] = exclude_plugins

    params["include_deleted"] = include_deleted

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v4/remotecluster",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, list["RemoteCluster"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = RemoteCluster.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

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
) -> Response[Union[AppError, list["RemoteCluster"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = UNSET,
    per_page: Union[Unset, int] = UNSET,
    exclude_offline: Union[Unset, bool] = UNSET,
    in_channel: Union[Unset, str] = UNSET,
    not_in_channel: Union[Unset, str] = UNSET,
    only_confirmed: Union[Unset, bool] = UNSET,
    only_plugins: Union[Unset, bool] = UNSET,
    exclude_plugins: Union[Unset, bool] = UNSET,
    include_deleted: Union[Unset, bool] = UNSET,
) -> Response[Union[AppError, list["RemoteCluster"]]]:
    """Get a list of remote clusters.

     Get a list of remote clusters.

    ##### Permissions
    `manage_secure_connections`

    Args:
        page (Union[Unset, int]):
        per_page (Union[Unset, int]):
        exclude_offline (Union[Unset, bool]):
        in_channel (Union[Unset, str]):
        not_in_channel (Union[Unset, str]):
        only_confirmed (Union[Unset, bool]):
        only_plugins (Union[Unset, bool]):
        exclude_plugins (Union[Unset, bool]):
        include_deleted (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['RemoteCluster']]]
    """

    kwargs = _get_kwargs(
        page=page,
        per_page=per_page,
        exclude_offline=exclude_offline,
        in_channel=in_channel,
        not_in_channel=not_in_channel,
        only_confirmed=only_confirmed,
        only_plugins=only_plugins,
        exclude_plugins=exclude_plugins,
        include_deleted=include_deleted,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = UNSET,
    per_page: Union[Unset, int] = UNSET,
    exclude_offline: Union[Unset, bool] = UNSET,
    in_channel: Union[Unset, str] = UNSET,
    not_in_channel: Union[Unset, str] = UNSET,
    only_confirmed: Union[Unset, bool] = UNSET,
    only_plugins: Union[Unset, bool] = UNSET,
    exclude_plugins: Union[Unset, bool] = UNSET,
    include_deleted: Union[Unset, bool] = UNSET,
) -> Optional[Union[AppError, list["RemoteCluster"]]]:
    """Get a list of remote clusters.

     Get a list of remote clusters.

    ##### Permissions
    `manage_secure_connections`

    Args:
        page (Union[Unset, int]):
        per_page (Union[Unset, int]):
        exclude_offline (Union[Unset, bool]):
        in_channel (Union[Unset, str]):
        not_in_channel (Union[Unset, str]):
        only_confirmed (Union[Unset, bool]):
        only_plugins (Union[Unset, bool]):
        exclude_plugins (Union[Unset, bool]):
        include_deleted (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['RemoteCluster']]
    """

    return sync_detailed(
        client=client,
        page=page,
        per_page=per_page,
        exclude_offline=exclude_offline,
        in_channel=in_channel,
        not_in_channel=not_in_channel,
        only_confirmed=only_confirmed,
        only_plugins=only_plugins,
        exclude_plugins=exclude_plugins,
        include_deleted=include_deleted,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = UNSET,
    per_page: Union[Unset, int] = UNSET,
    exclude_offline: Union[Unset, bool] = UNSET,
    in_channel: Union[Unset, str] = UNSET,
    not_in_channel: Union[Unset, str] = UNSET,
    only_confirmed: Union[Unset, bool] = UNSET,
    only_plugins: Union[Unset, bool] = UNSET,
    exclude_plugins: Union[Unset, bool] = UNSET,
    include_deleted: Union[Unset, bool] = UNSET,
) -> Response[Union[AppError, list["RemoteCluster"]]]:
    """Get a list of remote clusters.

     Get a list of remote clusters.

    ##### Permissions
    `manage_secure_connections`

    Args:
        page (Union[Unset, int]):
        per_page (Union[Unset, int]):
        exclude_offline (Union[Unset, bool]):
        in_channel (Union[Unset, str]):
        not_in_channel (Union[Unset, str]):
        only_confirmed (Union[Unset, bool]):
        only_plugins (Union[Unset, bool]):
        exclude_plugins (Union[Unset, bool]):
        include_deleted (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['RemoteCluster']]]
    """

    kwargs = _get_kwargs(
        page=page,
        per_page=per_page,
        exclude_offline=exclude_offline,
        in_channel=in_channel,
        not_in_channel=not_in_channel,
        only_confirmed=only_confirmed,
        only_plugins=only_plugins,
        exclude_plugins=exclude_plugins,
        include_deleted=include_deleted,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = UNSET,
    per_page: Union[Unset, int] = UNSET,
    exclude_offline: Union[Unset, bool] = UNSET,
    in_channel: Union[Unset, str] = UNSET,
    not_in_channel: Union[Unset, str] = UNSET,
    only_confirmed: Union[Unset, bool] = UNSET,
    only_plugins: Union[Unset, bool] = UNSET,
    exclude_plugins: Union[Unset, bool] = UNSET,
    include_deleted: Union[Unset, bool] = UNSET,
) -> Optional[Union[AppError, list["RemoteCluster"]]]:
    """Get a list of remote clusters.

     Get a list of remote clusters.

    ##### Permissions
    `manage_secure_connections`

    Args:
        page (Union[Unset, int]):
        per_page (Union[Unset, int]):
        exclude_offline (Union[Unset, bool]):
        in_channel (Union[Unset, str]):
        not_in_channel (Union[Unset, str]):
        only_confirmed (Union[Unset, bool]):
        only_plugins (Union[Unset, bool]):
        exclude_plugins (Union[Unset, bool]):
        include_deleted (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['RemoteCluster']]
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            per_page=per_page,
            exclude_offline=exclude_offline,
            in_channel=in_channel,
            not_in_channel=not_in_channel,
            only_confirmed=only_confirmed,
            only_plugins=only_plugins,
            exclude_plugins=exclude_plugins,
            include_deleted=include_deleted,
        )
    ).parsed
