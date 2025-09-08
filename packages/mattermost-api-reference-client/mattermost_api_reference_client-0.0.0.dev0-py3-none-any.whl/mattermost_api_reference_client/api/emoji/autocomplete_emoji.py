from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.emoji import Emoji
from ...types import UNSET, Response


def _get_kwargs(
    *,
    name: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["name"] = name

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v4/emoji/autocomplete",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, Emoji]]:
    if response.status_code == 200:
        response_200 = Emoji.from_dict(response.json())

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

    if response.status_code == 501:
        response_501 = AppError.from_dict(response.json())

        return response_501

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, Emoji]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    name: str,
) -> Response[Union[AppError, Emoji]]:
    """Autocomplete custom emoji

     Get a list of custom emoji with names starting with or matching the provided name. Returns a maximum
    of 100 results.
    ##### Permissions
    Must be authenticated.

    __Minimum server version__: 4.7

    Args:
        name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, Emoji]]
    """

    kwargs = _get_kwargs(
        name=name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    name: str,
) -> Optional[Union[AppError, Emoji]]:
    """Autocomplete custom emoji

     Get a list of custom emoji with names starting with or matching the provided name. Returns a maximum
    of 100 results.
    ##### Permissions
    Must be authenticated.

    __Minimum server version__: 4.7

    Args:
        name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, Emoji]
    """

    return sync_detailed(
        client=client,
        name=name,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    name: str,
) -> Response[Union[AppError, Emoji]]:
    """Autocomplete custom emoji

     Get a list of custom emoji with names starting with or matching the provided name. Returns a maximum
    of 100 results.
    ##### Permissions
    Must be authenticated.

    __Minimum server version__: 4.7

    Args:
        name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, Emoji]]
    """

    kwargs = _get_kwargs(
        name=name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    name: str,
) -> Optional[Union[AppError, Emoji]]:
    """Autocomplete custom emoji

     Get a list of custom emoji with names starting with or matching the provided name. Returns a maximum
    of 100 results.
    ##### Permissions
    Must be authenticated.

    __Minimum server version__: 4.7

    Args:
        name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, Emoji]
    """

    return (
        await asyncio_detailed(
            client=client,
            name=name,
        )
    ).parsed
