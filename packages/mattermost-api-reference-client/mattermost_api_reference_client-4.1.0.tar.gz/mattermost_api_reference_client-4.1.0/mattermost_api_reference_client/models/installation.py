from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.allowed_ip_range import AllowedIPRange


T = TypeVar("T", bound="Installation")


@_attrs_define
class Installation:
    """
    Attributes:
        id (Union[Unset, str]): A unique identifier
        allowed_ip_ranges (Union[Unset, AllowedIPRange]):
        state (Union[Unset, str]): The current state of the installation
    """

    id: Union[Unset, str] = UNSET
    allowed_ip_ranges: Union[Unset, "AllowedIPRange"] = UNSET
    state: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        allowed_ip_ranges: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.allowed_ip_ranges, Unset):
            allowed_ip_ranges = self.allowed_ip_ranges.to_dict()

        state = self.state

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if allowed_ip_ranges is not UNSET:
            field_dict["allowed_ip_ranges"] = allowed_ip_ranges
        if state is not UNSET:
            field_dict["state"] = state

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.allowed_ip_range import AllowedIPRange

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        _allowed_ip_ranges = d.pop("allowed_ip_ranges", UNSET)
        allowed_ip_ranges: Union[Unset, AllowedIPRange]
        if isinstance(_allowed_ip_ranges, Unset):
            allowed_ip_ranges = UNSET
        else:
            allowed_ip_ranges = AllowedIPRange.from_dict(_allowed_ip_ranges)

        state = d.pop("state", UNSET)

        installation = cls(
            id=id,
            allowed_ip_ranges=allowed_ip_ranges,
            state=state,
        )

        installation.additional_properties = d
        return installation

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
