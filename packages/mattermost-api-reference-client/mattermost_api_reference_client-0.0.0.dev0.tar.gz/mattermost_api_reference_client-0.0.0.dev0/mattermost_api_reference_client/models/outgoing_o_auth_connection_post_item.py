from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OutgoingOAuthConnectionPostItem")


@_attrs_define
class OutgoingOAuthConnectionPostItem:
    """
    Attributes:
        name (Union[Unset, str]): The name of the outgoing OAuth connection.
        client_id (Union[Unset, str]): The client ID of the outgoing OAuth connection.
        client_secret (Union[Unset, str]): The client secret of the outgoing OAuth connection.
        credentials_username (Union[Unset, str]): The username of the credentials of the outgoing OAuth connection.
        credentials_password (Union[Unset, str]): The password of the credentials of the outgoing OAuth connection.
        oauth_token_url (Union[Unset, str]): The OAuth token URL of the outgoing OAuth connection.
        grant_type (Union[Unset, str]): The grant type of the outgoing OAuth connection.
        audiences (Union[Unset, str]): The audiences of the outgoing OAuth connection.
    """

    name: Union[Unset, str] = UNSET
    client_id: Union[Unset, str] = UNSET
    client_secret: Union[Unset, str] = UNSET
    credentials_username: Union[Unset, str] = UNSET
    credentials_password: Union[Unset, str] = UNSET
    oauth_token_url: Union[Unset, str] = UNSET
    grant_type: Union[Unset, str] = UNSET
    audiences: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        client_id = self.client_id

        client_secret = self.client_secret

        credentials_username = self.credentials_username

        credentials_password = self.credentials_password

        oauth_token_url = self.oauth_token_url

        grant_type = self.grant_type

        audiences = self.audiences

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if client_id is not UNSET:
            field_dict["client_id"] = client_id
        if client_secret is not UNSET:
            field_dict["client_secret"] = client_secret
        if credentials_username is not UNSET:
            field_dict["credentials_username"] = credentials_username
        if credentials_password is not UNSET:
            field_dict["credentials_password"] = credentials_password
        if oauth_token_url is not UNSET:
            field_dict["oauth_token_url"] = oauth_token_url
        if grant_type is not UNSET:
            field_dict["grant_type"] = grant_type
        if audiences is not UNSET:
            field_dict["audiences"] = audiences

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        client_id = d.pop("client_id", UNSET)

        client_secret = d.pop("client_secret", UNSET)

        credentials_username = d.pop("credentials_username", UNSET)

        credentials_password = d.pop("credentials_password", UNSET)

        oauth_token_url = d.pop("oauth_token_url", UNSET)

        grant_type = d.pop("grant_type", UNSET)

        audiences = d.pop("audiences", UNSET)

        outgoing_o_auth_connection_post_item = cls(
            name=name,
            client_id=client_id,
            client_secret=client_secret,
            credentials_username=credentials_username,
            credentials_password=credentials_password,
            oauth_token_url=oauth_token_url,
            grant_type=grant_type,
            audiences=audiences,
        )

        outgoing_o_auth_connection_post_item.additional_properties = d
        return outgoing_o_auth_connection_post_item

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
