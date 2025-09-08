from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OAuthApp")


@_attrs_define
class OAuthApp:
    """
    Attributes:
        id (Union[Unset, str]): The client id of the application
        client_secret (Union[Unset, str]): The client secret of the application
        name (Union[Unset, str]): The name of the client application
        description (Union[Unset, str]): A short description of the application
        icon_url (Union[Unset, str]): A URL to an icon to display with the application
        callback_urls (Union[Unset, list[str]]): A list of callback URLs for the appliation
        homepage (Union[Unset, str]): A link to the website of the application
        is_trusted (Union[Unset, bool]): Set this to `true` to skip asking users for permission
        create_at (Union[Unset, int]): The time of registration for the application
        update_at (Union[Unset, int]): The last time of update for the application
    """

    id: Union[Unset, str] = UNSET
    client_secret: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    icon_url: Union[Unset, str] = UNSET
    callback_urls: Union[Unset, list[str]] = UNSET
    homepage: Union[Unset, str] = UNSET
    is_trusted: Union[Unset, bool] = UNSET
    create_at: Union[Unset, int] = UNSET
    update_at: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        client_secret = self.client_secret

        name = self.name

        description = self.description

        icon_url = self.icon_url

        callback_urls: Union[Unset, list[str]] = UNSET
        if not isinstance(self.callback_urls, Unset):
            callback_urls = self.callback_urls

        homepage = self.homepage

        is_trusted = self.is_trusted

        create_at = self.create_at

        update_at = self.update_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if client_secret is not UNSET:
            field_dict["client_secret"] = client_secret
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if icon_url is not UNSET:
            field_dict["icon_url"] = icon_url
        if callback_urls is not UNSET:
            field_dict["callback_urls"] = callback_urls
        if homepage is not UNSET:
            field_dict["homepage"] = homepage
        if is_trusted is not UNSET:
            field_dict["is_trusted"] = is_trusted
        if create_at is not UNSET:
            field_dict["create_at"] = create_at
        if update_at is not UNSET:
            field_dict["update_at"] = update_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        client_secret = d.pop("client_secret", UNSET)

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        icon_url = d.pop("icon_url", UNSET)

        callback_urls = cast(list[str], d.pop("callback_urls", UNSET))

        homepage = d.pop("homepage", UNSET)

        is_trusted = d.pop("is_trusted", UNSET)

        create_at = d.pop("create_at", UNSET)

        update_at = d.pop("update_at", UNSET)

        o_auth_app = cls(
            id=id,
            client_secret=client_secret,
            name=name,
            description=description,
            icon_url=icon_url,
            callback_urls=callback_urls,
            homepage=homepage,
            is_trusted=is_trusted,
            create_at=create_at,
            update_at=update_at,
        )

        o_auth_app.additional_properties = d
        return o_auth_app

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
