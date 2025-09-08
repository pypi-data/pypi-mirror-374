from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.attach_device_extra_props_body import AttachDeviceExtraPropsBody
from ...models.status_ok import StatusOK
from ...types import Response


def _get_kwargs(
    *,
    body: AttachDeviceExtraPropsBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/api/v4/users/sessions/device",
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
    *,
    client: Union[AuthenticatedClient, Client],
    body: AttachDeviceExtraPropsBody,
) -> Response[Union[AppError, StatusOK]]:
    """Attach mobile device and extra props to the session object

     Attach extra props to the session object of the currently logged in session.
    Adding a mobile device id will enable push notifications for a user, if configured by the server.
    Other props are also available, like whether the device has notifications disabled and the mobile
    version.
    ##### Permissions
    Must be authenticated.

    Args:
        body (AttachDeviceExtraPropsBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, StatusOK]]
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
    body: AttachDeviceExtraPropsBody,
) -> Optional[Union[AppError, StatusOK]]:
    """Attach mobile device and extra props to the session object

     Attach extra props to the session object of the currently logged in session.
    Adding a mobile device id will enable push notifications for a user, if configured by the server.
    Other props are also available, like whether the device has notifications disabled and the mobile
    version.
    ##### Permissions
    Must be authenticated.

    Args:
        body (AttachDeviceExtraPropsBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, StatusOK]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: AttachDeviceExtraPropsBody,
) -> Response[Union[AppError, StatusOK]]:
    """Attach mobile device and extra props to the session object

     Attach extra props to the session object of the currently logged in session.
    Adding a mobile device id will enable push notifications for a user, if configured by the server.
    Other props are also available, like whether the device has notifications disabled and the mobile
    version.
    ##### Permissions
    Must be authenticated.

    Args:
        body (AttachDeviceExtraPropsBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, StatusOK]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: AttachDeviceExtraPropsBody,
) -> Optional[Union[AppError, StatusOK]]:
    """Attach mobile device and extra props to the session object

     Attach extra props to the session object of the currently logged in session.
    Adding a mobile device id will enable push notifications for a user, if configured by the server.
    Other props are also available, like whether the device has notifications disabled and the mobile
    version.
    ##### Permissions
    Must be authenticated.

    Args:
        body (AttachDeviceExtraPropsBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, StatusOK]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
