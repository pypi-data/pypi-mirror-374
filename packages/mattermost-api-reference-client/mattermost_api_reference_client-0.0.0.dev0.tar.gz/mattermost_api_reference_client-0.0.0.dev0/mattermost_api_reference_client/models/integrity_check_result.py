from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.relational_integrity_check_data import RelationalIntegrityCheckData


T = TypeVar("T", bound="IntegrityCheckResult")


@_attrs_define
class IntegrityCheckResult:
    """an object with the result of the integrity check.

    Attributes:
        data (Union[Unset, RelationalIntegrityCheckData]): an object containing the results of a relational integrity
            check.
        err (Union[Unset, str]): a string value set in case of error.
    """

    data: Union[Unset, "RelationalIntegrityCheckData"] = UNSET
    err: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.data, Unset):
            data = self.data.to_dict()

        err = self.err

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if data is not UNSET:
            field_dict["data"] = data
        if err is not UNSET:
            field_dict["err"] = err

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.relational_integrity_check_data import RelationalIntegrityCheckData

        d = dict(src_dict)
        _data = d.pop("data", UNSET)
        data: Union[Unset, RelationalIntegrityCheckData]
        if isinstance(_data, Unset):
            data = UNSET
        else:
            data = RelationalIntegrityCheckData.from_dict(_data)

        err = d.pop("err", UNSET)

        integrity_check_result = cls(
            data=data,
            err=err,
        )

        integrity_check_result.additional_properties = d
        return integrity_check_result

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
