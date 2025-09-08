from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Audit")


@_attrs_define
class Audit:
    """
    Attributes:
        id (Union[Unset, str]):
        create_at (Union[Unset, int]): The time in milliseconds a audit was created
        user_id (Union[Unset, str]):
        action (Union[Unset, str]):
        extra_info (Union[Unset, str]):
        ip_address (Union[Unset, str]):
        session_id (Union[Unset, str]):
    """

    id: Union[Unset, str] = UNSET
    create_at: Union[Unset, int] = UNSET
    user_id: Union[Unset, str] = UNSET
    action: Union[Unset, str] = UNSET
    extra_info: Union[Unset, str] = UNSET
    ip_address: Union[Unset, str] = UNSET
    session_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        create_at = self.create_at

        user_id = self.user_id

        action = self.action

        extra_info = self.extra_info

        ip_address = self.ip_address

        session_id = self.session_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if create_at is not UNSET:
            field_dict["create_at"] = create_at
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if action is not UNSET:
            field_dict["action"] = action
        if extra_info is not UNSET:
            field_dict["extra_info"] = extra_info
        if ip_address is not UNSET:
            field_dict["ip_address"] = ip_address
        if session_id is not UNSET:
            field_dict["session_id"] = session_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        create_at = d.pop("create_at", UNSET)

        user_id = d.pop("user_id", UNSET)

        action = d.pop("action", UNSET)

        extra_info = d.pop("extra_info", UNSET)

        ip_address = d.pop("ip_address", UNSET)

        session_id = d.pop("session_id", UNSET)

        audit = cls(
            id=id,
            create_at=create_at,
            user_id=user_id,
            action=action,
            extra_info=extra_info,
            ip_address=ip_address,
            session_id=session_id,
        )

        audit.additional_properties = d
        return audit

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
