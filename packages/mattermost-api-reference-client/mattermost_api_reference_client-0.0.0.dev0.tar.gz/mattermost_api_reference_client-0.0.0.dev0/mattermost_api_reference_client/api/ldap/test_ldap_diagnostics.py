from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.ldap_diagnostic_result import LdapDiagnosticResult
from ...models.ldap_settings import LdapSettings
from ...models.test_ldap_diagnostics_test import TestLdapDiagnosticsTest
from ...types import UNSET, Response


def _get_kwargs(
    *,
    body: LdapSettings,
    test: TestLdapDiagnosticsTest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    json_test = test.value
    params["test"] = json_test

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v4/ldap/test_diagnostics",
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, list["LdapDiagnosticResult"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = LdapDiagnosticResult.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[Union[AppError, list["LdapDiagnosticResult"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: LdapSettings,
    test: TestLdapDiagnosticsTest,
) -> Response[Union[AppError, list["LdapDiagnosticResult"]]]:
    """Test LDAP diagnostics with specific settings

     Test LDAP diagnostics using the provided settings to validate configuration and see sample results
    without modifying the current server configuration. Use the `test` query parameter to specify which
    diagnostic to run.
    ##### Permissions
    Must have `sysconsole_read_authentication_ldap` or `manage_system` permission.

    Args:
        test (TestLdapDiagnosticsTest):  Example: filters.
        body (LdapSettings):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['LdapDiagnosticResult']]]
    """

    kwargs = _get_kwargs(
        body=body,
        test=test,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: LdapSettings,
    test: TestLdapDiagnosticsTest,
) -> Optional[Union[AppError, list["LdapDiagnosticResult"]]]:
    """Test LDAP diagnostics with specific settings

     Test LDAP diagnostics using the provided settings to validate configuration and see sample results
    without modifying the current server configuration. Use the `test` query parameter to specify which
    diagnostic to run.
    ##### Permissions
    Must have `sysconsole_read_authentication_ldap` or `manage_system` permission.

    Args:
        test (TestLdapDiagnosticsTest):  Example: filters.
        body (LdapSettings):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['LdapDiagnosticResult']]
    """

    return sync_detailed(
        client=client,
        body=body,
        test=test,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: LdapSettings,
    test: TestLdapDiagnosticsTest,
) -> Response[Union[AppError, list["LdapDiagnosticResult"]]]:
    """Test LDAP diagnostics with specific settings

     Test LDAP diagnostics using the provided settings to validate configuration and see sample results
    without modifying the current server configuration. Use the `test` query parameter to specify which
    diagnostic to run.
    ##### Permissions
    Must have `sysconsole_read_authentication_ldap` or `manage_system` permission.

    Args:
        test (TestLdapDiagnosticsTest):  Example: filters.
        body (LdapSettings):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['LdapDiagnosticResult']]]
    """

    kwargs = _get_kwargs(
        body=body,
        test=test,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: LdapSettings,
    test: TestLdapDiagnosticsTest,
) -> Optional[Union[AppError, list["LdapDiagnosticResult"]]]:
    """Test LDAP diagnostics with specific settings

     Test LDAP diagnostics using the provided settings to validate configuration and see sample results
    without modifying the current server configuration. Use the `test` query parameter to specify which
    diagnostic to run.
    ##### Permissions
    Must have `sysconsole_read_authentication_ldap` or `manage_system` permission.

    Args:
        test (TestLdapDiagnosticsTest):  Example: filters.
        body (LdapSettings):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['LdapDiagnosticResult']]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            test=test,
        )
    ).parsed
