from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Compliance")


@_attrs_define
class Compliance:
    """
    Attributes:
        id (Union[Unset, str]):
        create_at (Union[Unset, int]):
        user_id (Union[Unset, str]):
        status (Union[Unset, str]):
        count (Union[Unset, int]):
        desc (Union[Unset, str]):
        type_ (Union[Unset, str]):
        start_at (Union[Unset, int]):
        end_at (Union[Unset, int]):
        keywords (Union[Unset, str]):
        emails (Union[Unset, str]):
    """

    id: Union[Unset, str] = UNSET
    create_at: Union[Unset, int] = UNSET
    user_id: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    count: Union[Unset, int] = UNSET
    desc: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    start_at: Union[Unset, int] = UNSET
    end_at: Union[Unset, int] = UNSET
    keywords: Union[Unset, str] = UNSET
    emails: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        create_at = self.create_at

        user_id = self.user_id

        status = self.status

        count = self.count

        desc = self.desc

        type_ = self.type_

        start_at = self.start_at

        end_at = self.end_at

        keywords = self.keywords

        emails = self.emails

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if create_at is not UNSET:
            field_dict["create_at"] = create_at
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if status is not UNSET:
            field_dict["status"] = status
        if count is not UNSET:
            field_dict["count"] = count
        if desc is not UNSET:
            field_dict["desc"] = desc
        if type_ is not UNSET:
            field_dict["type"] = type_
        if start_at is not UNSET:
            field_dict["start_at"] = start_at
        if end_at is not UNSET:
            field_dict["end_at"] = end_at
        if keywords is not UNSET:
            field_dict["keywords"] = keywords
        if emails is not UNSET:
            field_dict["emails"] = emails

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        create_at = d.pop("create_at", UNSET)

        user_id = d.pop("user_id", UNSET)

        status = d.pop("status", UNSET)

        count = d.pop("count", UNSET)

        desc = d.pop("desc", UNSET)

        type_ = d.pop("type", UNSET)

        start_at = d.pop("start_at", UNSET)

        end_at = d.pop("end_at", UNSET)

        keywords = d.pop("keywords", UNSET)

        emails = d.pop("emails", UNSET)

        compliance = cls(
            id=id,
            create_at=create_at,
            user_id=user_id,
            status=status,
            count=count,
            desc=desc,
            type_=type_,
            start_at=start_at,
            end_at=end_at,
            keywords=keywords,
            emails=emails,
        )

        compliance.additional_properties = d
        return compliance

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
