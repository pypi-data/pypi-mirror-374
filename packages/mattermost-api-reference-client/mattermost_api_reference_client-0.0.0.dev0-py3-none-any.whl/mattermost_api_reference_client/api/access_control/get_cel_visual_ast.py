from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.cel_expression import CELExpression
from ...models.visual_expression import VisualExpression
from ...types import Response


def _get_kwargs(
    *,
    body: CELExpression,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v4/access_control_policies/cel/visual_ast",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, VisualExpression]]:
    if response.status_code == 200:
        response_200 = VisualExpression.from_dict(response.json())

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

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, VisualExpression]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CELExpression,
) -> Response[Union[AppError, VisualExpression]]:
    """Get the visual AST for a CEL expression

     Retrieves the visual AST for a CEL expression.
    ##### Permissions
    Must have the `manage_system` permission.

    Args:
        body (CELExpression):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, VisualExpression]]
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
    body: CELExpression,
) -> Optional[Union[AppError, VisualExpression]]:
    """Get the visual AST for a CEL expression

     Retrieves the visual AST for a CEL expression.
    ##### Permissions
    Must have the `manage_system` permission.

    Args:
        body (CELExpression):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, VisualExpression]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CELExpression,
) -> Response[Union[AppError, VisualExpression]]:
    """Get the visual AST for a CEL expression

     Retrieves the visual AST for a CEL expression.
    ##### Permissions
    Must have the `manage_system` permission.

    Args:
        body (CELExpression):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, VisualExpression]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CELExpression,
) -> Optional[Union[AppError, VisualExpression]]:
    """Get the visual AST for a CEL expression

     Retrieves the visual AST for a CEL expression.
    ##### Permissions
    Must have the `manage_system` permission.

    Args:
        body (CELExpression):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, VisualExpression]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
