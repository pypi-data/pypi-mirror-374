from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.search_teams_body import SearchTeamsBody
from ...models.search_teams_response_200 import SearchTeamsResponse200
from ...types import Response


def _get_kwargs(
    *,
    body: SearchTeamsBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v4/teams/search",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, SearchTeamsResponse200]]:
    if response.status_code == 200:
        response_200 = SearchTeamsResponse200.from_dict(response.json())

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
) -> Response[Union[AppError, SearchTeamsResponse200]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: SearchTeamsBody,
) -> Response[Union[AppError, SearchTeamsResponse200]]:
    r"""Search teams

     Search teams based on search term and options provided in the request body.

    ##### Permissions
    Logged in user only shows open teams
    Logged in user with \"manage_system\" permission shows all teams

    Args:
        body (SearchTeamsBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, SearchTeamsResponse200]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: SearchTeamsBody,
) -> Optional[Union[AppError, SearchTeamsResponse200]]:
    r"""Search teams

     Search teams based on search term and options provided in the request body.

    ##### Permissions
    Logged in user only shows open teams
    Logged in user with \"manage_system\" permission shows all teams

    Args:
        body (SearchTeamsBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, SearchTeamsResponse200]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: SearchTeamsBody,
) -> Response[Union[AppError, SearchTeamsResponse200]]:
    r"""Search teams

     Search teams based on search term and options provided in the request body.

    ##### Permissions
    Logged in user only shows open teams
    Logged in user with \"manage_system\" permission shows all teams

    Args:
        body (SearchTeamsBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, SearchTeamsResponse200]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: SearchTeamsBody,
) -> Optional[Union[AppError, SearchTeamsResponse200]]:
    r"""Search teams

     Search teams based on search term and options provided in the request body.

    ##### Permissions
    Logged in user only shows open teams
    Logged in user with \"manage_system\" permission shows all teams

    Args:
        body (SearchTeamsBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, SearchTeamsResponse200]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
