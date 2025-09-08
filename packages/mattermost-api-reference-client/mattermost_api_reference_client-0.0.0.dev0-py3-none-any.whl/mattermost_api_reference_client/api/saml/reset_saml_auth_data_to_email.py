from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.reset_saml_auth_data_to_email_body import ResetSamlAuthDataToEmailBody
from ...models.reset_saml_auth_data_to_email_response_200 import ResetSamlAuthDataToEmailResponse200
from ...types import Response


def _get_kwargs(
    *,
    body: ResetSamlAuthDataToEmailBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v4/saml/reset_auth_data",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, ResetSamlAuthDataToEmailResponse200]]:
    if response.status_code == 200:
        response_200 = ResetSamlAuthDataToEmailResponse200.from_dict(response.json())

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
) -> Response[Union[AppError, ResetSamlAuthDataToEmailResponse200]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ResetSamlAuthDataToEmailBody,
) -> Response[Union[AppError, ResetSamlAuthDataToEmailResponse200]]:
    r"""Reset AuthData to Email

     Reset the AuthData field of SAML users to their email. This is meant to be used when the \"id\"
    attribute is set to an empty value (\"\") from a previously non-empty value.
    __Minimum server version__: 5.35
    ##### Permissions
    Must have `manage_system` permission.

    Args:
        body (ResetSamlAuthDataToEmailBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, ResetSamlAuthDataToEmailResponse200]]
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
    body: ResetSamlAuthDataToEmailBody,
) -> Optional[Union[AppError, ResetSamlAuthDataToEmailResponse200]]:
    r"""Reset AuthData to Email

     Reset the AuthData field of SAML users to their email. This is meant to be used when the \"id\"
    attribute is set to an empty value (\"\") from a previously non-empty value.
    __Minimum server version__: 5.35
    ##### Permissions
    Must have `manage_system` permission.

    Args:
        body (ResetSamlAuthDataToEmailBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, ResetSamlAuthDataToEmailResponse200]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ResetSamlAuthDataToEmailBody,
) -> Response[Union[AppError, ResetSamlAuthDataToEmailResponse200]]:
    r"""Reset AuthData to Email

     Reset the AuthData field of SAML users to their email. This is meant to be used when the \"id\"
    attribute is set to an empty value (\"\") from a previously non-empty value.
    __Minimum server version__: 5.35
    ##### Permissions
    Must have `manage_system` permission.

    Args:
        body (ResetSamlAuthDataToEmailBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, ResetSamlAuthDataToEmailResponse200]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ResetSamlAuthDataToEmailBody,
) -> Optional[Union[AppError, ResetSamlAuthDataToEmailResponse200]]:
    r"""Reset AuthData to Email

     Reset the AuthData field of SAML users to their email. This is meant to be used when the \"id\"
    attribute is set to an empty value (\"\") from a previously non-empty value.
    __Minimum server version__: 5.35
    ##### Permissions
    Must have `manage_system` permission.

    Args:
        body (ResetSamlAuthDataToEmailBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, ResetSamlAuthDataToEmailResponse200]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
