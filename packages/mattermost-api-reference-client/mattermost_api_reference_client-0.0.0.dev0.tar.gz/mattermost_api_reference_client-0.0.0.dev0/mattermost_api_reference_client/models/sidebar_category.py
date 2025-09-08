from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.sidebar_category_type import SidebarCategoryType
from ..types import UNSET, Unset

T = TypeVar("T", bound="SidebarCategory")


@_attrs_define
class SidebarCategory:
    """User's sidebar category

    Attributes:
        id (Union[Unset, str]):
        user_id (Union[Unset, str]):
        team_id (Union[Unset, str]):
        display_name (Union[Unset, str]):
        type_ (Union[Unset, SidebarCategoryType]):
    """

    id: Union[Unset, str] = UNSET
    user_id: Union[Unset, str] = UNSET
    team_id: Union[Unset, str] = UNSET
    display_name: Union[Unset, str] = UNSET
    type_: Union[Unset, SidebarCategoryType] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        user_id = self.user_id

        team_id = self.team_id

        display_name = self.display_name

        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if team_id is not UNSET:
            field_dict["team_id"] = team_id
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        user_id = d.pop("user_id", UNSET)

        team_id = d.pop("team_id", UNSET)

        display_name = d.pop("display_name", UNSET)

        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, SidebarCategoryType]
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = SidebarCategoryType(_type_)

        sidebar_category = cls(
            id=id,
            user_id=user_id,
            team_id=team_id,
            display_name=display_name,
            type_=type_,
        )

        sidebar_category.additional_properties = d
        return sidebar_category

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
