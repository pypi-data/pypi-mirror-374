from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CheckUserMfaResponse200")


@_attrs_define
class CheckUserMfaResponse200:
    """
    Attributes:
        mfa_required (Union[Unset, bool]): Value will `true` if MFA is active, `false` otherwise
    """

    mfa_required: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        mfa_required = self.mfa_required

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if mfa_required is not UNSET:
            field_dict["mfa_required"] = mfa_required

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        mfa_required = d.pop("mfa_required", UNSET)

        check_user_mfa_response_200 = cls(
            mfa_required=mfa_required,
        )

        check_user_mfa_response_200.additional_properties = d
        return check_user_mfa_response_200

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
