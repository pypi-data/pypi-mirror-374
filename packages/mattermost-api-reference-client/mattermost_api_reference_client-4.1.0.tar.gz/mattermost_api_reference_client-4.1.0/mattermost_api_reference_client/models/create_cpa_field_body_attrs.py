from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.create_cpa_field_body_attrs_value_type import CreateCPAFieldBodyAttrsValueType
from ..models.create_cpa_field_body_attrs_visibility import CreateCPAFieldBodyAttrsVisibility
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_cpa_field_body_attrs_options_item import CreateCPAFieldBodyAttrsOptionsItem


T = TypeVar("T", bound="CreateCPAFieldBodyAttrs")


@_attrs_define
class CreateCPAFieldBodyAttrs:
    """
    Attributes:
        visibility (Union[Unset, CreateCPAFieldBodyAttrsVisibility]): Visibility of the attribute Default:
            CreateCPAFieldBodyAttrsVisibility.WHEN_SET.
        sort_order (Union[Unset, float]): Sort order for displaying this attribute
        options (Union[Unset, list['CreateCPAFieldBodyAttrsOptionsItem']]): Options for select/multiselect fields
        value_type (Union[Unset, CreateCPAFieldBodyAttrsValueType]): Type of text value
        ldap (Union[Unset, str]): LDAP attribute for syncing
        saml (Union[Unset, str]): SAML attribute for syncing
    """

    visibility: Union[Unset, CreateCPAFieldBodyAttrsVisibility] = CreateCPAFieldBodyAttrsVisibility.WHEN_SET
    sort_order: Union[Unset, float] = UNSET
    options: Union[Unset, list["CreateCPAFieldBodyAttrsOptionsItem"]] = UNSET
    value_type: Union[Unset, CreateCPAFieldBodyAttrsValueType] = UNSET
    ldap: Union[Unset, str] = UNSET
    saml: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        visibility: Union[Unset, str] = UNSET
        if not isinstance(self.visibility, Unset):
            visibility = self.visibility.value

        sort_order = self.sort_order

        options: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.options, Unset):
            options = []
            for options_item_data in self.options:
                options_item = options_item_data.to_dict()
                options.append(options_item)

        value_type: Union[Unset, str] = UNSET
        if not isinstance(self.value_type, Unset):
            value_type = self.value_type.value

        ldap = self.ldap

        saml = self.saml

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if visibility is not UNSET:
            field_dict["visibility"] = visibility
        if sort_order is not UNSET:
            field_dict["sort_order"] = sort_order
        if options is not UNSET:
            field_dict["options"] = options
        if value_type is not UNSET:
            field_dict["value_type"] = value_type
        if ldap is not UNSET:
            field_dict["ldap"] = ldap
        if saml is not UNSET:
            field_dict["saml"] = saml

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_cpa_field_body_attrs_options_item import CreateCPAFieldBodyAttrsOptionsItem

        d = dict(src_dict)
        _visibility = d.pop("visibility", UNSET)
        visibility: Union[Unset, CreateCPAFieldBodyAttrsVisibility]
        if isinstance(_visibility, Unset):
            visibility = UNSET
        else:
            visibility = CreateCPAFieldBodyAttrsVisibility(_visibility)

        sort_order = d.pop("sort_order", UNSET)

        options = []
        _options = d.pop("options", UNSET)
        for options_item_data in _options or []:
            options_item = CreateCPAFieldBodyAttrsOptionsItem.from_dict(options_item_data)

            options.append(options_item)

        _value_type = d.pop("value_type", UNSET)
        value_type: Union[Unset, CreateCPAFieldBodyAttrsValueType]
        if isinstance(_value_type, Unset):
            value_type = UNSET
        else:
            value_type = CreateCPAFieldBodyAttrsValueType(_value_type)

        ldap = d.pop("ldap", UNSET)

        saml = d.pop("saml", UNSET)

        create_cpa_field_body_attrs = cls(
            visibility=visibility,
            sort_order=sort_order,
            options=options,
            value_type=value_type,
            ldap=ldap,
            saml=saml,
        )

        create_cpa_field_body_attrs.additional_properties = d
        return create_cpa_field_body_attrs

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
