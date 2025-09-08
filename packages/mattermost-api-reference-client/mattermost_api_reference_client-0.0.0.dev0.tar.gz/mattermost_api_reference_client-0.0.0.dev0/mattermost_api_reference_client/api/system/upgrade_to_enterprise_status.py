from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.upgrade_to_enterprise_status_response_200 import UpgradeToEnterpriseStatusResponse200
from ...types import Response


def _get_kwargs() -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v4/upgrade_to_enterprise/status",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, UpgradeToEnterpriseStatusResponse200]]:
    if response.status_code == 200:
        response_200 = UpgradeToEnterpriseStatusResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 403:
        response_403 = AppError.from_dict(response.json())

        return response_403

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, UpgradeToEnterpriseStatusResponse200]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, UpgradeToEnterpriseStatusResponse200]]:
    """Get the current status for the inplace upgrade from Team Edition to Enterprise Edition

     It returns the percentage of completion of the current upgrade or the error if there is any.
    __Minimum server version__: 5.27
    ##### Permissions
    Must have `manage_system` permission.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, UpgradeToEnterpriseStatusResponse200]]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, UpgradeToEnterpriseStatusResponse200]]:
    """Get the current status for the inplace upgrade from Team Edition to Enterprise Edition

     It returns the percentage of completion of the current upgrade or the error if there is any.
    __Minimum server version__: 5.27
    ##### Permissions
    Must have `manage_system` permission.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, UpgradeToEnterpriseStatusResponse200]
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, UpgradeToEnterpriseStatusResponse200]]:
    """Get the current status for the inplace upgrade from Team Edition to Enterprise Edition

     It returns the percentage of completion of the current upgrade or the error if there is any.
    __Minimum server version__: 5.27
    ##### Permissions
    Must have `manage_system` permission.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, UpgradeToEnterpriseStatusResponse200]]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, UpgradeToEnterpriseStatusResponse200]]:
    """Get the current status for the inplace upgrade from Team Edition to Enterprise Edition

     It returns the percentage of completion of the current upgrade or the error if there is any.
    __Minimum server version__: 5.27
    ##### Permissions
    Must have `manage_system` permission.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, UpgradeToEnterpriseStatusResponse200]
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
