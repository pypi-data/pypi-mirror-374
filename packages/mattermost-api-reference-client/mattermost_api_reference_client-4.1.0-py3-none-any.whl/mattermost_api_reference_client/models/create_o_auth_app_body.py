from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateOAuthAppBody")


@_attrs_define
class CreateOAuthAppBody:
    """
    Attributes:
        name (str): The name of the client application
        description (str): A short description of the application
        callback_urls (list[str]): A list of callback URLs for the appliation
        homepage (str): A link to the website of the application
        icon_url (Union[Unset, str]): A URL to an icon to display with the application
        is_trusted (Union[Unset, bool]): Set this to `true` to skip asking users for permission
    """

    name: str
    description: str
    callback_urls: list[str]
    homepage: str
    icon_url: Union[Unset, str] = UNSET
    is_trusted: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        callback_urls = self.callback_urls

        homepage = self.homepage

        icon_url = self.icon_url

        is_trusted = self.is_trusted

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "callback_urls": callback_urls,
                "homepage": homepage,
            }
        )
        if icon_url is not UNSET:
            field_dict["icon_url"] = icon_url
        if is_trusted is not UNSET:
            field_dict["is_trusted"] = is_trusted

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description")

        callback_urls = cast(list[str], d.pop("callback_urls"))

        homepage = d.pop("homepage")

        icon_url = d.pop("icon_url", UNSET)

        is_trusted = d.pop("is_trusted", UNSET)

        create_o_auth_app_body = cls(
            name=name,
            description=description,
            callback_urls=callback_urls,
            homepage=homepage,
            icon_url=icon_url,
            is_trusted=is_trusted,
        )

        create_o_auth_app_body.additional_properties = d
        return create_o_auth_app_body

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
