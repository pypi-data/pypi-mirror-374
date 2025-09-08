from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.access_control_policy import AccessControlPolicy


T = TypeVar("T", bound="AccessControlPoliciesWithCount")


@_attrs_define
class AccessControlPoliciesWithCount:
    """
    Attributes:
        policies (Union[Unset, list['AccessControlPolicy']]):
        total_count (Union[Unset, int]): The total number of policies.
    """

    policies: Union[Unset, list["AccessControlPolicy"]] = UNSET
    total_count: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        policies: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.policies, Unset):
            policies = []
            for policies_item_data in self.policies:
                policies_item = policies_item_data.to_dict()
                policies.append(policies_item)

        total_count = self.total_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if policies is not UNSET:
            field_dict["policies"] = policies
        if total_count is not UNSET:
            field_dict["total_count"] = total_count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.access_control_policy import AccessControlPolicy

        d = dict(src_dict)
        policies = []
        _policies = d.pop("policies", UNSET)
        for policies_item_data in _policies or []:
            policies_item = AccessControlPolicy.from_dict(policies_item_data)

            policies.append(policies_item)

        total_count = d.pop("total_count", UNSET)

        access_control_policies_with_count = cls(
            policies=policies,
            total_count=total_count,
        )

        access_control_policies_with_count.additional_properties = d
        return access_control_policies_with_count

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
