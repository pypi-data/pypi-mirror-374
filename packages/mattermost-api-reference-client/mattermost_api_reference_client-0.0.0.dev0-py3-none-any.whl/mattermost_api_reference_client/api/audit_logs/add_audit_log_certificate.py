from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.add_audit_log_certificate_body import AddAuditLogCertificateBody
from ...models.app_error import AppError
from ...models.status_ok import StatusOK
from ...types import Response


def _get_kwargs(
    *,
    body: AddAuditLogCertificateBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v4/audit_logs/certificate",
    }

    _kwargs["files"] = body.to_multipart()

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
    body: AddAuditLogCertificateBody,
) -> Response[Union[AppError, StatusOK]]:
    """Upload audit log certificate

     Upload the certificate to be used for TLS verification with the audit log service.

    ##### Permissions
    Must have `sysconsole_write_experimental_features` permission.

    __Minimum server version__: 10.9

    Args:
        body (AddAuditLogCertificateBody):

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
    body: AddAuditLogCertificateBody,
) -> Optional[Union[AppError, StatusOK]]:
    """Upload audit log certificate

     Upload the certificate to be used for TLS verification with the audit log service.

    ##### Permissions
    Must have `sysconsole_write_experimental_features` permission.

    __Minimum server version__: 10.9

    Args:
        body (AddAuditLogCertificateBody):

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
    body: AddAuditLogCertificateBody,
) -> Response[Union[AppError, StatusOK]]:
    """Upload audit log certificate

     Upload the certificate to be used for TLS verification with the audit log service.

    ##### Permissions
    Must have `sysconsole_write_experimental_features` permission.

    __Minimum server version__: 10.9

    Args:
        body (AddAuditLogCertificateBody):

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
    body: AddAuditLogCertificateBody,
) -> Optional[Union[AppError, StatusOK]]:
    """Upload audit log certificate

     Upload the certificate to be used for TLS verification with the audit log service.

    ##### Permissions
    Must have `sysconsole_write_experimental_features` permission.

    __Minimum server version__: 10.9

    Args:
        body (AddAuditLogCertificateBody):

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
