from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.create_outgoing_webhook_body import CreateOutgoingWebhookBody
from ...models.outgoing_webhook import OutgoingWebhook
from ...types import Response


def _get_kwargs(
    *,
    body: CreateOutgoingWebhookBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v4/hooks/outgoing",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, OutgoingWebhook]]:
    if response.status_code == 201:
        response_201 = OutgoingWebhook.from_dict(response.json())

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
    *,
    client: Union[AuthenticatedClient, Client],
    body: CreateOutgoingWebhookBody,
) -> Response[Union[AppError, OutgoingWebhook]]:
    """Create an outgoing webhook

     Create an outgoing webhook for a team.
    ##### Permissions
    `manage_webhooks` for the team the webhook is in.

    `manage_others_outgoing_webhooks` for the team the webhook is in if the user is different than the
    requester.

    Args:
        body (CreateOutgoingWebhookBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, OutgoingWebhook]]
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
    body: CreateOutgoingWebhookBody,
) -> Optional[Union[AppError, OutgoingWebhook]]:
    """Create an outgoing webhook

     Create an outgoing webhook for a team.
    ##### Permissions
    `manage_webhooks` for the team the webhook is in.

    `manage_others_outgoing_webhooks` for the team the webhook is in if the user is different than the
    requester.

    Args:
        body (CreateOutgoingWebhookBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, OutgoingWebhook]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CreateOutgoingWebhookBody,
) -> Response[Union[AppError, OutgoingWebhook]]:
    """Create an outgoing webhook

     Create an outgoing webhook for a team.
    ##### Permissions
    `manage_webhooks` for the team the webhook is in.

    `manage_others_outgoing_webhooks` for the team the webhook is in if the user is different than the
    requester.

    Args:
        body (CreateOutgoingWebhookBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, OutgoingWebhook]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CreateOutgoingWebhookBody,
) -> Optional[Union[AppError, OutgoingWebhook]]:
    """Create an outgoing webhook

     Create an outgoing webhook for a team.
    ##### Permissions
    `manage_webhooks` for the team the webhook is in.

    `manage_others_outgoing_webhooks` for the team the webhook is in if the user is different than the
    requester.

    Args:
        body (CreateOutgoingWebhookBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, OutgoingWebhook]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
