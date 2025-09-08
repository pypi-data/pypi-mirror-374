from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OpenGraphProfile")


@_attrs_define
class OpenGraphProfile:
    """
    Attributes:
        first_name (Union[Unset, str]):
        last_name (Union[Unset, str]):
        username (Union[Unset, str]):
        gender (Union[Unset, str]):
    """

    first_name: Union[Unset, str] = UNSET
    last_name: Union[Unset, str] = UNSET
    username: Union[Unset, str] = UNSET
    gender: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        first_name = self.first_name

        last_name = self.last_name

        username = self.username

        gender = self.gender

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if first_name is not UNSET:
            field_dict["first_name"] = first_name
        if last_name is not UNSET:
            field_dict["last_name"] = last_name
        if username is not UNSET:
            field_dict["username"] = username
        if gender is not UNSET:
            field_dict["gender"] = gender

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        first_name = d.pop("first_name", UNSET)

        last_name = d.pop("last_name", UNSET)

        username = d.pop("username", UNSET)

        gender = d.pop("gender", UNSET)

        open_graph_profile = cls(
            first_name=first_name,
            last_name=last_name,
            username=username,
            gender=gender,
        )

        open_graph_profile.additional_properties = d
        return open_graph_profile

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
