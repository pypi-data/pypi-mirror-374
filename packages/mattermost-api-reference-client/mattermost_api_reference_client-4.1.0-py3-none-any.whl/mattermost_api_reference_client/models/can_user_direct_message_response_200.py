from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CanUserDirectMessageResponse200")


@_attrs_define
class CanUserDirectMessageResponse200:
    """
    Attributes:
        can_dm (Union[Unset, bool]): Whether the user can send DMs to the other user
    """

    can_dm: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        can_dm = self.can_dm

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if can_dm is not UNSET:
            field_dict["can_dm"] = can_dm

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        can_dm = d.pop("can_dm", UNSET)

        can_user_direct_message_response_200 = cls(
            can_dm=can_dm,
        )

        can_user_direct_message_response_200.additional_properties = d
        return can_user_direct_message_response_200

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
