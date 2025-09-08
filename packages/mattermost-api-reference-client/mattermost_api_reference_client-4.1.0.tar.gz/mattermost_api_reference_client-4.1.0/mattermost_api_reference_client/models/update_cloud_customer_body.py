from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateCloudCustomerBody")


@_attrs_define
class UpdateCloudCustomerBody:
    """
    Attributes:
        name (Union[Unset, str]):
        email (Union[Unset, str]):
        contact_first_name (Union[Unset, str]):
        contact_last_name (Union[Unset, str]):
        num_employees (Union[Unset, str]):
    """

    name: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    contact_first_name: Union[Unset, str] = UNSET
    contact_last_name: Union[Unset, str] = UNSET
    num_employees: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        email = self.email

        contact_first_name = self.contact_first_name

        contact_last_name = self.contact_last_name

        num_employees = self.num_employees

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if email is not UNSET:
            field_dict["email"] = email
        if contact_first_name is not UNSET:
            field_dict["contact_first_name"] = contact_first_name
        if contact_last_name is not UNSET:
            field_dict["contact_last_name"] = contact_last_name
        if num_employees is not UNSET:
            field_dict["num_employees"] = num_employees

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        email = d.pop("email", UNSET)

        contact_first_name = d.pop("contact_first_name", UNSET)

        contact_last_name = d.pop("contact_last_name", UNSET)

        num_employees = d.pop("num_employees", UNSET)

        update_cloud_customer_body = cls(
            name=name,
            email=email,
            contact_first_name=contact_first_name,
            contact_last_name=contact_last_name,
            num_employees=num_employees,
        )

        update_cloud_customer_body.additional_properties = d
        return update_cloud_customer_body

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
