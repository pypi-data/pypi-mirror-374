from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.retention_policy_for_channel_list import RetentionPolicyForChannelList
from ...types import UNSET, Response, Unset


def _get_kwargs(
    user_id: str,
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
        "url": f"/api/v4/users/{user_id}/data_retention/channel_policies",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, RetentionPolicyForChannelList]]:
    if response.status_code == 200:
        response_200 = RetentionPolicyForChannelList.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = AppError.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = AppError.from_dict(response.json())

        return response_403

    if response.status_code == 500:
        response_500 = AppError.from_dict(response.json())

        return response_500

    if response.status_code == 501:
        response_501 = AppError.from_dict(response.json())

        return response_501

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, RetentionPolicyForChannelList]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
) -> Response[Union[AppError, RetentionPolicyForChannelList]]:
    """Get the policies which are applied to a user's channels

     Gets the policies which are applied to the all of the channels to which a user belongs.

    __Minimum server version__: 5.35

    ##### Permissions
    Must be logged in as the user or have the `manage_system` permission.

    ##### License
    Requires an E20 license.

    Args:
        user_id (str):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, RetentionPolicyForChannelList]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        page=page,
        per_page=per_page,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
) -> Optional[Union[AppError, RetentionPolicyForChannelList]]:
    """Get the policies which are applied to a user's channels

     Gets the policies which are applied to the all of the channels to which a user belongs.

    __Minimum server version__: 5.35

    ##### Permissions
    Must be logged in as the user or have the `manage_system` permission.

    ##### License
    Requires an E20 license.

    Args:
        user_id (str):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, RetentionPolicyForChannelList]
    """

    return sync_detailed(
        user_id=user_id,
        client=client,
        page=page,
        per_page=per_page,
    ).parsed


async def asyncio_detailed(
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
) -> Response[Union[AppError, RetentionPolicyForChannelList]]:
    """Get the policies which are applied to a user's channels

     Gets the policies which are applied to the all of the channels to which a user belongs.

    __Minimum server version__: 5.35

    ##### Permissions
    Must be logged in as the user or have the `manage_system` permission.

    ##### License
    Requires an E20 license.

    Args:
        user_id (str):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, RetentionPolicyForChannelList]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        page=page,
        per_page=per_page,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 0,
    per_page: Union[Unset, int] = 60,
) -> Optional[Union[AppError, RetentionPolicyForChannelList]]:
    """Get the policies which are applied to a user's channels

     Gets the policies which are applied to the all of the channels to which a user belongs.

    __Minimum server version__: 5.35

    ##### Permissions
    Must be logged in as the user or have the `manage_system` permission.

    ##### License
    Requires an E20 license.

    Args:
        user_id (str):
        page (Union[Unset, int]):  Default: 0.
        per_page (Union[Unset, int]):  Default: 60.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, RetentionPolicyForChannelList]
    """

    return (
        await asyncio_detailed(
            user_id=user_id,
            client=client,
            page=page,
            per_page=per_page,
        )
    ).parsed
