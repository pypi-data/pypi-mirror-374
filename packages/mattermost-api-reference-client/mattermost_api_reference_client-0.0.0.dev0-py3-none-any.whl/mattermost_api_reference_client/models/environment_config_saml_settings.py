from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EnvironmentConfigSamlSettings")


@_attrs_define
class EnvironmentConfigSamlSettings:
    """
    Attributes:
        enable (Union[Unset, bool]):
        verify (Union[Unset, bool]):
        encrypt (Union[Unset, bool]):
        idp_url (Union[Unset, bool]):
        idp_descriptor_url (Union[Unset, bool]):
        assertion_consumer_service_url (Union[Unset, bool]):
        idp_certificate_file (Union[Unset, bool]):
        public_certificate_file (Union[Unset, bool]):
        private_key_file (Union[Unset, bool]):
        first_name_attribute (Union[Unset, bool]):
        last_name_attribute (Union[Unset, bool]):
        email_attribute (Union[Unset, bool]):
        username_attribute (Union[Unset, bool]):
        nickname_attribute (Union[Unset, bool]):
        locale_attribute (Union[Unset, bool]):
        position_attribute (Union[Unset, bool]):
        login_button_text (Union[Unset, bool]):
    """

    enable: Union[Unset, bool] = UNSET
    verify: Union[Unset, bool] = UNSET
    encrypt: Union[Unset, bool] = UNSET
    idp_url: Union[Unset, bool] = UNSET
    idp_descriptor_url: Union[Unset, bool] = UNSET
    assertion_consumer_service_url: Union[Unset, bool] = UNSET
    idp_certificate_file: Union[Unset, bool] = UNSET
    public_certificate_file: Union[Unset, bool] = UNSET
    private_key_file: Union[Unset, bool] = UNSET
    first_name_attribute: Union[Unset, bool] = UNSET
    last_name_attribute: Union[Unset, bool] = UNSET
    email_attribute: Union[Unset, bool] = UNSET
    username_attribute: Union[Unset, bool] = UNSET
    nickname_attribute: Union[Unset, bool] = UNSET
    locale_attribute: Union[Unset, bool] = UNSET
    position_attribute: Union[Unset, bool] = UNSET
    login_button_text: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enable = self.enable

        verify = self.verify

        encrypt = self.encrypt

        idp_url = self.idp_url

        idp_descriptor_url = self.idp_descriptor_url

        assertion_consumer_service_url = self.assertion_consumer_service_url

        idp_certificate_file = self.idp_certificate_file

        public_certificate_file = self.public_certificate_file

        private_key_file = self.private_key_file

        first_name_attribute = self.first_name_attribute

        last_name_attribute = self.last_name_attribute

        email_attribute = self.email_attribute

        username_attribute = self.username_attribute

        nickname_attribute = self.nickname_attribute

        locale_attribute = self.locale_attribute

        position_attribute = self.position_attribute

        login_button_text = self.login_button_text

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enable is not UNSET:
            field_dict["Enable"] = enable
        if verify is not UNSET:
            field_dict["Verify"] = verify
        if encrypt is not UNSET:
            field_dict["Encrypt"] = encrypt
        if idp_url is not UNSET:
            field_dict["IdpUrl"] = idp_url
        if idp_descriptor_url is not UNSET:
            field_dict["IdpDescriptorUrl"] = idp_descriptor_url
        if assertion_consumer_service_url is not UNSET:
            field_dict["AssertionConsumerServiceURL"] = assertion_consumer_service_url
        if idp_certificate_file is not UNSET:
            field_dict["IdpCertificateFile"] = idp_certificate_file
        if public_certificate_file is not UNSET:
            field_dict["PublicCertificateFile"] = public_certificate_file
        if private_key_file is not UNSET:
            field_dict["PrivateKeyFile"] = private_key_file
        if first_name_attribute is not UNSET:
            field_dict["FirstNameAttribute"] = first_name_attribute
        if last_name_attribute is not UNSET:
            field_dict["LastNameAttribute"] = last_name_attribute
        if email_attribute is not UNSET:
            field_dict["EmailAttribute"] = email_attribute
        if username_attribute is not UNSET:
            field_dict["UsernameAttribute"] = username_attribute
        if nickname_attribute is not UNSET:
            field_dict["NicknameAttribute"] = nickname_attribute
        if locale_attribute is not UNSET:
            field_dict["LocaleAttribute"] = locale_attribute
        if position_attribute is not UNSET:
            field_dict["PositionAttribute"] = position_attribute
        if login_button_text is not UNSET:
            field_dict["LoginButtonText"] = login_button_text

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        enable = d.pop("Enable", UNSET)

        verify = d.pop("Verify", UNSET)

        encrypt = d.pop("Encrypt", UNSET)

        idp_url = d.pop("IdpUrl", UNSET)

        idp_descriptor_url = d.pop("IdpDescriptorUrl", UNSET)

        assertion_consumer_service_url = d.pop("AssertionConsumerServiceURL", UNSET)

        idp_certificate_file = d.pop("IdpCertificateFile", UNSET)

        public_certificate_file = d.pop("PublicCertificateFile", UNSET)

        private_key_file = d.pop("PrivateKeyFile", UNSET)

        first_name_attribute = d.pop("FirstNameAttribute", UNSET)

        last_name_attribute = d.pop("LastNameAttribute", UNSET)

        email_attribute = d.pop("EmailAttribute", UNSET)

        username_attribute = d.pop("UsernameAttribute", UNSET)

        nickname_attribute = d.pop("NicknameAttribute", UNSET)

        locale_attribute = d.pop("LocaleAttribute", UNSET)

        position_attribute = d.pop("PositionAttribute", UNSET)

        login_button_text = d.pop("LoginButtonText", UNSET)

        environment_config_saml_settings = cls(
            enable=enable,
            verify=verify,
            encrypt=encrypt,
            idp_url=idp_url,
            idp_descriptor_url=idp_descriptor_url,
            assertion_consumer_service_url=assertion_consumer_service_url,
            idp_certificate_file=idp_certificate_file,
            public_certificate_file=public_certificate_file,
            private_key_file=private_key_file,
            first_name_attribute=first_name_attribute,
            last_name_attribute=last_name_attribute,
            email_attribute=email_attribute,
            username_attribute=username_attribute,
            nickname_attribute=nickname_attribute,
            locale_attribute=locale_attribute,
            position_attribute=position_attribute,
            login_button_text=login_button_text,
        )

        environment_config_saml_settings.additional_properties = d
        return environment_config_saml_settings

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
