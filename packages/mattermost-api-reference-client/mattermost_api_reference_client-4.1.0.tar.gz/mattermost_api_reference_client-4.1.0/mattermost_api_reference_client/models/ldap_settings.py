from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="LdapSettings")


@_attrs_define
class LdapSettings:
    """
    Attributes:
        enable (Union[Unset, bool]):
        enable_sync (Union[Unset, bool]):
        ldap_server (Union[Unset, str]):
        ldap_port (Union[Unset, int]):
        connection_security (Union[Unset, str]):
        base_dn (Union[Unset, str]):
        bind_username (Union[Unset, str]):
        bind_password (Union[Unset, str]):
        maximum_login_attempts (Union[Unset, int]):
        user_filter (Union[Unset, str]):
        group_filter (Union[Unset, str]):
        guest_filter (Union[Unset, str]):
        enable_admin_filter (Union[Unset, bool]):
        admin_filter (Union[Unset, str]):
        group_display_name_attribute (Union[Unset, str]):
        group_id_attribute (Union[Unset, str]):
        first_name_attribute (Union[Unset, str]):
        last_name_attribute (Union[Unset, str]):
        email_attribute (Union[Unset, str]):
        username_attribute (Union[Unset, str]):
        nickname_attribute (Union[Unset, str]):
        id_attribute (Union[Unset, str]):
        position_attribute (Union[Unset, str]):
        login_id_attribute (Union[Unset, str]):
        picture_attribute (Union[Unset, str]):
        sync_interval_minutes (Union[Unset, int]):
        skip_certificate_verification (Union[Unset, bool]):
        public_certificate_file (Union[Unset, str]):
        private_key_file (Union[Unset, str]):
        query_timeout (Union[Unset, int]):
        max_page_size (Union[Unset, int]):
        login_field_name (Union[Unset, str]):
        login_button_color (Union[Unset, str]):
        login_button_border_color (Union[Unset, str]):
        login_button_text_color (Union[Unset, str]):
    """

    enable: Union[Unset, bool] = UNSET
    enable_sync: Union[Unset, bool] = UNSET
    ldap_server: Union[Unset, str] = UNSET
    ldap_port: Union[Unset, int] = UNSET
    connection_security: Union[Unset, str] = UNSET
    base_dn: Union[Unset, str] = UNSET
    bind_username: Union[Unset, str] = UNSET
    bind_password: Union[Unset, str] = UNSET
    maximum_login_attempts: Union[Unset, int] = UNSET
    user_filter: Union[Unset, str] = UNSET
    group_filter: Union[Unset, str] = UNSET
    guest_filter: Union[Unset, str] = UNSET
    enable_admin_filter: Union[Unset, bool] = UNSET
    admin_filter: Union[Unset, str] = UNSET
    group_display_name_attribute: Union[Unset, str] = UNSET
    group_id_attribute: Union[Unset, str] = UNSET
    first_name_attribute: Union[Unset, str] = UNSET
    last_name_attribute: Union[Unset, str] = UNSET
    email_attribute: Union[Unset, str] = UNSET
    username_attribute: Union[Unset, str] = UNSET
    nickname_attribute: Union[Unset, str] = UNSET
    id_attribute: Union[Unset, str] = UNSET
    position_attribute: Union[Unset, str] = UNSET
    login_id_attribute: Union[Unset, str] = UNSET
    picture_attribute: Union[Unset, str] = UNSET
    sync_interval_minutes: Union[Unset, int] = UNSET
    skip_certificate_verification: Union[Unset, bool] = UNSET
    public_certificate_file: Union[Unset, str] = UNSET
    private_key_file: Union[Unset, str] = UNSET
    query_timeout: Union[Unset, int] = UNSET
    max_page_size: Union[Unset, int] = UNSET
    login_field_name: Union[Unset, str] = UNSET
    login_button_color: Union[Unset, str] = UNSET
    login_button_border_color: Union[Unset, str] = UNSET
    login_button_text_color: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enable = self.enable

        enable_sync = self.enable_sync

        ldap_server = self.ldap_server

        ldap_port = self.ldap_port

        connection_security = self.connection_security

        base_dn = self.base_dn

        bind_username = self.bind_username

        bind_password = self.bind_password

        maximum_login_attempts = self.maximum_login_attempts

        user_filter = self.user_filter

        group_filter = self.group_filter

        guest_filter = self.guest_filter

        enable_admin_filter = self.enable_admin_filter

        admin_filter = self.admin_filter

        group_display_name_attribute = self.group_display_name_attribute

        group_id_attribute = self.group_id_attribute

        first_name_attribute = self.first_name_attribute

        last_name_attribute = self.last_name_attribute

        email_attribute = self.email_attribute

        username_attribute = self.username_attribute

        nickname_attribute = self.nickname_attribute

        id_attribute = self.id_attribute

        position_attribute = self.position_attribute

        login_id_attribute = self.login_id_attribute

        picture_attribute = self.picture_attribute

        sync_interval_minutes = self.sync_interval_minutes

        skip_certificate_verification = self.skip_certificate_verification

        public_certificate_file = self.public_certificate_file

        private_key_file = self.private_key_file

        query_timeout = self.query_timeout

        max_page_size = self.max_page_size

        login_field_name = self.login_field_name

        login_button_color = self.login_button_color

        login_button_border_color = self.login_button_border_color

        login_button_text_color = self.login_button_text_color

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enable is not UNSET:
            field_dict["Enable"] = enable
        if enable_sync is not UNSET:
            field_dict["EnableSync"] = enable_sync
        if ldap_server is not UNSET:
            field_dict["LdapServer"] = ldap_server
        if ldap_port is not UNSET:
            field_dict["LdapPort"] = ldap_port
        if connection_security is not UNSET:
            field_dict["ConnectionSecurity"] = connection_security
        if base_dn is not UNSET:
            field_dict["BaseDN"] = base_dn
        if bind_username is not UNSET:
            field_dict["BindUsername"] = bind_username
        if bind_password is not UNSET:
            field_dict["BindPassword"] = bind_password
        if maximum_login_attempts is not UNSET:
            field_dict["MaximumLoginAttempts"] = maximum_login_attempts
        if user_filter is not UNSET:
            field_dict["UserFilter"] = user_filter
        if group_filter is not UNSET:
            field_dict["GroupFilter"] = group_filter
        if guest_filter is not UNSET:
            field_dict["GuestFilter"] = guest_filter
        if enable_admin_filter is not UNSET:
            field_dict["EnableAdminFilter"] = enable_admin_filter
        if admin_filter is not UNSET:
            field_dict["AdminFilter"] = admin_filter
        if group_display_name_attribute is not UNSET:
            field_dict["GroupDisplayNameAttribute"] = group_display_name_attribute
        if group_id_attribute is not UNSET:
            field_dict["GroupIdAttribute"] = group_id_attribute
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
        if id_attribute is not UNSET:
            field_dict["IdAttribute"] = id_attribute
        if position_attribute is not UNSET:
            field_dict["PositionAttribute"] = position_attribute
        if login_id_attribute is not UNSET:
            field_dict["LoginIdAttribute"] = login_id_attribute
        if picture_attribute is not UNSET:
            field_dict["PictureAttribute"] = picture_attribute
        if sync_interval_minutes is not UNSET:
            field_dict["SyncIntervalMinutes"] = sync_interval_minutes
        if skip_certificate_verification is not UNSET:
            field_dict["SkipCertificateVerification"] = skip_certificate_verification
        if public_certificate_file is not UNSET:
            field_dict["PublicCertificateFile"] = public_certificate_file
        if private_key_file is not UNSET:
            field_dict["PrivateKeyFile"] = private_key_file
        if query_timeout is not UNSET:
            field_dict["QueryTimeout"] = query_timeout
        if max_page_size is not UNSET:
            field_dict["MaxPageSize"] = max_page_size
        if login_field_name is not UNSET:
            field_dict["LoginFieldName"] = login_field_name
        if login_button_color is not UNSET:
            field_dict["LoginButtonColor"] = login_button_color
        if login_button_border_color is not UNSET:
            field_dict["LoginButtonBorderColor"] = login_button_border_color
        if login_button_text_color is not UNSET:
            field_dict["LoginButtonTextColor"] = login_button_text_color

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        enable = d.pop("Enable", UNSET)

        enable_sync = d.pop("EnableSync", UNSET)

        ldap_server = d.pop("LdapServer", UNSET)

        ldap_port = d.pop("LdapPort", UNSET)

        connection_security = d.pop("ConnectionSecurity", UNSET)

        base_dn = d.pop("BaseDN", UNSET)

        bind_username = d.pop("BindUsername", UNSET)

        bind_password = d.pop("BindPassword", UNSET)

        maximum_login_attempts = d.pop("MaximumLoginAttempts", UNSET)

        user_filter = d.pop("UserFilter", UNSET)

        group_filter = d.pop("GroupFilter", UNSET)

        guest_filter = d.pop("GuestFilter", UNSET)

        enable_admin_filter = d.pop("EnableAdminFilter", UNSET)

        admin_filter = d.pop("AdminFilter", UNSET)

        group_display_name_attribute = d.pop("GroupDisplayNameAttribute", UNSET)

        group_id_attribute = d.pop("GroupIdAttribute", UNSET)

        first_name_attribute = d.pop("FirstNameAttribute", UNSET)

        last_name_attribute = d.pop("LastNameAttribute", UNSET)

        email_attribute = d.pop("EmailAttribute", UNSET)

        username_attribute = d.pop("UsernameAttribute", UNSET)

        nickname_attribute = d.pop("NicknameAttribute", UNSET)

        id_attribute = d.pop("IdAttribute", UNSET)

        position_attribute = d.pop("PositionAttribute", UNSET)

        login_id_attribute = d.pop("LoginIdAttribute", UNSET)

        picture_attribute = d.pop("PictureAttribute", UNSET)

        sync_interval_minutes = d.pop("SyncIntervalMinutes", UNSET)

        skip_certificate_verification = d.pop("SkipCertificateVerification", UNSET)

        public_certificate_file = d.pop("PublicCertificateFile", UNSET)

        private_key_file = d.pop("PrivateKeyFile", UNSET)

        query_timeout = d.pop("QueryTimeout", UNSET)

        max_page_size = d.pop("MaxPageSize", UNSET)

        login_field_name = d.pop("LoginFieldName", UNSET)

        login_button_color = d.pop("LoginButtonColor", UNSET)

        login_button_border_color = d.pop("LoginButtonBorderColor", UNSET)

        login_button_text_color = d.pop("LoginButtonTextColor", UNSET)

        ldap_settings = cls(
            enable=enable,
            enable_sync=enable_sync,
            ldap_server=ldap_server,
            ldap_port=ldap_port,
            connection_security=connection_security,
            base_dn=base_dn,
            bind_username=bind_username,
            bind_password=bind_password,
            maximum_login_attempts=maximum_login_attempts,
            user_filter=user_filter,
            group_filter=group_filter,
            guest_filter=guest_filter,
            enable_admin_filter=enable_admin_filter,
            admin_filter=admin_filter,
            group_display_name_attribute=group_display_name_attribute,
            group_id_attribute=group_id_attribute,
            first_name_attribute=first_name_attribute,
            last_name_attribute=last_name_attribute,
            email_attribute=email_attribute,
            username_attribute=username_attribute,
            nickname_attribute=nickname_attribute,
            id_attribute=id_attribute,
            position_attribute=position_attribute,
            login_id_attribute=login_id_attribute,
            picture_attribute=picture_attribute,
            sync_interval_minutes=sync_interval_minutes,
            skip_certificate_verification=skip_certificate_verification,
            public_certificate_file=public_certificate_file,
            private_key_file=private_key_file,
            query_timeout=query_timeout,
            max_page_size=max_page_size,
            login_field_name=login_field_name,
            login_button_color=login_button_color,
            login_button_border_color=login_button_border_color,
            login_button_text_color=login_button_text_color,
        )

        ldap_settings.additional_properties = d
        return ldap_settings

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
