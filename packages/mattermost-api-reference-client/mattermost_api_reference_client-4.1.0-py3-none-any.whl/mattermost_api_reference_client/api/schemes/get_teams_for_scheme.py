from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.team import Team
from ...types import UNSET, Response, Unset


def _get_kwargs(
    scheme_id: str,
    *,
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["per_page"] = per_page

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v4/schemes/{scheme_id}/teams",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, list["Team"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Team.from_dict(response_200_item_data)

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

    if response.status_code == 404:
        response_404 = AppError.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, list["Team"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    scheme_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
) -> Response[Union[AppError, list["Team"]]]:
    """Get a page of teams which use this scheme.

     Get a page of teams which use this scheme. The provided Scheme ID should be for a Team-scoped
    Scheme.
    Use the query parameters to modify the behaviour of this endpoint.

    ##### Permissions
    `manage_system` permission is required.

    __Minimum server version__: 5.0

    Args:
        scheme_id (str):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['Team']]]
    """

    kwargs = _get_kwargs(
        scheme_id=scheme_id,
        page=page,
        per_page=per_page,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    scheme_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
) -> Optional[Union[AppError, list["Team"]]]:
    """Get a page of teams which use this scheme.

     Get a page of teams which use this scheme. The provided Scheme ID should be for a Team-scoped
    Scheme.
    Use the query parameters to modify the behaviour of this endpoint.

    ##### Permissions
    `manage_system` permission is required.

    __Minimum server version__: 5.0

    Args:
        scheme_id (str):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['Team']]
    """

    return sync_detailed(
        scheme_id=scheme_id,
        client=client,
        page=page,
        per_page=per_page,
    ).parsed


async def asyncio_detailed(
    scheme_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
) -> Response[Union[AppError, list["Team"]]]:
    """Get a page of teams which use this scheme.

     Get a page of teams which use this scheme. The provided Scheme ID should be for a Team-scoped
    Scheme.
    Use the query parameters to modify the behaviour of this endpoint.

    ##### Permissions
    `manage_system` permission is required.

    __Minimum server version__: 5.0

    Args:
        scheme_id (str):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['Team']]]
    """

    kwargs = _get_kwargs(
        scheme_id=scheme_id,
        page=page,
        per_page=per_page,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    scheme_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
) -> Optional[Union[AppError, list["Team"]]]:
    """Get a page of teams which use this scheme.

     Get a page of teams which use this scheme. The provided Scheme ID should be for a Team-scoped
    Scheme.
    Use the query parameters to modify the behaviour of this endpoint.

    ##### Permissions
    `manage_system` permission is required.

    __Minimum server version__: 5.0

    Args:
        scheme_id (str):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['Team']]
    """

    return (
        await asyncio_detailed(
            scheme_id=scheme_id,
            client=client,
            page=page,
            per_page=per_page,
        )
    ).parsed
