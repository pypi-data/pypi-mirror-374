from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.outgoing_webhook import OutgoingWebhook
from ...models.update_outgoing_webhook_body import UpdateOutgoingWebhookBody
from ...types import Response


def _get_kwargs(
    hook_id: str,
    *,
    body: UpdateOutgoingWebhookBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/api/v4/hooks/outgoing/{hook_id}",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, OutgoingWebhook]]:
    if response.status_code == 200:
        response_200 = OutgoingWebhook.from_dict(response.json())

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

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, OutgoingWebhook]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    hook_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateOutgoingWebhookBody,
) -> Response[Union[AppError, OutgoingWebhook]]:
    """Update an outgoing webhook

     Update an outgoing webhook given the hook id.
    ##### Permissions
    `manage_webhooks` for system or `manage_webhooks` for the specific team or `manage_webhooks` for the
    channel.

    Args:
        hook_id (str):
        body (UpdateOutgoingWebhookBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, OutgoingWebhook]]
    """

    kwargs = _get_kwargs(
        hook_id=hook_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    hook_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateOutgoingWebhookBody,
) -> Optional[Union[AppError, OutgoingWebhook]]:
    """Update an outgoing webhook

     Update an outgoing webhook given the hook id.
    ##### Permissions
    `manage_webhooks` for system or `manage_webhooks` for the specific team or `manage_webhooks` for the
    channel.

    Args:
        hook_id (str):
        body (UpdateOutgoingWebhookBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, OutgoingWebhook]
    """

    return sync_detailed(
        hook_id=hook_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    hook_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateOutgoingWebhookBody,
) -> Response[Union[AppError, OutgoingWebhook]]:
    """Update an outgoing webhook

     Update an outgoing webhook given the hook id.
    ##### Permissions
    `manage_webhooks` for system or `manage_webhooks` for the specific team or `manage_webhooks` for the
    channel.

    Args:
        hook_id (str):
        body (UpdateOutgoingWebhookBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, OutgoingWebhook]]
    """

    kwargs = _get_kwargs(
        hook_id=hook_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    hook_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateOutgoingWebhookBody,
) -> Optional[Union[AppError, OutgoingWebhook]]:
    """Update an outgoing webhook

     Update an outgoing webhook given the hook id.
    ##### Permissions
    `manage_webhooks` for system or `manage_webhooks` for the specific team or `manage_webhooks` for the
    channel.

    Args:
        hook_id (str):
        body (UpdateOutgoingWebhookBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, OutgoingWebhook]
    """

    return (
        await asyncio_detailed(
            hook_id=hook_id,
            client=client,
            body=body,
        )
    ).parsed
