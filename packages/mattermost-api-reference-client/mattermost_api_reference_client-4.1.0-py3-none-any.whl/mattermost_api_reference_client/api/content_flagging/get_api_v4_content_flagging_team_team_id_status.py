from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_api_v4_content_flagging_team_team_id_status_response_200 import (
    GetApiV4ContentFlaggingTeamTeamIdStatusResponse200,
)
from ...types import Response


def _get_kwargs(
    team_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v4/content_flagging/team/{team_id}/status",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, GetApiV4ContentFlaggingTeamTeamIdStatusResponse200]]:
    if response.status_code == 200:
        response_200 = GetApiV4ContentFlaggingTeamTeamIdStatusResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403

    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404

    if response.status_code == 500:
        response_500 = cast(Any, None)
        return response_500

    if response.status_code == 501:
        response_501 = cast(Any, None)
        return response_501

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, GetApiV4ContentFlaggingTeamTeamIdStatusResponse200]]:
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
) -> Response[Union[Any, GetApiV4ContentFlaggingTeamTeamIdStatusResponse200]]:
    """Get content flagging status for a team

     Returns the content flagging status for a specific team, indicating whether content flagging is
    enabled on the specified team or not.

    Args:
        team_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, GetApiV4ContentFlaggingTeamTeamIdStatusResponse200]]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[Any, GetApiV4ContentFlaggingTeamTeamIdStatusResponse200]]:
    """Get content flagging status for a team

     Returns the content flagging status for a specific team, indicating whether content flagging is
    enabled on the specified team or not.

    Args:
        team_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, GetApiV4ContentFlaggingTeamTeamIdStatusResponse200]
    """

    return sync_detailed(
        team_id=team_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[Any, GetApiV4ContentFlaggingTeamTeamIdStatusResponse200]]:
    """Get content flagging status for a team

     Returns the content flagging status for a specific team, indicating whether content flagging is
    enabled on the specified team or not.

    Args:
        team_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, GetApiV4ContentFlaggingTeamTeamIdStatusResponse200]]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    team_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[Any, GetApiV4ContentFlaggingTeamTeamIdStatusResponse200]]:
    """Get content flagging status for a team

     Returns the content flagging status for a specific team, indicating whether content flagging is
    enabled on the specified team or not.

    Args:
        team_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, GetApiV4ContentFlaggingTeamTeamIdStatusResponse200]
    """

    return (
        await asyncio_detailed(
            team_id=team_id,
            client=client,
        )
    ).parsed
