from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page: Union[Unset, int] = UNSET,
    per_page: Union[Unset, int] = UNSET,
    filter_: Union[Unset, str] = UNSET,
    server_version: Union[Unset, str] = UNSET,
    local_only: Union[Unset, bool] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["per_page"] = per_page

    params["filter"] = filter_

    params["server_version"] = server_version

    params["local_only"] = local_only

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v4/plugins/marketplace",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[AppError]:
    if response.status_code == 400:
        response_400 = AppError.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = AppError.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = AppError.from_dict(response.json())

        return response_403

    if response.status_code == 501:
        response_501 = AppError.from_dict(response.json())

        return response_501

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[AppError]:
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
    filter_: Union[Unset, str] = UNSET,
    server_version: Union[Unset, str] = UNSET,
    local_only: Union[Unset, bool] = UNSET,
) -> Response[AppError]:
    """Gets all the marketplace plugins

     Gets all plugins from the marketplace server, merging data from locally installed plugins as well as
    prepackaged plugins shipped with the server.

    ##### Permissions
    Must have `manage_system` permission.

    __Minimum server version__: 5.16

    Args:
        page (Union[Unset, int]):
        per_page (Union[Unset, int]):
        filter_ (Union[Unset, str]):
        server_version (Union[Unset, str]):
        local_only (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AppError]
    """

    kwargs = _get_kwargs(
        page=page,
        per_page=per_page,
        filter_=filter_,
        server_version=server_version,
        local_only=local_only,
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
    filter_: Union[Unset, str] = UNSET,
    server_version: Union[Unset, str] = UNSET,
    local_only: Union[Unset, bool] = UNSET,
) -> Optional[AppError]:
    """Gets all the marketplace plugins

     Gets all plugins from the marketplace server, merging data from locally installed plugins as well as
    prepackaged plugins shipped with the server.

    ##### Permissions
    Must have `manage_system` permission.

    __Minimum server version__: 5.16

    Args:
        page (Union[Unset, int]):
        per_page (Union[Unset, int]):
        filter_ (Union[Unset, str]):
        server_version (Union[Unset, str]):
        local_only (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AppError
    """

    return sync_detailed(
        client=client,
        page=page,
        per_page=per_page,
        filter_=filter_,
        server_version=server_version,
        local_only=local_only,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = UNSET,
    per_page: Union[Unset, int] = UNSET,
    filter_: Union[Unset, str] = UNSET,
    server_version: Union[Unset, str] = UNSET,
    local_only: Union[Unset, bool] = UNSET,
) -> Response[AppError]:
    """Gets all the marketplace plugins

     Gets all plugins from the marketplace server, merging data from locally installed plugins as well as
    prepackaged plugins shipped with the server.

    ##### Permissions
    Must have `manage_system` permission.

    __Minimum server version__: 5.16

    Args:
        page (Union[Unset, int]):
        per_page (Union[Unset, int]):
        filter_ (Union[Unset, str]):
        server_version (Union[Unset, str]):
        local_only (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AppError]
    """

    kwargs = _get_kwargs(
        page=page,
        per_page=per_page,
        filter_=filter_,
        server_version=server_version,
        local_only=local_only,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = UNSET,
    per_page: Union[Unset, int] = UNSET,
    filter_: Union[Unset, str] = UNSET,
    server_version: Union[Unset, str] = UNSET,
    local_only: Union[Unset, bool] = UNSET,
) -> Optional[AppError]:
    """Gets all the marketplace plugins

     Gets all plugins from the marketplace server, merging data from locally installed plugins as well as
    prepackaged plugins shipped with the server.

    ##### Permissions
    Must have `manage_system` permission.

    __Minimum server version__: 5.16

    Args:
        page (Union[Unset, int]):
        per_page (Union[Unset, int]):
        filter_ (Union[Unset, str]):
        server_version (Union[Unset, str]):
        local_only (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AppError
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            per_page=per_page,
            filter_=filter_,
            server_version=server_version,
            local_only=local_only,
        )
    ).parsed
