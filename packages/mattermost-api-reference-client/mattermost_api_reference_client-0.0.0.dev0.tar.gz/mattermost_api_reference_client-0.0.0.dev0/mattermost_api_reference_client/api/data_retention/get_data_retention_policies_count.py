from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.get_data_retention_policies_count_response_200 import GetDataRetentionPoliciesCountResponse200
from ...types import Response


def _get_kwargs() -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v4/data_retention/policies_count",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, GetDataRetentionPoliciesCountResponse200]]:
    if response.status_code == 200:
        response_200 = GetDataRetentionPoliciesCountResponse200.from_dict(response.json())

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
) -> Response[Union[AppError, GetDataRetentionPoliciesCountResponse200]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, GetDataRetentionPoliciesCountResponse200]]:
    """Get the number of granular data retention policies

     Gets the number of granular (i.e. team or channel-specific) data retention
    policies from the server.

    __Minimum server version__: 5.35

    ##### Permissions
    Must have the `sysconsole_read_compliance_data_retention` permission.

    ##### License
    Requires an E20 license.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, GetDataRetentionPoliciesCountResponse200]]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, GetDataRetentionPoliciesCountResponse200]]:
    """Get the number of granular data retention policies

     Gets the number of granular (i.e. team or channel-specific) data retention
    policies from the server.

    __Minimum server version__: 5.35

    ##### Permissions
    Must have the `sysconsole_read_compliance_data_retention` permission.

    ##### License
    Requires an E20 license.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, GetDataRetentionPoliciesCountResponse200]
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, GetDataRetentionPoliciesCountResponse200]]:
    """Get the number of granular data retention policies

     Gets the number of granular (i.e. team or channel-specific) data retention
    policies from the server.

    __Minimum server version__: 5.35

    ##### Permissions
    Must have the `sysconsole_read_compliance_data_retention` permission.

    ##### License
    Requires an E20 license.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, GetDataRetentionPoliciesCountResponse200]]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, GetDataRetentionPoliciesCountResponse200]]:
    """Get the number of granular data retention policies

     Gets the number of granular (i.e. team or channel-specific) data retention
    policies from the server.

    __Minimum server version__: 5.35

    ##### Permissions
    Must have the `sysconsole_read_compliance_data_retention` permission.

    ##### License
    Requires an E20 license.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, GetDataRetentionPoliciesCountResponse200]
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
