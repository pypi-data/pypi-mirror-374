from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.saml_certificate_status import SamlCertificateStatus
from ...types import Response


def _get_kwargs() -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v4/saml/certificate/status",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, SamlCertificateStatus]]:
    if response.status_code == 200:
        response_200 = SamlCertificateStatus.from_dict(response.json())

        return response_200

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
) -> Response[Union[AppError, SamlCertificateStatus]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, SamlCertificateStatus]]:
    """Get certificate status

     Get the status of the uploaded certificates and keys in use by your SAML configuration.
    ##### Permissions
    Must have `sysconsole_write_authentication` permission.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, SamlCertificateStatus]]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, SamlCertificateStatus]]:
    """Get certificate status

     Get the status of the uploaded certificates and keys in use by your SAML configuration.
    ##### Permissions
    Must have `sysconsole_write_authentication` permission.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, SamlCertificateStatus]
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, SamlCertificateStatus]]:
    """Get certificate status

     Get the status of the uploaded certificates and keys in use by your SAML configuration.
    ##### Permissions
    Must have `sysconsole_write_authentication` permission.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, SamlCertificateStatus]]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, SamlCertificateStatus]]:
    """Get certificate status

     Get the status of the uploaded certificates and keys in use by your SAML configuration.
    ##### Permissions
    Must have `sysconsole_write_authentication` permission.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, SamlCertificateStatus]
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
