from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.patch_cpa_field_body import PatchCPAFieldBody
from ...models.property_field import PropertyField
from ...types import Response


def _get_kwargs(
    field_id: str,
    *,
    body: PatchCPAFieldBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": f"/api/v4/custom_profile_attributes/fields/{field_id}",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, PropertyField]]:
    if response.status_code == 200:
        response_200 = PropertyField.from_dict(response.json())

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
) -> Response[Union[AppError, PropertyField]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    field_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: PatchCPAFieldBody,
) -> Response[Union[AppError, PropertyField]]:
    """Patch a Custom Profile Attribute field

     Partially update a Custom Profile Attribute field by providing
    only the fields you want to update. Omitted fields will not be
    updated. The fields that can be updated are defined in the
    request body, all other provided fields will be ignored.

    _This endpoint is experimental._

    __Minimum server version__: 10.5

    ##### Permissions
    Must have `manage_system` permission.

    Args:
        field_id (str):
        body (PatchCPAFieldBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, PropertyField]]
    """

    kwargs = _get_kwargs(
        field_id=field_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    field_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: PatchCPAFieldBody,
) -> Optional[Union[AppError, PropertyField]]:
    """Patch a Custom Profile Attribute field

     Partially update a Custom Profile Attribute field by providing
    only the fields you want to update. Omitted fields will not be
    updated. The fields that can be updated are defined in the
    request body, all other provided fields will be ignored.

    _This endpoint is experimental._

    __Minimum server version__: 10.5

    ##### Permissions
    Must have `manage_system` permission.

    Args:
        field_id (str):
        body (PatchCPAFieldBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, PropertyField]
    """

    return sync_detailed(
        field_id=field_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    field_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: PatchCPAFieldBody,
) -> Response[Union[AppError, PropertyField]]:
    """Patch a Custom Profile Attribute field

     Partially update a Custom Profile Attribute field by providing
    only the fields you want to update. Omitted fields will not be
    updated. The fields that can be updated are defined in the
    request body, all other provided fields will be ignored.

    _This endpoint is experimental._

    __Minimum server version__: 10.5

    ##### Permissions
    Must have `manage_system` permission.

    Args:
        field_id (str):
        body (PatchCPAFieldBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, PropertyField]]
    """

    kwargs = _get_kwargs(
        field_id=field_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    field_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: PatchCPAFieldBody,
) -> Optional[Union[AppError, PropertyField]]:
    """Patch a Custom Profile Attribute field

     Partially update a Custom Profile Attribute field by providing
    only the fields you want to update. Omitted fields will not be
    updated. The fields that can be updated are defined in the
    request body, all other provided fields will be ignored.

    _This endpoint is experimental._

    __Minimum server version__: 10.5

    ##### Permissions
    Must have `manage_system` permission.

    Args:
        field_id (str):
        body (PatchCPAFieldBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, PropertyField]
    """

    return (
        await asyncio_detailed(
            field_id=field_id,
            client=client,
            body=body,
        )
    ).parsed
