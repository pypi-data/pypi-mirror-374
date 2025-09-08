from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.team import Team
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
    include_total_count: Union[Unset, bool] = False,
    exclude_policy_constrained: Union[Unset, bool] = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["per_page"] = per_page

    params["include_total_count"] = include_total_count

    params["exclude_policy_constrained"] = exclude_policy_constrained

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v4/teams",
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
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
    include_total_count: Union[Unset, bool] = False,
    exclude_policy_constrained: Union[Unset, bool] = False,
) -> Response[Union[AppError, list["Team"]]]:
    r"""Get teams

     For regular users only returns open teams. Users with the \"manage_system\" permission will return
    teams regardless of type. The result is based on query string parameters - page and per_page.
    ##### Permissions
    Must be authenticated. \"manage_system\" permission is required to show all teams.

    Args:
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.
        include_total_count (Union[Unset, bool]):  Default: False.
        exclude_policy_constrained (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['Team']]]
    """

    kwargs = _get_kwargs(
        page=page,
        per_page=per_page,
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
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
    include_total_count: Union[Unset, bool] = False,
    exclude_policy_constrained: Union[Unset, bool] = False,
) -> Optional[Union[AppError, list["Team"]]]:
    r"""Get teams

     For regular users only returns open teams. Users with the \"manage_system\" permission will return
    teams regardless of type. The result is based on query string parameters - page and per_page.
    ##### Permissions
    Must be authenticated. \"manage_system\" permission is required to show all teams.

    Args:
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.
        include_total_count (Union[Unset, bool]):  Default: False.
        exclude_policy_constrained (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['Team']]
    """

    return sync_detailed(
        client=client,
        page=page,
        per_page=per_page,
        include_total_count=include_total_count,
        exclude_policy_constrained=exclude_policy_constrained,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
    include_total_count: Union[Unset, bool] = False,
    exclude_policy_constrained: Union[Unset, bool] = False,
) -> Response[Union[AppError, list["Team"]]]:
    r"""Get teams

     For regular users only returns open teams. Users with the \"manage_system\" permission will return
    teams regardless of type. The result is based on query string parameters - page and per_page.
    ##### Permissions
    Must be authenticated. \"manage_system\" permission is required to show all teams.

    Args:
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.
        include_total_count (Union[Unset, bool]):  Default: False.
        exclude_policy_constrained (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['Team']]]
    """

    kwargs = _get_kwargs(
        page=page,
        per_page=per_page,
        include_total_count=include_total_count,
        exclude_policy_constrained=exclude_policy_constrained,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
    include_total_count: Union[Unset, bool] = False,
    exclude_policy_constrained: Union[Unset, bool] = False,
) -> Optional[Union[AppError, list["Team"]]]:
    r"""Get teams

     For regular users only returns open teams. Users with the \"manage_system\" permission will return
    teams regardless of type. The result is based on query string parameters - page and per_page.
    ##### Permissions
    Must be authenticated. \"manage_system\" permission is required to show all teams.

    Args:
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.
        include_total_count (Union[Unset, bool]):  Default: False.
        exclude_policy_constrained (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['Team']]
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            per_page=per_page,
            include_total_count=include_total_count,
            exclude_policy_constrained=exclude_policy_constrained,
        )
    ).parsed
