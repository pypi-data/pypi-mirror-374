from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.emoji import Emoji
from ...types import Response


def _get_kwargs(
    emoji_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": f"/api/v4/emoji/{emoji_id}",
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
    emoji_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, Emoji]]:
    """Delete a custom emoji

     Delete a custom emoji.
    ##### Permissions
    Must have the `manage_team` or `manage_system` permissions or be the user who created the emoji.

    Args:
        emoji_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, Emoji]]
    """

    kwargs = _get_kwargs(
        emoji_id=emoji_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    emoji_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, Emoji]]:
    """Delete a custom emoji

     Delete a custom emoji.
    ##### Permissions
    Must have the `manage_team` or `manage_system` permissions or be the user who created the emoji.

    Args:
        emoji_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, Emoji]
    """

    return sync_detailed(
        emoji_id=emoji_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    emoji_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, Emoji]]:
    """Delete a custom emoji

     Delete a custom emoji.
    ##### Permissions
    Must have the `manage_team` or `manage_system` permissions or be the user who created the emoji.

    Args:
        emoji_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, Emoji]]
    """

    kwargs = _get_kwargs(
        emoji_id=emoji_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    emoji_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, Emoji]]:
    """Delete a custom emoji

     Delete a custom emoji.
    ##### Permissions
    Must have the `manage_team` or `manage_system` permissions or be the user who created the emoji.

    Args:
        emoji_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, Emoji]
    """

    return (
        await asyncio_detailed(
            emoji_id=emoji_id,
            client=client,
        )
    ).parsed
