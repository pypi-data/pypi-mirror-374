from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateUserStatusBody")


@_attrs_define
class UpdateUserStatusBody:
    """
    Attributes:
        user_id (str): User ID
        status (str): User status, can be `online`, `away`, `offline` and `dnd`
        dnd_end_time (Union[Unset, int]): Time in epoch seconds at which a dnd status would be unset.
    """

    user_id: str
    status: str
    dnd_end_time: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_id = self.user_id

        status = self.status

        dnd_end_time = self.dnd_end_time

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user_id": user_id,
                "status": status,
            }
        )
        if dnd_end_time is not UNSET:
            field_dict["dnd_end_time"] = dnd_end_time

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        user_id = d.pop("user_id")

        status = d.pop("status")

        dnd_end_time = d.pop("dnd_end_time", UNSET)

        update_user_status_body = cls(
            user_id=user_id,
            status=status,
            dnd_end_time=dnd_end_time,
        )

        update_user_status_body.additional_properties = d
        return update_user_status_body

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
