from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.bot import Bot
from ...types import UNSET, Response, Unset


def _get_kwargs(
    bot_user_id: str,
    *,
    include_deleted: Union[Unset, bool] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["include_deleted"] = include_deleted

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v4/bots/{bot_user_id}",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, Bot]]:
    if response.status_code == 200:
        response_200 = Bot.from_dict(response.json())

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
) -> Response[Union[AppError, Bot]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    bot_user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_deleted: Union[Unset, bool] = UNSET,
) -> Response[Union[AppError, Bot]]:
    """Get a bot

     Get a bot specified by its bot id.
    ##### Permissions
    Must have `read_bots` permission for bots you are managing, and `read_others_bots` permission for
    bots others are managing.
    __Minimum server version__: 5.10

    Args:
        bot_user_id (str):
        include_deleted (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, Bot]]
    """

    kwargs = _get_kwargs(
        bot_user_id=bot_user_id,
        include_deleted=include_deleted,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    bot_user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_deleted: Union[Unset, bool] = UNSET,
) -> Optional[Union[AppError, Bot]]:
    """Get a bot

     Get a bot specified by its bot id.
    ##### Permissions
    Must have `read_bots` permission for bots you are managing, and `read_others_bots` permission for
    bots others are managing.
    __Minimum server version__: 5.10

    Args:
        bot_user_id (str):
        include_deleted (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, Bot]
    """

    return sync_detailed(
        bot_user_id=bot_user_id,
        client=client,
        include_deleted=include_deleted,
    ).parsed


async def asyncio_detailed(
    bot_user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_deleted: Union[Unset, bool] = UNSET,
) -> Response[Union[AppError, Bot]]:
    """Get a bot

     Get a bot specified by its bot id.
    ##### Permissions
    Must have `read_bots` permission for bots you are managing, and `read_others_bots` permission for
    bots others are managing.
    __Minimum server version__: 5.10

    Args:
        bot_user_id (str):
        include_deleted (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, Bot]]
    """

    kwargs = _get_kwargs(
        bot_user_id=bot_user_id,
        include_deleted=include_deleted,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    bot_user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_deleted: Union[Unset, bool] = UNSET,
) -> Optional[Union[AppError, Bot]]:
    """Get a bot

     Get a bot specified by its bot id.
    ##### Permissions
    Must have `read_bots` permission for bots you are managing, and `read_others_bots` permission for
    bots others are managing.
    __Minimum server version__: 5.10

    Args:
        bot_user_id (str):
        include_deleted (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, Bot]
    """

    return (
        await asyncio_detailed(
            bot_user_id=bot_user_id,
            client=client,
            include_deleted=include_deleted,
        )
    ).parsed
