from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.incoming_webhook import IncomingWebhook
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
    team_id: Union[Unset, str] = UNSET,
    include_total_count: Union[Unset, bool] = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["per_page"] = per_page

    params["team_id"] = team_id

    params["include_total_count"] = include_total_count

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v4/hooks/incoming",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, list["IncomingWebhook"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = IncomingWebhook.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[Union[AppError, list["IncomingWebhook"]]]:
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
    per_page: Union[Unset, int] = 60,
    team_id: Union[Unset, str] = UNSET,
    include_total_count: Union[Unset, bool] = False,
) -> Response[Union[AppError, list["IncomingWebhook"]]]:
    """List incoming webhooks

     Get a page of a list of incoming webhooks. Optionally filter for a specific team using query
    parameters.
    ##### Permissions
    `manage_webhooks` for the system or `manage_webhooks` for the specific team.

    Args:
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.
        team_id (Union[Unset, str]):
        include_total_count (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['IncomingWebhook']]]
    """

    kwargs = _get_kwargs(
        page=page,
        per_page=per_page,
        team_id=team_id,
        include_total_count=include_total_count,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
    team_id: Union[Unset, str] = UNSET,
    include_total_count: Union[Unset, bool] = False,
) -> Optional[Union[AppError, list["IncomingWebhook"]]]:
    """List incoming webhooks

     Get a page of a list of incoming webhooks. Optionally filter for a specific team using query
    parameters.
    ##### Permissions
    `manage_webhooks` for the system or `manage_webhooks` for the specific team.

    Args:
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.
        team_id (Union[Unset, str]):
        include_total_count (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['IncomingWebhook']]
    """

    return sync_detailed(
        client=client,
        page=page,
        per_page=per_page,
        team_id=team_id,
        include_total_count=include_total_count,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
    team_id: Union[Unset, str] = UNSET,
    include_total_count: Union[Unset, bool] = False,
) -> Response[Union[AppError, list["IncomingWebhook"]]]:
    """List incoming webhooks

     Get a page of a list of incoming webhooks. Optionally filter for a specific team using query
    parameters.
    ##### Permissions
    `manage_webhooks` for the system or `manage_webhooks` for the specific team.

    Args:
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.
        team_id (Union[Unset, str]):
        include_total_count (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['IncomingWebhook']]]
    """

    kwargs = _get_kwargs(
        page=page,
        per_page=per_page,
        team_id=team_id,
        include_total_count=include_total_count,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
    team_id: Union[Unset, str] = UNSET,
    include_total_count: Union[Unset, bool] = False,
) -> Optional[Union[AppError, list["IncomingWebhook"]]]:
    """List incoming webhooks

     Get a page of a list of incoming webhooks. Optionally filter for a specific team using query
    parameters.
    ##### Permissions
    `manage_webhooks` for the system or `manage_webhooks` for the specific team.

    Args:
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.
        team_id (Union[Unset, str]):
        include_total_count (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['IncomingWebhook']]
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            per_page=per_page,
            team_id=team_id,
            include_total_count=include_total_count,
        )
    ).parsed
