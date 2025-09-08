from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.address import Address
from ...models.app_error import AppError
from ...models.cloud_customer import CloudCustomer
from ...types import Response


def _get_kwargs(
    *,
    body: Address,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/api/v4/cloud/customer/address",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, CloudCustomer]]:
    if response.status_code == 200:
        response_200 = CloudCustomer.from_dict(response.json())

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
) -> Response[Union[AppError, CloudCustomer]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: Address,
) -> Response[Union[AppError, CloudCustomer]]:
    """Update cloud customer address

     Updates the company address for the Mattermost Cloud customer bound to this installation.
    ##### Permissions
    Must have `manage_system` permission and be licensed for Cloud.
    __Minimum server version__: 5.29 __Note:__ This is intended for internal use and is subject to
    change.

    Args:
        body (Address):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, CloudCustomer]]
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
    body: Address,
) -> Optional[Union[AppError, CloudCustomer]]:
    """Update cloud customer address

     Updates the company address for the Mattermost Cloud customer bound to this installation.
    ##### Permissions
    Must have `manage_system` permission and be licensed for Cloud.
    __Minimum server version__: 5.29 __Note:__ This is intended for internal use and is subject to
    change.

    Args:
        body (Address):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, CloudCustomer]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: Address,
) -> Response[Union[AppError, CloudCustomer]]:
    """Update cloud customer address

     Updates the company address for the Mattermost Cloud customer bound to this installation.
    ##### Permissions
    Must have `manage_system` permission and be licensed for Cloud.
    __Minimum server version__: 5.29 __Note:__ This is intended for internal use and is subject to
    change.

    Args:
        body (Address):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, CloudCustomer]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: Address,
) -> Optional[Union[AppError, CloudCustomer]]:
    """Update cloud customer address

     Updates the company address for the Mattermost Cloud customer bound to this installation.
    ##### Permissions
    Must have `manage_system` permission and be licensed for Cloud.
    __Minimum server version__: 5.29 __Note:__ This is intended for internal use and is subject to
    change.

    Args:
        body (Address):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, CloudCustomer]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
