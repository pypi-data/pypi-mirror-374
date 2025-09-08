from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.get_checklist_autocomplete_response_200_item import GetChecklistAutocompleteResponse200Item
from ...types import UNSET, Response


def _get_kwargs(
    *,
    channel_id: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["channel_ID"] = channel_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/plugins/playbooks/api/v0/runs/checklist-autocomplete",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Error, list["GetChecklistAutocompleteResponse200Item"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = GetChecklistAutocompleteResponse200Item.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    if response.status_code == 500:
        response_500 = Error.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Error, list["GetChecklistAutocompleteResponse200Item"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    channel_id: str,
) -> Response[Union[Error, list["GetChecklistAutocompleteResponse200Item"]]]:
    """Get autocomplete data for /playbook check

     This is an internal endpoint used by the autocomplete system to retrieve the data needed to show the
    list of items that the user can check.

    Args:
        channel_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, list['GetChecklistAutocompleteResponse200Item']]]
    """

    kwargs = _get_kwargs(
        channel_id=channel_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    channel_id: str,
) -> Optional[Union[Error, list["GetChecklistAutocompleteResponse200Item"]]]:
    """Get autocomplete data for /playbook check

     This is an internal endpoint used by the autocomplete system to retrieve the data needed to show the
    list of items that the user can check.

    Args:
        channel_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, list['GetChecklistAutocompleteResponse200Item']]
    """

    return sync_detailed(
        client=client,
        channel_id=channel_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    channel_id: str,
) -> Response[Union[Error, list["GetChecklistAutocompleteResponse200Item"]]]:
    """Get autocomplete data for /playbook check

     This is an internal endpoint used by the autocomplete system to retrieve the data needed to show the
    list of items that the user can check.

    Args:
        channel_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, list['GetChecklistAutocompleteResponse200Item']]]
    """

    kwargs = _get_kwargs(
        channel_id=channel_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    channel_id: str,
) -> Optional[Union[Error, list["GetChecklistAutocompleteResponse200Item"]]]:
    """Get autocomplete data for /playbook check

     This is an internal endpoint used by the autocomplete system to retrieve the data needed to show the
    list of items that the user can check.

    Args:
        channel_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, list['GetChecklistAutocompleteResponse200Item']]
    """

    return (
        await asyncio_detailed(
            client=client,
            channel_id=channel_id,
        )
    ).parsed
