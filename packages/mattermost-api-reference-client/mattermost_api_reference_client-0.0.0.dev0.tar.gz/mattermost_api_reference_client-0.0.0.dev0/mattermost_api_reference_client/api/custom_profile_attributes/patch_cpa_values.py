from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.patch_cpa_values_body_item import PatchCPAValuesBodyItem
from ...models.patch_cpa_values_response_200_item import PatchCPAValuesResponse200Item
from ...types import Response


def _get_kwargs(
    *,
    body: list["PatchCPAValuesBodyItem"],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/api/v4/custom_profile_attributes/values",
    }

    _kwargs["json"] = []
    for body_item_data in body:
        body_item = body_item_data.to_dict()
        _kwargs["json"].append(body_item)

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, list["PatchCPAValuesResponse200Item"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = PatchCPAValuesResponse200Item.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[Union[AppError, list["PatchCPAValuesResponse200Item"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: list["PatchCPAValuesBodyItem"],
) -> Response[Union[AppError, list["PatchCPAValuesResponse200Item"]]]:
    """Patch Custom Profile Attribute values

     Partially update a set of values on the requester's Custom
    Profile Attribute fields by providing only the information you
    want to update. Omitted fields will not be updated. The fields
    that can be updated are defined in the request body, all other
    provided fields will be ignored.

    _This endpoint is experimental._

    __Minimum server version__: 10.5

    ##### Permissions
    Must be authenticated.

    Args:
        body (list['PatchCPAValuesBodyItem']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['PatchCPAValuesResponse200Item']]]
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
    body: list["PatchCPAValuesBodyItem"],
) -> Optional[Union[AppError, list["PatchCPAValuesResponse200Item"]]]:
    """Patch Custom Profile Attribute values

     Partially update a set of values on the requester's Custom
    Profile Attribute fields by providing only the information you
    want to update. Omitted fields will not be updated. The fields
    that can be updated are defined in the request body, all other
    provided fields will be ignored.

    _This endpoint is experimental._

    __Minimum server version__: 10.5

    ##### Permissions
    Must be authenticated.

    Args:
        body (list['PatchCPAValuesBodyItem']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['PatchCPAValuesResponse200Item']]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: list["PatchCPAValuesBodyItem"],
) -> Response[Union[AppError, list["PatchCPAValuesResponse200Item"]]]:
    """Patch Custom Profile Attribute values

     Partially update a set of values on the requester's Custom
    Profile Attribute fields by providing only the information you
    want to update. Omitted fields will not be updated. The fields
    that can be updated are defined in the request body, all other
    provided fields will be ignored.

    _This endpoint is experimental._

    __Minimum server version__: 10.5

    ##### Permissions
    Must be authenticated.

    Args:
        body (list['PatchCPAValuesBodyItem']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['PatchCPAValuesResponse200Item']]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: list["PatchCPAValuesBodyItem"],
) -> Optional[Union[AppError, list["PatchCPAValuesResponse200Item"]]]:
    """Patch Custom Profile Attribute values

     Partially update a set of values on the requester's Custom
    Profile Attribute fields by providing only the information you
    want to update. Omitted fields will not be updated. The fields
    that can be updated are defined in the request body, all other
    provided fields will be ignored.

    _This endpoint is experimental._

    __Minimum server version__: 10.5

    ##### Permissions
    Must be authenticated.

    Args:
        body (list['PatchCPAValuesBodyItem']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['PatchCPAValuesResponse200Item']]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
