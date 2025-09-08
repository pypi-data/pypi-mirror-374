from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.search_user_access_tokens_body import SearchUserAccessTokensBody
from ...models.user_access_token_sanitized import UserAccessTokenSanitized
from ...types import Response


def _get_kwargs(
    *,
    body: SearchUserAccessTokensBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v4/users/tokens/search",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[list["UserAccessTokenSanitized"]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = UserAccessTokenSanitized.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["UserAccessTokenSanitized"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: SearchUserAccessTokensBody,
) -> Response[list["UserAccessTokenSanitized"]]:
    """Search tokens

     Get a list of tokens based on search criteria provided in the request body. Searches are done
    against the token id, user id and username.

    __Minimum server version__: 4.7

    ##### Permissions
    Must have `manage_system` permission.

    Args:
        body (SearchUserAccessTokensBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['UserAccessTokenSanitized']]
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
    body: SearchUserAccessTokensBody,
) -> Optional[list["UserAccessTokenSanitized"]]:
    """Search tokens

     Get a list of tokens based on search criteria provided in the request body. Searches are done
    against the token id, user id and username.

    __Minimum server version__: 4.7

    ##### Permissions
    Must have `manage_system` permission.

    Args:
        body (SearchUserAccessTokensBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['UserAccessTokenSanitized']
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: SearchUserAccessTokensBody,
) -> Response[list["UserAccessTokenSanitized"]]:
    """Search tokens

     Get a list of tokens based on search criteria provided in the request body. Searches are done
    against the token id, user id and username.

    __Minimum server version__: 4.7

    ##### Permissions
    Must have `manage_system` permission.

    Args:
        body (SearchUserAccessTokensBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['UserAccessTokenSanitized']]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: SearchUserAccessTokensBody,
) -> Optional[list["UserAccessTokenSanitized"]]:
    """Search tokens

     Get a list of tokens based on search criteria provided in the request body. Searches are done
    against the token id, user id and username.

    __Minimum server version__: 4.7

    ##### Permissions
    Must have `manage_system` permission.

    Args:
        body (SearchUserAccessTokensBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['UserAccessTokenSanitized']
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
