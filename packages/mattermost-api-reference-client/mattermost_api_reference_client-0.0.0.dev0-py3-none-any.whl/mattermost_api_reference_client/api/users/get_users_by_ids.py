from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.user import User
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: list[str],
    since: Union[Unset, int] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["since"] = since

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v4/users/ids",
        "params": params,
    }

    _kwargs["json"] = body

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, list["User"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = User.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[Union[AppError, list["User"]]]:
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
    since: Union[Unset, int] = UNSET,
) -> Response[Union[AppError, list["User"]]]:
    """Get users by ids

     Get a list of users based on a provided list of user ids.
    ##### Permissions
    Requires an active session but no other permissions.

    Args:
        since (Union[Unset, int]):
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['User']]]
    """

    kwargs = _get_kwargs(
        body=body,
        since=since,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: list[str],
    since: Union[Unset, int] = UNSET,
) -> Optional[Union[AppError, list["User"]]]:
    """Get users by ids

     Get a list of users based on a provided list of user ids.
    ##### Permissions
    Requires an active session but no other permissions.

    Args:
        since (Union[Unset, int]):
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['User']]
    """

    return sync_detailed(
        client=client,
        body=body,
        since=since,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: list[str],
    since: Union[Unset, int] = UNSET,
) -> Response[Union[AppError, list["User"]]]:
    """Get users by ids

     Get a list of users based on a provided list of user ids.
    ##### Permissions
    Requires an active session but no other permissions.

    Args:
        since (Union[Unset, int]):
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['User']]]
    """

    kwargs = _get_kwargs(
        body=body,
        since=since,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: list[str],
    since: Union[Unset, int] = UNSET,
) -> Optional[Union[AppError, list["User"]]]:
    """Get users by ids

     Get a list of users based on a provided list of user ids.
    ##### Permissions
    Requires an active session but no other permissions.

    Args:
        since (Union[Unset, int]):
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['User']]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            since=since,
        )
    ).parsed
