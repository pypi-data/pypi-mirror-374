from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AccessControlPolicy")


@_attrs_define
class AccessControlPolicy:
    """
    Attributes:
        id (Union[Unset, str]): The unique identifier of the policy.
        name (Union[Unset, str]): The unique name for the policy.
        display_name (Union[Unset, str]): The human-readable name for the policy.
        description (Union[Unset, str]): A description of the policy.
        expression (Union[Unset, str]): The CEL expression defining the policy rules.
        is_active (Union[Unset, bool]): Whether the policy is currently active and enforced.
        create_at (Union[Unset, int]): The time in milliseconds the policy was created.
        update_at (Union[Unset, int]): The time in milliseconds the policy was last updated.
        delete_at (Union[Unset, int]): The time in milliseconds the policy was deleted.
    """

    id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    display_name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    expression: Union[Unset, str] = UNSET
    is_active: Union[Unset, bool] = UNSET
    create_at: Union[Unset, int] = UNSET
    update_at: Union[Unset, int] = UNSET
    delete_at: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        display_name = self.display_name

        description = self.description

        expression = self.expression

        is_active = self.is_active

        create_at = self.create_at

        update_at = self.update_at

        delete_at = self.delete_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if description is not UNSET:
            field_dict["description"] = description
        if expression is not UNSET:
            field_dict["expression"] = expression
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if create_at is not UNSET:
            field_dict["create_at"] = create_at
        if update_at is not UNSET:
            field_dict["update_at"] = update_at
        if delete_at is not UNSET:
            field_dict["delete_at"] = delete_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        display_name = d.pop("display_name", UNSET)

        description = d.pop("description", UNSET)

        expression = d.pop("expression", UNSET)

        is_active = d.pop("is_active", UNSET)

        create_at = d.pop("create_at", UNSET)

        update_at = d.pop("update_at", UNSET)

        delete_at = d.pop("delete_at", UNSET)

        access_control_policy = cls(
            id=id,
            name=name,
            display_name=display_name,
            description=description,
            expression=expression,
            is_active=is_active,
            create_at=create_at,
            update_at=update_at,
            delete_at=delete_at,
        )

        access_control_policy.additional_properties = d
        return access_control_policy

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
