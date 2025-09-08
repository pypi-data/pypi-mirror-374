from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="LoginBody")


@_attrs_define
class LoginBody:
    """
    Attributes:
        id (Union[Unset, str]):
        login_id (Union[Unset, str]):
        token (Union[Unset, str]):
        device_id (Union[Unset, str]):
        ldap_only (Union[Unset, bool]):
        password (Union[Unset, str]): The password used for email authentication.
    """

    id: Union[Unset, str] = UNSET
    login_id: Union[Unset, str] = UNSET
    token: Union[Unset, str] = UNSET
    device_id: Union[Unset, str] = UNSET
    ldap_only: Union[Unset, bool] = UNSET
    password: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        login_id = self.login_id

        token = self.token

        device_id = self.device_id

        ldap_only = self.ldap_only

        password = self.password

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if login_id is not UNSET:
            field_dict["login_id"] = login_id
        if token is not UNSET:
            field_dict["token"] = token
        if device_id is not UNSET:
            field_dict["device_id"] = device_id
        if ldap_only is not UNSET:
            field_dict["ldap_only"] = ldap_only
        if password is not UNSET:
            field_dict["password"] = password

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        login_id = d.pop("login_id", UNSET)

        token = d.pop("token", UNSET)

        device_id = d.pop("device_id", UNSET)

        ldap_only = d.pop("ldap_only", UNSET)

        password = d.pop("password", UNSET)

        login_body = cls(
            id=id,
            login_id=login_id,
            token=token,
            device_id=device_id,
            ldap_only=ldap_only,
            password=password,
        )

        login_body.additional_properties = d
        return login_body

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
