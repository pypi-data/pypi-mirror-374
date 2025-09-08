from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.register_terms_of_service_action_body import RegisterTermsOfServiceActionBody
from ...models.status_ok import StatusOK
from ...types import Response


def _get_kwargs(
    user_id: str,
    *,
    body: RegisterTermsOfServiceActionBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v4/users/{user_id}/terms_of_service",
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

    if response.status_code == 403:
        response_403 = AppError.from_dict(response.json())

        return response_403

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
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: RegisterTermsOfServiceActionBody,
) -> Response[Union[AppError, StatusOK]]:
    """Records user action when they accept or decline custom terms of service

     Records user action when they accept or decline custom terms of service. Records the action in audit
    table.
    Updates user's last accepted terms of service ID if they accepted it.

    __Minimum server version__: 5.4
    ##### Permissions
    Must be logged in as the user being acted on.

    Args:
        user_id (str):
        body (RegisterTermsOfServiceActionBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, StatusOK]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: RegisterTermsOfServiceActionBody,
) -> Optional[Union[AppError, StatusOK]]:
    """Records user action when they accept or decline custom terms of service

     Records user action when they accept or decline custom terms of service. Records the action in audit
    table.
    Updates user's last accepted terms of service ID if they accepted it.

    __Minimum server version__: 5.4
    ##### Permissions
    Must be logged in as the user being acted on.

    Args:
        user_id (str):
        body (RegisterTermsOfServiceActionBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, StatusOK]
    """

    return sync_detailed(
        user_id=user_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: RegisterTermsOfServiceActionBody,
) -> Response[Union[AppError, StatusOK]]:
    """Records user action when they accept or decline custom terms of service

     Records user action when they accept or decline custom terms of service. Records the action in audit
    table.
    Updates user's last accepted terms of service ID if they accepted it.

    __Minimum server version__: 5.4
    ##### Permissions
    Must be logged in as the user being acted on.

    Args:
        user_id (str):
        body (RegisterTermsOfServiceActionBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, StatusOK]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: RegisterTermsOfServiceActionBody,
) -> Optional[Union[AppError, StatusOK]]:
    """Records user action when they accept or decline custom terms of service

     Records user action when they accept or decline custom terms of service. Records the action in audit
    table.
    Updates user's last accepted terms of service ID if they accepted it.

    __Minimum server version__: 5.4
    ##### Permissions
    Must be logged in as the user being acted on.

    Args:
        user_id (str):
        body (RegisterTermsOfServiceActionBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, StatusOK]
    """

    return (
        await asyncio_detailed(
            user_id=user_id,
            client=client,
            body=body,
        )
    ).parsed
