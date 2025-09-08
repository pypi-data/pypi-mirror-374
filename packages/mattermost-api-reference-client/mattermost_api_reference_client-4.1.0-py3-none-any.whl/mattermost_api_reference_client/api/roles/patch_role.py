from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.patch_role_body import PatchRoleBody
from ...models.role import Role
from ...types import Response


def _get_kwargs(
    role_id: str,
    *,
    body: PatchRoleBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/api/v4/roles/{role_id}/patch",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, Role]]:
    if response.status_code == 200:
        response_200 = Role.from_dict(response.json())

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
) -> Response[Union[AppError, Role]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    role_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: PatchRoleBody,
) -> Response[Union[AppError, Role]]:
    """Patch a role

     Partially update a role by providing only the fields you want to update. Omitted fields will not be
    updated. The fields that can be updated are defined in the request body, all other provided fields
    will be ignored.

    ##### Permissions
    Must have `sysconsole_write_user_management_permissions` or `manage_system` permission. When
    updating the role of a system admin, the `manage_system` permission is mandatory.

    __Minimum server version__: 4.9

    Args:
        role_id (str):
        body (PatchRoleBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, Role]]
    """

    kwargs = _get_kwargs(
        role_id=role_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    role_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: PatchRoleBody,
) -> Optional[Union[AppError, Role]]:
    """Patch a role

     Partially update a role by providing only the fields you want to update. Omitted fields will not be
    updated. The fields that can be updated are defined in the request body, all other provided fields
    will be ignored.

    ##### Permissions
    Must have `sysconsole_write_user_management_permissions` or `manage_system` permission. When
    updating the role of a system admin, the `manage_system` permission is mandatory.

    __Minimum server version__: 4.9

    Args:
        role_id (str):
        body (PatchRoleBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, Role]
    """

    return sync_detailed(
        role_id=role_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    role_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: PatchRoleBody,
) -> Response[Union[AppError, Role]]:
    """Patch a role

     Partially update a role by providing only the fields you want to update. Omitted fields will not be
    updated. The fields that can be updated are defined in the request body, all other provided fields
    will be ignored.

    ##### Permissions
    Must have `sysconsole_write_user_management_permissions` or `manage_system` permission. When
    updating the role of a system admin, the `manage_system` permission is mandatory.

    __Minimum server version__: 4.9

    Args:
        role_id (str):
        body (PatchRoleBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, Role]]
    """

    kwargs = _get_kwargs(
        role_id=role_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    role_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: PatchRoleBody,
) -> Optional[Union[AppError, Role]]:
    """Patch a role

     Partially update a role by providing only the fields you want to update. Omitted fields will not be
    updated. The fields that can be updated are defined in the request body, all other provided fields
    will be ignored.

    ##### Permissions
    Must have `sysconsole_write_user_management_permissions` or `manage_system` permission. When
    updating the role of a system admin, the `manage_system` permission is mandatory.

    __Minimum server version__: 4.9

    Args:
        role_id (str):
        body (PatchRoleBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, Role]
    """

    return (
        await asyncio_detailed(
            role_id=role_id,
            client=client,
            body=body,
        )
    ).parsed
