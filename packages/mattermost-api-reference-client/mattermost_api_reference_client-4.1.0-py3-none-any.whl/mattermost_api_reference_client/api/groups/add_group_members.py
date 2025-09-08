from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.add_group_members_body import AddGroupMembersBody
from ...models.app_error import AppError
from ...models.group_member import GroupMember
from ...types import Response


def _get_kwargs(
    group_id: str,
    *,
    body: AddGroupMembersBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v4/groups/{group_id}/members",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, AppError, list["GroupMember"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = GroupMember.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    if response.status_code == 403:
        response_403 = AppError.from_dict(response.json())

        return response_403

    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404

    if response.status_code == 501:
        response_501 = cast(Any, None)
        return response_501

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, AppError, list["GroupMember"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    group_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: AddGroupMembersBody,
) -> Response[Union[Any, AppError, list["GroupMember"]]]:
    """Adds members to a custom group

     Adds members to a custom group.

    ##### Permissions
    Must have `custom_group_manage_members` permission for the given group.

    __Minimum server version__: 6.3

    Args:
        group_id (str):
        body (AddGroupMembersBody): An object containing the user ids of the members to add.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, AppError, list['GroupMember']]]
    """

    kwargs = _get_kwargs(
        group_id=group_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    group_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: AddGroupMembersBody,
) -> Optional[Union[Any, AppError, list["GroupMember"]]]:
    """Adds members to a custom group

     Adds members to a custom group.

    ##### Permissions
    Must have `custom_group_manage_members` permission for the given group.

    __Minimum server version__: 6.3

    Args:
        group_id (str):
        body (AddGroupMembersBody): An object containing the user ids of the members to add.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, AppError, list['GroupMember']]
    """

    return sync_detailed(
        group_id=group_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    group_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: AddGroupMembersBody,
) -> Response[Union[Any, AppError, list["GroupMember"]]]:
    """Adds members to a custom group

     Adds members to a custom group.

    ##### Permissions
    Must have `custom_group_manage_members` permission for the given group.

    __Minimum server version__: 6.3

    Args:
        group_id (str):
        body (AddGroupMembersBody): An object containing the user ids of the members to add.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, AppError, list['GroupMember']]]
    """

    kwargs = _get_kwargs(
        group_id=group_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    group_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: AddGroupMembersBody,
) -> Optional[Union[Any, AppError, list["GroupMember"]]]:
    """Adds members to a custom group

     Adds members to a custom group.

    ##### Permissions
    Must have `custom_group_manage_members` permission for the given group.

    __Minimum server version__: 6.3

    Args:
        group_id (str):
        body (AddGroupMembersBody): An object containing the user ids of the members to add.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, AppError, list['GroupMember']]
    """

    return (
        await asyncio_detailed(
            group_id=group_id,
            client=client,
            body=body,
        )
    ).parsed
