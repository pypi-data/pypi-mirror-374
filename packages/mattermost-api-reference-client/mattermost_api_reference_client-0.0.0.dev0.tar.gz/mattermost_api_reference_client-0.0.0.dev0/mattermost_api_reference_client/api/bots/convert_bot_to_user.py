from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.convert_bot_to_user_body import ConvertBotToUserBody
from ...models.status_ok import StatusOK
from ...types import UNSET, Response, Unset


def _get_kwargs(
    bot_user_id: str,
    *,
    body: ConvertBotToUserBody,
    set_system_admin: Union[Unset, bool] = False,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["set_system_admin"] = set_system_admin

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v4/bots/{bot_user_id}/convert_to_user",
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, StatusOK]]:
    if response.status_code == 200:
        response_200 = StatusOK.from_dict(response.json())

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
) -> Response[Union[AppError, StatusOK]]:
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
    body: ConvertBotToUserBody,
    set_system_admin: Union[Unset, bool] = False,
) -> Response[Union[AppError, StatusOK]]:
    """Convert a bot into a user

     Convert a bot into a user.

    __Minimum server version__: 5.26

    ##### Permissions
    Must have `manage_system` permission.

    Args:
        bot_user_id (str):
        set_system_admin (Union[Unset, bool]):  Default: False.
        body (ConvertBotToUserBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, StatusOK]]
    """

    kwargs = _get_kwargs(
        bot_user_id=bot_user_id,
        body=body,
        set_system_admin=set_system_admin,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    bot_user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ConvertBotToUserBody,
    set_system_admin: Union[Unset, bool] = False,
) -> Optional[Union[AppError, StatusOK]]:
    """Convert a bot into a user

     Convert a bot into a user.

    __Minimum server version__: 5.26

    ##### Permissions
    Must have `manage_system` permission.

    Args:
        bot_user_id (str):
        set_system_admin (Union[Unset, bool]):  Default: False.
        body (ConvertBotToUserBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, StatusOK]
    """

    return sync_detailed(
        bot_user_id=bot_user_id,
        client=client,
        body=body,
        set_system_admin=set_system_admin,
    ).parsed


async def asyncio_detailed(
    bot_user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ConvertBotToUserBody,
    set_system_admin: Union[Unset, bool] = False,
) -> Response[Union[AppError, StatusOK]]:
    """Convert a bot into a user

     Convert a bot into a user.

    __Minimum server version__: 5.26

    ##### Permissions
    Must have `manage_system` permission.

    Args:
        bot_user_id (str):
        set_system_admin (Union[Unset, bool]):  Default: False.
        body (ConvertBotToUserBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, StatusOK]]
    """

    kwargs = _get_kwargs(
        bot_user_id=bot_user_id,
        body=body,
        set_system_admin=set_system_admin,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    bot_user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ConvertBotToUserBody,
    set_system_admin: Union[Unset, bool] = False,
) -> Optional[Union[AppError, StatusOK]]:
    """Convert a bot into a user

     Convert a bot into a user.

    __Minimum server version__: 5.26

    ##### Permissions
    Must have `manage_system` permission.

    Args:
        bot_user_id (str):
        set_system_admin (Union[Unset, bool]):  Default: False.
        body (ConvertBotToUserBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, StatusOK]
    """

    return (
        await asyncio_detailed(
            bot_user_id=bot_user_id,
            client=client,
            body=body,
            set_system_admin=set_system_admin,
        )
    ).parsed
