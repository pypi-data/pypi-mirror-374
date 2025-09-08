from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.create_group_body_group import CreateGroupBodyGroup


T = TypeVar("T", bound="CreateGroupBody")


@_attrs_define
class CreateGroupBody:
    """
    Attributes:
        group (CreateGroupBodyGroup): Group object to create.
        user_ids (list[str]): The user ids of the group members to add.
    """

    group: "CreateGroupBodyGroup"
    user_ids: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        group = self.group.to_dict()

        user_ids = self.user_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "group": group,
                "user_ids": user_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_group_body_group import CreateGroupBodyGroup

        d = dict(src_dict)
        group = CreateGroupBodyGroup.from_dict(d.pop("group"))

        user_ids = cast(list[str], d.pop("user_ids"))

        create_group_body = cls(
            group=group,
            user_ids=user_ids,
        )

        create_group_body.additional_properties = d
        return create_group_body

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
