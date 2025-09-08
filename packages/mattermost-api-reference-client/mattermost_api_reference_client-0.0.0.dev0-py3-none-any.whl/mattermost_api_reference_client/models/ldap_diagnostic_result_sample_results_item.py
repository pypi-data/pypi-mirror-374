from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.ldap_diagnostic_result_sample_results_item_available_attributes import (
        LdapDiagnosticResultSampleResultsItemAvailableAttributes,
    )


T = TypeVar("T", bound="LdapDiagnosticResultSampleResultsItem")


@_attrs_define
class LdapDiagnosticResultSampleResultsItem:
    """
    Attributes:
        dn (Union[Unset, str]): Distinguished Name
        username (Union[Unset, str]): Username
        email (Union[Unset, str]): Email
        first_name (Union[Unset, str]): First name
        last_name (Union[Unset, str]): Last name
        id (Union[Unset, str]): ID attribute
        display_name (Union[Unset, str]): Display name for groups
        available_attributes (Union[Unset, LdapDiagnosticResultSampleResultsItemAvailableAttributes]): Map of all
            available LDAP attributes
    """

    dn: Union[Unset, str] = UNSET
    username: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    first_name: Union[Unset, str] = UNSET
    last_name: Union[Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    display_name: Union[Unset, str] = UNSET
    available_attributes: Union[Unset, "LdapDiagnosticResultSampleResultsItemAvailableAttributes"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        dn = self.dn

        username = self.username

        email = self.email

        first_name = self.first_name

        last_name = self.last_name

        id = self.id

        display_name = self.display_name

        available_attributes: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.available_attributes, Unset):
            available_attributes = self.available_attributes.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if dn is not UNSET:
            field_dict["dn"] = dn
        if username is not UNSET:
            field_dict["username"] = username
        if email is not UNSET:
            field_dict["email"] = email
        if first_name is not UNSET:
            field_dict["first_name"] = first_name
        if last_name is not UNSET:
            field_dict["last_name"] = last_name
        if id is not UNSET:
            field_dict["id"] = id
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if available_attributes is not UNSET:
            field_dict["available_attributes"] = available_attributes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.ldap_diagnostic_result_sample_results_item_available_attributes import (
            LdapDiagnosticResultSampleResultsItemAvailableAttributes,
        )

        d = dict(src_dict)
        dn = d.pop("dn", UNSET)

        username = d.pop("username", UNSET)

        email = d.pop("email", UNSET)

        first_name = d.pop("first_name", UNSET)

        last_name = d.pop("last_name", UNSET)

        id = d.pop("id", UNSET)

        display_name = d.pop("display_name", UNSET)

        _available_attributes = d.pop("available_attributes", UNSET)
        available_attributes: Union[Unset, LdapDiagnosticResultSampleResultsItemAvailableAttributes]
        if isinstance(_available_attributes, Unset):
            available_attributes = UNSET
        else:
            available_attributes = LdapDiagnosticResultSampleResultsItemAvailableAttributes.from_dict(
                _available_attributes
            )

        ldap_diagnostic_result_sample_results_item = cls(
            dn=dn,
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            id=id,
            display_name=display_name,
            available_attributes=available_attributes,
        )

        ldap_diagnostic_result_sample_results_item.additional_properties = d
        return ldap_diagnostic_result_sample_results_item

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
