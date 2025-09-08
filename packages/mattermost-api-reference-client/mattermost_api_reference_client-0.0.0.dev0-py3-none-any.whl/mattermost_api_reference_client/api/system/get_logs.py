from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page: Union[Unset, int] = 0,
    logs_per_page: Union[Unset, str] = "10000",
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["logs_per_page"] = logs_per_page

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v4/logs",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, list[str]]]:
    if response.status_code == 200:
        response_200 = cast(list[str], response.json())

        return response_200

    if response.status_code == 403:
        response_403 = AppError.from_dict(response.json())

        return response_403

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, list[str]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 0,
    logs_per_page: Union[Unset, str] = "10000",
) -> Response[Union[AppError, list[str]]]:
    """Get logs

     Get a page of server logs, selected with `page` and `logs_per_page` query parameters.
    ##### Permissions
    Must have `manage_system` permission.

    Args:
        page (Union[Unset, int]):  Default: 0.
        logs_per_page (Union[Unset, str]):  Default: '10000'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list[str]]]
    """

    kwargs = _get_kwargs(
        page=page,
        logs_per_page=logs_per_page,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 0,
    logs_per_page: Union[Unset, str] = "10000",
) -> Optional[Union[AppError, list[str]]]:
    """Get logs

     Get a page of server logs, selected with `page` and `logs_per_page` query parameters.
    ##### Permissions
    Must have `manage_system` permission.

    Args:
        page (Union[Unset, int]):  Default: 0.
        logs_per_page (Union[Unset, str]):  Default: '10000'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list[str]]
    """

    return sync_detailed(
        client=client,
        page=page,
        logs_per_page=logs_per_page,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 0,
    logs_per_page: Union[Unset, str] = "10000",
) -> Response[Union[AppError, list[str]]]:
    """Get logs

     Get a page of server logs, selected with `page` and `logs_per_page` query parameters.
    ##### Permissions
    Must have `manage_system` permission.

    Args:
        page (Union[Unset, int]):  Default: 0.
        logs_per_page (Union[Unset, str]):  Default: '10000'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list[str]]]
    """

    kwargs = _get_kwargs(
        page=page,
        logs_per_page=logs_per_page,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 0,
    logs_per_page: Union[Unset, str] = "10000",
) -> Optional[Union[AppError, list[str]]]:
    """Get logs

     Get a page of server logs, selected with `page` and `logs_per_page` query parameters.
    ##### Permissions
    Must have `manage_system` permission.

    Args:
        page (Union[Unset, int]):  Default: 0.
        logs_per_page (Union[Unset, str]):  Default: '10000'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list[str]]
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            logs_per_page=logs_per_page,
        )
    ).parsed
