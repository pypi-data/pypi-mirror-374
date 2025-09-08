from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.patch_scheme_body import PatchSchemeBody
from ...models.scheme import Scheme
from ...types import Response


def _get_kwargs(
    scheme_id: str,
    *,
    body: PatchSchemeBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/api/v4/schemes/{scheme_id}/patch",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, Scheme]]:
    if response.status_code == 200:
        response_200 = Scheme.from_dict(response.json())

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

    if response.status_code == 501:
        response_501 = AppError.from_dict(response.json())

        return response_501

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, Scheme]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    scheme_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: PatchSchemeBody,
) -> Response[Union[AppError, Scheme]]:
    """Patch a scheme

     Partially update a scheme by providing only the fields you want to update. Omitted fields will not
    be updated. The fields that can be updated are defined in the request body, all other provided
    fields will be ignored.

    ##### Permissions
    `manage_system` permission is required.

    __Minimum server version__: 5.0

    Args:
        scheme_id (str):
        body (PatchSchemeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, Scheme]]
    """

    kwargs = _get_kwargs(
        scheme_id=scheme_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    scheme_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: PatchSchemeBody,
) -> Optional[Union[AppError, Scheme]]:
    """Patch a scheme

     Partially update a scheme by providing only the fields you want to update. Omitted fields will not
    be updated. The fields that can be updated are defined in the request body, all other provided
    fields will be ignored.

    ##### Permissions
    `manage_system` permission is required.

    __Minimum server version__: 5.0

    Args:
        scheme_id (str):
        body (PatchSchemeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, Scheme]
    """

    return sync_detailed(
        scheme_id=scheme_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    scheme_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: PatchSchemeBody,
) -> Response[Union[AppError, Scheme]]:
    """Patch a scheme

     Partially update a scheme by providing only the fields you want to update. Omitted fields will not
    be updated. The fields that can be updated are defined in the request body, all other provided
    fields will be ignored.

    ##### Permissions
    `manage_system` permission is required.

    __Minimum server version__: 5.0

    Args:
        scheme_id (str):
        body (PatchSchemeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, Scheme]]
    """

    kwargs = _get_kwargs(
        scheme_id=scheme_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    scheme_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: PatchSchemeBody,
) -> Optional[Union[AppError, Scheme]]:
    """Patch a scheme

     Partially update a scheme by providing only the fields you want to update. Omitted fields will not
    be updated. The fields that can be updated are defined in the request body, all other provided
    fields will be ignored.

    ##### Permissions
    `manage_system` permission is required.

    __Minimum server version__: 5.0

    Args:
        scheme_id (str):
        body (PatchSchemeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, Scheme]
    """

    return (
        await asyncio_detailed(
            scheme_id=scheme_id,
            client=client,
            body=body,
        )
    ).parsed
