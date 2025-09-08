from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.lookup_interactive_dialog_body import LookupInteractiveDialogBody
from ...models.lookup_interactive_dialog_response_200 import LookupInteractiveDialogResponse200
from ...types import Response


def _get_kwargs(
    *,
    body: LookupInteractiveDialogBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v4/actions/dialogs/lookup",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, LookupInteractiveDialogResponse200]]:
    if response.status_code == 200:
        response_200 = LookupInteractiveDialogResponse200.from_dict(response.json())

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
) -> Response[Union[AppError, LookupInteractiveDialogResponse200]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: LookupInteractiveDialogBody,
) -> Response[Union[AppError, LookupInteractiveDialogResponse200]]:
    """Lookup dialog elements

     Endpoint used by the Mattermost clients to lookup dynamic dialog elements. See
    https://docs.mattermost.com/developer/interactive-dialogs.html for more information on interactive
    dialogs.
    __Minimum server version: 11.0__

    Args:
        body (LookupInteractiveDialogBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, LookupInteractiveDialogResponse200]]
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
    body: LookupInteractiveDialogBody,
) -> Optional[Union[AppError, LookupInteractiveDialogResponse200]]:
    """Lookup dialog elements

     Endpoint used by the Mattermost clients to lookup dynamic dialog elements. See
    https://docs.mattermost.com/developer/interactive-dialogs.html for more information on interactive
    dialogs.
    __Minimum server version: 11.0__

    Args:
        body (LookupInteractiveDialogBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, LookupInteractiveDialogResponse200]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: LookupInteractiveDialogBody,
) -> Response[Union[AppError, LookupInteractiveDialogResponse200]]:
    """Lookup dialog elements

     Endpoint used by the Mattermost clients to lookup dynamic dialog elements. See
    https://docs.mattermost.com/developer/interactive-dialogs.html for more information on interactive
    dialogs.
    __Minimum server version: 11.0__

    Args:
        body (LookupInteractiveDialogBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, LookupInteractiveDialogResponse200]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: LookupInteractiveDialogBody,
) -> Optional[Union[AppError, LookupInteractiveDialogResponse200]]:
    """Lookup dialog elements

     Endpoint used by the Mattermost clients to lookup dynamic dialog elements. See
    https://docs.mattermost.com/developer/interactive-dialogs.html for more information on interactive
    dialogs.
    __Minimum server version: 11.0__

    Args:
        body (LookupInteractiveDialogBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, LookupInteractiveDialogResponse200]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
