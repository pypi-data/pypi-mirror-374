from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.confirm_customer_payment_body import ConfirmCustomerPaymentBody
from ...types import Response


def _get_kwargs(
    *,
    body: ConfirmCustomerPaymentBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v4/cloud/payment/confirm",
    }

    _kwargs["files"] = body.to_multipart()

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, AppError]]:
    if response.status_code == 200:
        response_200 = cast(Any, None)
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
) -> Response[Union[Any, AppError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ConfirmCustomerPaymentBody,
) -> Response[Union[Any, AppError]]:
    """Completes the payment setup intent

     Confirms the payment setup intent initiated when posting to `/cloud/payment`.
    ##### Permissions
    Must have `manage_system` permission and be licensed for Cloud.
    __Minimum server version__: 5.28 __Note:__ This is intended for internal use and is subject to
    change.

    Args:
        body (ConfirmCustomerPaymentBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, AppError]]
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
    body: ConfirmCustomerPaymentBody,
) -> Optional[Union[Any, AppError]]:
    """Completes the payment setup intent

     Confirms the payment setup intent initiated when posting to `/cloud/payment`.
    ##### Permissions
    Must have `manage_system` permission and be licensed for Cloud.
    __Minimum server version__: 5.28 __Note:__ This is intended for internal use and is subject to
    change.

    Args:
        body (ConfirmCustomerPaymentBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, AppError]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ConfirmCustomerPaymentBody,
) -> Response[Union[Any, AppError]]:
    """Completes the payment setup intent

     Confirms the payment setup intent initiated when posting to `/cloud/payment`.
    ##### Permissions
    Must have `manage_system` permission and be licensed for Cloud.
    __Minimum server version__: 5.28 __Note:__ This is intended for internal use and is subject to
    change.

    Args:
        body (ConfirmCustomerPaymentBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, AppError]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ConfirmCustomerPaymentBody,
) -> Optional[Union[Any, AppError]]:
    """Completes the payment setup intent

     Confirms the payment setup intent initiated when posting to `/cloud/payment`.
    ##### Permissions
    Must have `manage_system` permission and be licensed for Cloud.
    __Minimum server version__: 5.28 __Note:__ This is intended for internal use and is subject to
    change.

    Args:
        body (ConfirmCustomerPaymentBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, AppError]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
