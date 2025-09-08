from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.switch_account_type_body import SwitchAccountTypeBody
from ...models.switch_account_type_response_200 import SwitchAccountTypeResponse200
from ...types import Response


def _get_kwargs(
    *,
    body: SwitchAccountTypeBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v4/users/login/switch",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, SwitchAccountTypeResponse200]]:
    if response.status_code == 200:
        response_200 = SwitchAccountTypeResponse200.from_dict(response.json())

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

    if response.status_code == 501:
        response_501 = AppError.from_dict(response.json())

        return response_501

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, SwitchAccountTypeResponse200]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: SwitchAccountTypeBody,
) -> Response[Union[AppError, SwitchAccountTypeResponse200]]:
    """Switch login method

     Switch a user's login method from using email to OAuth2/SAML/LDAP or back to email. When switching
    to OAuth2/SAML, account switching is not complete until the user follows the returned link and
    completes any steps on the OAuth2/SAML service provider.

    To switch from email to OAuth2/SAML, specify `current_service`, `new_service`, `email` and
    `password`.

    To switch from OAuth2/SAML to email, specify `current_service`, `new_service`, `email` and
    `new_password`.

    To switch from email to LDAP/AD, specify `current_service`, `new_service`, `email`, `password`,
    `ldap_ip` and `new_password` (this is the user's LDAP password).

    To switch from LDAP/AD to email, specify `current_service`, `new_service`, `ldap_ip`, `password`
    (this is the user's LDAP password), `email`  and `new_password`.

    Additionally, specify `mfa_code` when trying to switch an account on LDAP/AD or email that has MFA
    activated.

    ##### Permissions
    No current authentication required except when switching from OAuth2/SAML to email.

    Args:
        body (SwitchAccountTypeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, SwitchAccountTypeResponse200]]
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
    body: SwitchAccountTypeBody,
) -> Optional[Union[AppError, SwitchAccountTypeResponse200]]:
    """Switch login method

     Switch a user's login method from using email to OAuth2/SAML/LDAP or back to email. When switching
    to OAuth2/SAML, account switching is not complete until the user follows the returned link and
    completes any steps on the OAuth2/SAML service provider.

    To switch from email to OAuth2/SAML, specify `current_service`, `new_service`, `email` and
    `password`.

    To switch from OAuth2/SAML to email, specify `current_service`, `new_service`, `email` and
    `new_password`.

    To switch from email to LDAP/AD, specify `current_service`, `new_service`, `email`, `password`,
    `ldap_ip` and `new_password` (this is the user's LDAP password).

    To switch from LDAP/AD to email, specify `current_service`, `new_service`, `ldap_ip`, `password`
    (this is the user's LDAP password), `email`  and `new_password`.

    Additionally, specify `mfa_code` when trying to switch an account on LDAP/AD or email that has MFA
    activated.

    ##### Permissions
    No current authentication required except when switching from OAuth2/SAML to email.

    Args:
        body (SwitchAccountTypeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, SwitchAccountTypeResponse200]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: SwitchAccountTypeBody,
) -> Response[Union[AppError, SwitchAccountTypeResponse200]]:
    """Switch login method

     Switch a user's login method from using email to OAuth2/SAML/LDAP or back to email. When switching
    to OAuth2/SAML, account switching is not complete until the user follows the returned link and
    completes any steps on the OAuth2/SAML service provider.

    To switch from email to OAuth2/SAML, specify `current_service`, `new_service`, `email` and
    `password`.

    To switch from OAuth2/SAML to email, specify `current_service`, `new_service`, `email` and
    `new_password`.

    To switch from email to LDAP/AD, specify `current_service`, `new_service`, `email`, `password`,
    `ldap_ip` and `new_password` (this is the user's LDAP password).

    To switch from LDAP/AD to email, specify `current_service`, `new_service`, `ldap_ip`, `password`
    (this is the user's LDAP password), `email`  and `new_password`.

    Additionally, specify `mfa_code` when trying to switch an account on LDAP/AD or email that has MFA
    activated.

    ##### Permissions
    No current authentication required except when switching from OAuth2/SAML to email.

    Args:
        body (SwitchAccountTypeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, SwitchAccountTypeResponse200]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: SwitchAccountTypeBody,
) -> Optional[Union[AppError, SwitchAccountTypeResponse200]]:
    """Switch login method

     Switch a user's login method from using email to OAuth2/SAML/LDAP or back to email. When switching
    to OAuth2/SAML, account switching is not complete until the user follows the returned link and
    completes any steps on the OAuth2/SAML service provider.

    To switch from email to OAuth2/SAML, specify `current_service`, `new_service`, `email` and
    `password`.

    To switch from OAuth2/SAML to email, specify `current_service`, `new_service`, `email` and
    `new_password`.

    To switch from email to LDAP/AD, specify `current_service`, `new_service`, `email`, `password`,
    `ldap_ip` and `new_password` (this is the user's LDAP password).

    To switch from LDAP/AD to email, specify `current_service`, `new_service`, `ldap_ip`, `password`
    (this is the user's LDAP password), `email`  and `new_password`.

    Additionally, specify `mfa_code` when trying to switch an account on LDAP/AD or email that has MFA
    activated.

    ##### Permissions
    No current authentication required except when switching from OAuth2/SAML to email.

    Args:
        body (SwitchAccountTypeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, SwitchAccountTypeResponse200]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
