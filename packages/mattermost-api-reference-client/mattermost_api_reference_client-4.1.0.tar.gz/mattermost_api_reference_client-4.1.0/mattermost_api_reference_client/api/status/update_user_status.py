from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.status import Status
from ...models.update_user_status_body import UpdateUserStatusBody
from ...types import Response


def _get_kwargs(
    user_id: str,
    *,
    body: UpdateUserStatusBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/api/v4/users/{user_id}/status",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, Status]]:
    if response.status_code == 200:
        response_200 = Status.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = AppError.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = AppError.from_dict(response.json())

        return response_401

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, Status]]:
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
    body: UpdateUserStatusBody,
) -> Response[Union[AppError, Status]]:
    r"""Update user status

     Manually set a user's status. When setting a user's status, the status will remain that value until
    set \"online\" again, which will return the status to being automatically updated based on user
    activity.
    ##### Permissions
    Must have `edit_other_users` permission for the team.

    Args:
        user_id (str):
        body (UpdateUserStatusBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, Status]]
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
    body: UpdateUserStatusBody,
) -> Optional[Union[AppError, Status]]:
    r"""Update user status

     Manually set a user's status. When setting a user's status, the status will remain that value until
    set \"online\" again, which will return the status to being automatically updated based on user
    activity.
    ##### Permissions
    Must have `edit_other_users` permission for the team.

    Args:
        user_id (str):
        body (UpdateUserStatusBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, Status]
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
    body: UpdateUserStatusBody,
) -> Response[Union[AppError, Status]]:
    r"""Update user status

     Manually set a user's status. When setting a user's status, the status will remain that value until
    set \"online\" again, which will return the status to being automatically updated based on user
    activity.
    ##### Permissions
    Must have `edit_other_users` permission for the team.

    Args:
        user_id (str):
        body (UpdateUserStatusBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, Status]]
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
    body: UpdateUserStatusBody,
) -> Optional[Union[AppError, Status]]:
    r"""Update user status

     Manually set a user's status. When setting a user's status, the status will remain that value until
    set \"online\" again, which will return the status to being automatically updated based on user
    activity.
    ##### Permissions
    Must have `edit_other_users` permission for the team.

    Args:
        user_id (str):
        body (UpdateUserStatusBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, Status]
    """

    return (
        await asyncio_detailed(
            user_id=user_id,
            client=client,
            body=body,
        )
    ).parsed
