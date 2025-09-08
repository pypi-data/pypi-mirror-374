from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.ldap_groups_paged import LDAPGroupsPaged
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    q: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["q"] = q

    params["page"] = page

    params["per_page"] = per_page

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v4/ldap/groups",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, list["LDAPGroupsPaged"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = LDAPGroupsPaged.from_dict(response_200_item_data)

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
) -> Response[Union[AppError, list["LDAPGroupsPaged"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    q: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
) -> Response[Union[AppError, list["LDAPGroupsPaged"]]]:
    """Returns a list of LDAP groups

     ##### Permissions
    Must have `manage_system` permission.
    __Minimum server version__: 5.11

    Args:
        q (Union[Unset, str]):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['LDAPGroupsPaged']]]
    """

    kwargs = _get_kwargs(
        q=q,
        page=page,
        per_page=per_page,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    q: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
) -> Optional[Union[AppError, list["LDAPGroupsPaged"]]]:
    """Returns a list of LDAP groups

     ##### Permissions
    Must have `manage_system` permission.
    __Minimum server version__: 5.11

    Args:
        q (Union[Unset, str]):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['LDAPGroupsPaged']]
    """

    return sync_detailed(
        client=client,
        q=q,
        page=page,
        per_page=per_page,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    q: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
) -> Response[Union[AppError, list["LDAPGroupsPaged"]]]:
    """Returns a list of LDAP groups

     ##### Permissions
    Must have `manage_system` permission.
    __Minimum server version__: 5.11

    Args:
        q (Union[Unset, str]):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['LDAPGroupsPaged']]]
    """

    kwargs = _get_kwargs(
        q=q,
        page=page,
        per_page=per_page,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    q: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
) -> Optional[Union[AppError, list["LDAPGroupsPaged"]]]:
    """Returns a list of LDAP groups

     ##### Permissions
    Must have `manage_system` permission.
    __Minimum server version__: 5.11

    Args:
        q (Union[Unset, str]):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['LDAPGroupsPaged']]
    """

    return (
        await asyncio_detailed(
            client=client,
            q=q,
            page=page,
            per_page=per_page,
        )
    ).parsed
