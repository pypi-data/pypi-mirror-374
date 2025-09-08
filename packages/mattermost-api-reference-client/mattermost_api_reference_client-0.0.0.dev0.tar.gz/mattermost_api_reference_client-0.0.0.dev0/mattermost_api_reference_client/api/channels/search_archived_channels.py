from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.channel import Channel
from ...models.search_archived_channels_body import SearchArchivedChannelsBody
from ...types import Response


def _get_kwargs(
    team_id: str,
    *,
    body: SearchArchivedChannelsBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v4/teams/{team_id}/channels/search_archived",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, list["Channel"]]]:
    if response.status_code == 201:
        response_201 = []
        _response_201 = response.json()
        for response_201_item_data in _response_201:
            response_201_item = Channel.from_dict(response_201_item_data)

            response_201.append(response_201_item)

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
) -> Response[Union[AppError, list["Channel"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: SearchArchivedChannelsBody,
) -> Response[Union[AppError, list["Channel"]]]:
    """Search archived channels

     Search archived channels on a team based on the search term provided in the request body.

    __Minimum server version__: 5.18

    ##### Permissions
    Must have the `list_team_channels` permission.

    In server version 5.18 and later, a user without the `list_team_channels` permission will be able to
    use this endpoint, with the search results limited to the channels that the user is a member of.

    Args:
        team_id (str):
        body (SearchArchivedChannelsBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['Channel']]]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: SearchArchivedChannelsBody,
) -> Optional[Union[AppError, list["Channel"]]]:
    """Search archived channels

     Search archived channels on a team based on the search term provided in the request body.

    __Minimum server version__: 5.18

    ##### Permissions
    Must have the `list_team_channels` permission.

    In server version 5.18 and later, a user without the `list_team_channels` permission will be able to
    use this endpoint, with the search results limited to the channels that the user is a member of.

    Args:
        team_id (str):
        body (SearchArchivedChannelsBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['Channel']]
    """

    return sync_detailed(
        team_id=team_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: SearchArchivedChannelsBody,
) -> Response[Union[AppError, list["Channel"]]]:
    """Search archived channels

     Search archived channels on a team based on the search term provided in the request body.

    __Minimum server version__: 5.18

    ##### Permissions
    Must have the `list_team_channels` permission.

    In server version 5.18 and later, a user without the `list_team_channels` permission will be able to
    use this endpoint, with the search results limited to the channels that the user is a member of.

    Args:
        team_id (str):
        body (SearchArchivedChannelsBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['Channel']]]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: SearchArchivedChannelsBody,
) -> Optional[Union[AppError, list["Channel"]]]:
    """Search archived channels

     Search archived channels on a team based on the search term provided in the request body.

    __Minimum server version__: 5.18

    ##### Permissions
    Must have the `list_team_channels` permission.

    In server version 5.18 and later, a user without the `list_team_channels` permission will be able to
    use this endpoint, with the search results limited to the channels that the user is a member of.

    Args:
        team_id (str):
        body (SearchArchivedChannelsBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['Channel']]
    """

    return (
        await asyncio_detailed(
            team_id=team_id,
            client=client,
            body=body,
        )
    ).parsed
