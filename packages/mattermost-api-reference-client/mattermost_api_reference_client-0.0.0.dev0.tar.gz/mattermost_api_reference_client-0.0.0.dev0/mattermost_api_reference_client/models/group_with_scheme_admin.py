from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.group import Group


T = TypeVar("T", bound="GroupWithSchemeAdmin")


@_attrs_define
class GroupWithSchemeAdmin:
    """group augmented with scheme admin information

    Attributes:
        group (Union[Unset, Group]):
        scheme_admin (Union[Unset, bool]):
    """

    group: Union[Unset, "Group"] = UNSET
    scheme_admin: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        group: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.group, Unset):
            group = self.group.to_dict()

        scheme_admin = self.scheme_admin

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if group is not UNSET:
            field_dict["group"] = group
        if scheme_admin is not UNSET:
            field_dict["scheme_admin"] = scheme_admin

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.group import Group

        d = dict(src_dict)
        _group = d.pop("group", UNSET)
        group: Union[Unset, Group]
        if isinstance(_group, Unset):
            group = UNSET
        else:
            group = Group.from_dict(_group)

        scheme_admin = d.pop("scheme_admin", UNSET)

        group_with_scheme_admin = cls(
            group=group,
            scheme_admin=scheme_admin,
        )

        group_with_scheme_admin.additional_properties = d
        return group_with_scheme_admin

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
