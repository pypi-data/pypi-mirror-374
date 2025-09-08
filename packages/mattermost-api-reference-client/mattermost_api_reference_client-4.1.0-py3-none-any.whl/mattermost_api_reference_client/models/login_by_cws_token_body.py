from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="LoginByCwsTokenBody")


@_attrs_define
class LoginByCwsTokenBody:
    """
    Attributes:
        login_id (Union[Unset, str]):
        cws_token (Union[Unset, str]):
    """

    login_id: Union[Unset, str] = UNSET
    cws_token: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        login_id = self.login_id

        cws_token = self.cws_token

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if login_id is not UNSET:
            field_dict["login_id"] = login_id
        if cws_token is not UNSET:
            field_dict["cws_token"] = cws_token

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        login_id = d.pop("login_id", UNSET)

        cws_token = d.pop("cws_token", UNSET)

        login_by_cws_token_body = cls(
            login_id=login_id,
            cws_token=cws_token,
        )

        login_by_cws_token_body.additional_properties = d
        return login_by_cws_token_body

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
