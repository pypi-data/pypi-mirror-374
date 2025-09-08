from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SwitchAccountTypeResponse200")


@_attrs_define
class SwitchAccountTypeResponse200:
    """
    Attributes:
        follow_link (Union[Unset, str]): The link for the user to follow to login or to complete the account switching
            when the current service is OAuth2/SAML
    """

    follow_link: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        follow_link = self.follow_link

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if follow_link is not UNSET:
            field_dict["follow_link"] = follow_link

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        follow_link = d.pop("follow_link", UNSET)

        switch_account_type_response_200 = cls(
            follow_link=follow_link,
        )

        switch_account_type_response_200.additional_properties = d
        return switch_account_type_response_200

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
