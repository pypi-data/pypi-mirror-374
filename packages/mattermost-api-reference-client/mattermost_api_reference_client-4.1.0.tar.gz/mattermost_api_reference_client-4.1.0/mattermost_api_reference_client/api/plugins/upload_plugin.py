from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.status_ok import StatusOK
from ...models.upload_plugin_body import UploadPluginBody
from ...types import Response


def _get_kwargs(
    *,
    body: UploadPluginBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v4/plugins",
    }

    _kwargs["files"] = body.to_multipart()

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, StatusOK]]:
    if response.status_code == 201:
        response_201 = StatusOK.from_dict(response.json())

        return response_201

    if response.status_code == 400:
        response_400 = AppError.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = AppError.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = AppError.from_dict(response.json())

        return response_403

    if response.status_code == 413:
        response_413 = AppError.from_dict(response.json())

        return response_413

    if response.status_code == 501:
        response_501 = AppError.from_dict(response.json())

        return response_501

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
    body: UploadPluginBody,
) -> Response[Union[AppError, StatusOK]]:
    """Upload plugin

     Upload a plugin that is contained within a compressed .tar.gz file. Plugins and plugin uploads must
    be enabled in the server's config settings.

    ##### Permissions
    Must have `manage_system` permission.

    __Minimum server version__: 4.4

    Args:
        body (UploadPluginBody):

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
    body: UploadPluginBody,
) -> Optional[Union[AppError, StatusOK]]:
    """Upload plugin

     Upload a plugin that is contained within a compressed .tar.gz file. Plugins and plugin uploads must
    be enabled in the server's config settings.

    ##### Permissions
    Must have `manage_system` permission.

    __Minimum server version__: 4.4

    Args:
        body (UploadPluginBody):

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
    body: UploadPluginBody,
) -> Response[Union[AppError, StatusOK]]:
    """Upload plugin

     Upload a plugin that is contained within a compressed .tar.gz file. Plugins and plugin uploads must
    be enabled in the server's config settings.

    ##### Permissions
    Must have `manage_system` permission.

    __Minimum server version__: 4.4

    Args:
        body (UploadPluginBody):

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
    body: UploadPluginBody,
) -> Optional[Union[AppError, StatusOK]]:
    """Upload plugin

     Upload a plugin that is contained within a compressed .tar.gz file. Plugins and plugin uploads must
    be enabled in the server's config settings.

    ##### Permissions
    Must have `manage_system` permission.

    __Minimum server version__: 4.4

    Args:
        body (UploadPluginBody):

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
