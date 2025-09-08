from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.status_ok import StatusOK
from ...types import UNSET, Response


def _get_kwargs(
    policy_id: str,
    *,
    active: bool,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["active"] = active

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v4/access_control_policies/{policy_id}/activate",
        "params": params,
    }

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

    if response.status_code == 500:
        response_500 = AppError.from_dict(response.json())

        return response_500

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
    policy_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    active: bool,
) -> Response[Union[AppError, StatusOK]]:
    """Activate or deactivate an access control policy

     Updates the active status of an access control policy.
    ##### Permissions
    Must have the `manage_system` permission.

    Args:
        policy_id (str):
        active (bool):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, StatusOK]]
    """

    kwargs = _get_kwargs(
        policy_id=policy_id,
        active=active,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    policy_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    active: bool,
) -> Optional[Union[AppError, StatusOK]]:
    """Activate or deactivate an access control policy

     Updates the active status of an access control policy.
    ##### Permissions
    Must have the `manage_system` permission.

    Args:
        policy_id (str):
        active (bool):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, StatusOK]
    """

    return sync_detailed(
        policy_id=policy_id,
        client=client,
        active=active,
    ).parsed


async def asyncio_detailed(
    policy_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    active: bool,
) -> Response[Union[AppError, StatusOK]]:
    """Activate or deactivate an access control policy

     Updates the active status of an access control policy.
    ##### Permissions
    Must have the `manage_system` permission.

    Args:
        policy_id (str):
        active (bool):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, StatusOK]]
    """

    kwargs = _get_kwargs(
        policy_id=policy_id,
        active=active,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    policy_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    active: bool,
) -> Optional[Union[AppError, StatusOK]]:
    """Activate or deactivate an access control policy

     Updates the active status of an access control policy.
    ##### Permissions
    Must have the `manage_system` permission.

    Args:
        policy_id (str):
        active (bool):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, StatusOK]
    """

    return (
        await asyncio_detailed(
            policy_id=policy_id,
            client=client,
            active=active,
        )
    ).parsed
