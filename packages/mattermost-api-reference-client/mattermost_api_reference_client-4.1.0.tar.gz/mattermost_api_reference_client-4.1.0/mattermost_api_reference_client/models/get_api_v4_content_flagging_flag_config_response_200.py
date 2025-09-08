from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetApiV4ContentFlaggingFlagConfigResponse200")


@_attrs_define
class GetApiV4ContentFlaggingFlagConfigResponse200:
    """
    Attributes:
        reasons (Union[Unset, list[str]]): List of reasons for flagging content
        reporter_comment_required (Union[Unset, bool]): Indicates if a comment from the reporter is required when
            flagging content
    """

    reasons: Union[Unset, list[str]] = UNSET
    reporter_comment_required: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        reasons: Union[Unset, list[str]] = UNSET
        if not isinstance(self.reasons, Unset):
            reasons = self.reasons

        reporter_comment_required = self.reporter_comment_required

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if reasons is not UNSET:
            field_dict["reasons"] = reasons
        if reporter_comment_required is not UNSET:
            field_dict["reporter_comment_required"] = reporter_comment_required

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        reasons = cast(list[str], d.pop("reasons", UNSET))

        reporter_comment_required = d.pop("reporter_comment_required", UNSET)

        get_api_v4_content_flagging_flag_config_response_200 = cls(
            reasons=reasons,
            reporter_comment_required=reporter_comment_required,
        )

        get_api_v4_content_flagging_flag_config_response_200.additional_properties = d
        return get_api_v4_content_flagging_flag_config_response_200

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
