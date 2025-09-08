from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EnvironmentConfigServiceSettings")


@_attrs_define
class EnvironmentConfigServiceSettings:
    """
    Attributes:
        site_url (Union[Unset, bool]):
        listen_address (Union[Unset, bool]):
        connection_security (Union[Unset, bool]):
        tls_cert_file (Union[Unset, bool]):
        tls_key_file (Union[Unset, bool]):
        use_lets_encrypt (Union[Unset, bool]):
        lets_encrypt_certificate_cache_file (Union[Unset, bool]):
        forward_80_to_443 (Union[Unset, bool]):
        read_timeout (Union[Unset, bool]):
        write_timeout (Union[Unset, bool]):
        maximum_login_attempts (Union[Unset, bool]):
        segment_developer_key (Union[Unset, bool]):
        google_developer_key (Union[Unset, bool]):
        enable_o_auth_service_provider (Union[Unset, bool]):
        enable_incoming_webhooks (Union[Unset, bool]):
        enable_outgoing_webhooks (Union[Unset, bool]):
        enable_commands (Union[Unset, bool]):
        enable_only_admin_integrations (Union[Unset, bool]):
        enable_post_username_override (Union[Unset, bool]):
        enable_post_icon_override (Union[Unset, bool]):
        enable_testing (Union[Unset, bool]):
        enable_developer (Union[Unset, bool]):
        enable_security_fix_alert (Union[Unset, bool]):
        enable_insecure_outgoing_connections (Union[Unset, bool]):
        enable_multifactor_authentication (Union[Unset, bool]):
        enforce_multifactor_authentication (Union[Unset, bool]):
        allow_cors_from (Union[Unset, bool]):
        session_length_web_in_days (Union[Unset, bool]):
        session_length_mobile_in_days (Union[Unset, bool]):
        session_length_sso_in_days (Union[Unset, bool]):
        session_cache_in_minutes (Union[Unset, bool]):
        websocket_secure_port (Union[Unset, bool]):
        websocket_port (Union[Unset, bool]):
        webserver_mode (Union[Unset, bool]):
        enable_custom_emoji (Union[Unset, bool]):
        restrict_custom_emoji_creation (Union[Unset, bool]):
    """

    site_url: Union[Unset, bool] = UNSET
    listen_address: Union[Unset, bool] = UNSET
    connection_security: Union[Unset, bool] = UNSET
    tls_cert_file: Union[Unset, bool] = UNSET
    tls_key_file: Union[Unset, bool] = UNSET
    use_lets_encrypt: Union[Unset, bool] = UNSET
    lets_encrypt_certificate_cache_file: Union[Unset, bool] = UNSET
    forward_80_to_443: Union[Unset, bool] = UNSET
    read_timeout: Union[Unset, bool] = UNSET
    write_timeout: Union[Unset, bool] = UNSET
    maximum_login_attempts: Union[Unset, bool] = UNSET
    segment_developer_key: Union[Unset, bool] = UNSET
    google_developer_key: Union[Unset, bool] = UNSET
    enable_o_auth_service_provider: Union[Unset, bool] = UNSET
    enable_incoming_webhooks: Union[Unset, bool] = UNSET
    enable_outgoing_webhooks: Union[Unset, bool] = UNSET
    enable_commands: Union[Unset, bool] = UNSET
    enable_only_admin_integrations: Union[Unset, bool] = UNSET
    enable_post_username_override: Union[Unset, bool] = UNSET
    enable_post_icon_override: Union[Unset, bool] = UNSET
    enable_testing: Union[Unset, bool] = UNSET
    enable_developer: Union[Unset, bool] = UNSET
    enable_security_fix_alert: Union[Unset, bool] = UNSET
    enable_insecure_outgoing_connections: Union[Unset, bool] = UNSET
    enable_multifactor_authentication: Union[Unset, bool] = UNSET
    enforce_multifactor_authentication: Union[Unset, bool] = UNSET
    allow_cors_from: Union[Unset, bool] = UNSET
    session_length_web_in_days: Union[Unset, bool] = UNSET
    session_length_mobile_in_days: Union[Unset, bool] = UNSET
    session_length_sso_in_days: Union[Unset, bool] = UNSET
    session_cache_in_minutes: Union[Unset, bool] = UNSET
    websocket_secure_port: Union[Unset, bool] = UNSET
    websocket_port: Union[Unset, bool] = UNSET
    webserver_mode: Union[Unset, bool] = UNSET
    enable_custom_emoji: Union[Unset, bool] = UNSET
    restrict_custom_emoji_creation: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        site_url = self.site_url

        listen_address = self.listen_address

        connection_security = self.connection_security

        tls_cert_file = self.tls_cert_file

        tls_key_file = self.tls_key_file

        use_lets_encrypt = self.use_lets_encrypt

        lets_encrypt_certificate_cache_file = self.lets_encrypt_certificate_cache_file

        forward_80_to_443 = self.forward_80_to_443

        read_timeout = self.read_timeout

        write_timeout = self.write_timeout

        maximum_login_attempts = self.maximum_login_attempts

        segment_developer_key = self.segment_developer_key

        google_developer_key = self.google_developer_key

        enable_o_auth_service_provider = self.enable_o_auth_service_provider

        enable_incoming_webhooks = self.enable_incoming_webhooks

        enable_outgoing_webhooks = self.enable_outgoing_webhooks

        enable_commands = self.enable_commands

        enable_only_admin_integrations = self.enable_only_admin_integrations

        enable_post_username_override = self.enable_post_username_override

        enable_post_icon_override = self.enable_post_icon_override

        enable_testing = self.enable_testing

        enable_developer = self.enable_developer

        enable_security_fix_alert = self.enable_security_fix_alert

        enable_insecure_outgoing_connections = self.enable_insecure_outgoing_connections

        enable_multifactor_authentication = self.enable_multifactor_authentication

        enforce_multifactor_authentication = self.enforce_multifactor_authentication

        allow_cors_from = self.allow_cors_from

        session_length_web_in_days = self.session_length_web_in_days

        session_length_mobile_in_days = self.session_length_mobile_in_days

        session_length_sso_in_days = self.session_length_sso_in_days

        session_cache_in_minutes = self.session_cache_in_minutes

        websocket_secure_port = self.websocket_secure_port

        websocket_port = self.websocket_port

        webserver_mode = self.webserver_mode

        enable_custom_emoji = self.enable_custom_emoji

        restrict_custom_emoji_creation = self.restrict_custom_emoji_creation

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if site_url is not UNSET:
            field_dict["SiteURL"] = site_url
        if listen_address is not UNSET:
            field_dict["ListenAddress"] = listen_address
        if connection_security is not UNSET:
            field_dict["ConnectionSecurity"] = connection_security
        if tls_cert_file is not UNSET:
            field_dict["TLSCertFile"] = tls_cert_file
        if tls_key_file is not UNSET:
            field_dict["TLSKeyFile"] = tls_key_file
        if use_lets_encrypt is not UNSET:
            field_dict["UseLetsEncrypt"] = use_lets_encrypt
        if lets_encrypt_certificate_cache_file is not UNSET:
            field_dict["LetsEncryptCertificateCacheFile"] = lets_encrypt_certificate_cache_file
        if forward_80_to_443 is not UNSET:
            field_dict["Forward80To443"] = forward_80_to_443
        if read_timeout is not UNSET:
            field_dict["ReadTimeout"] = read_timeout
        if write_timeout is not UNSET:
            field_dict["WriteTimeout"] = write_timeout
        if maximum_login_attempts is not UNSET:
            field_dict["MaximumLoginAttempts"] = maximum_login_attempts
        if segment_developer_key is not UNSET:
            field_dict["SegmentDeveloperKey"] = segment_developer_key
        if google_developer_key is not UNSET:
            field_dict["GoogleDeveloperKey"] = google_developer_key
        if enable_o_auth_service_provider is not UNSET:
            field_dict["EnableOAuthServiceProvider"] = enable_o_auth_service_provider
        if enable_incoming_webhooks is not UNSET:
            field_dict["EnableIncomingWebhooks"] = enable_incoming_webhooks
        if enable_outgoing_webhooks is not UNSET:
            field_dict["EnableOutgoingWebhooks"] = enable_outgoing_webhooks
        if enable_commands is not UNSET:
            field_dict["EnableCommands"] = enable_commands
        if enable_only_admin_integrations is not UNSET:
            field_dict["EnableOnlyAdminIntegrations"] = enable_only_admin_integrations
        if enable_post_username_override is not UNSET:
            field_dict["EnablePostUsernameOverride"] = enable_post_username_override
        if enable_post_icon_override is not UNSET:
            field_dict["EnablePostIconOverride"] = enable_post_icon_override
        if enable_testing is not UNSET:
            field_dict["EnableTesting"] = enable_testing
        if enable_developer is not UNSET:
            field_dict["EnableDeveloper"] = enable_developer
        if enable_security_fix_alert is not UNSET:
            field_dict["EnableSecurityFixAlert"] = enable_security_fix_alert
        if enable_insecure_outgoing_connections is not UNSET:
            field_dict["EnableInsecureOutgoingConnections"] = enable_insecure_outgoing_connections
        if enable_multifactor_authentication is not UNSET:
            field_dict["EnableMultifactorAuthentication"] = enable_multifactor_authentication
        if enforce_multifactor_authentication is not UNSET:
            field_dict["EnforceMultifactorAuthentication"] = enforce_multifactor_authentication
        if allow_cors_from is not UNSET:
            field_dict["AllowCorsFrom"] = allow_cors_from
        if session_length_web_in_days is not UNSET:
            field_dict["SessionLengthWebInDays"] = session_length_web_in_days
        if session_length_mobile_in_days is not UNSET:
            field_dict["SessionLengthMobileInDays"] = session_length_mobile_in_days
        if session_length_sso_in_days is not UNSET:
            field_dict["SessionLengthSSOInDays"] = session_length_sso_in_days
        if session_cache_in_minutes is not UNSET:
            field_dict["SessionCacheInMinutes"] = session_cache_in_minutes
        if websocket_secure_port is not UNSET:
            field_dict["WebsocketSecurePort"] = websocket_secure_port
        if websocket_port is not UNSET:
            field_dict["WebsocketPort"] = websocket_port
        if webserver_mode is not UNSET:
            field_dict["WebserverMode"] = webserver_mode
        if enable_custom_emoji is not UNSET:
            field_dict["EnableCustomEmoji"] = enable_custom_emoji
        if restrict_custom_emoji_creation is not UNSET:
            field_dict["RestrictCustomEmojiCreation"] = restrict_custom_emoji_creation

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        site_url = d.pop("SiteURL", UNSET)

        listen_address = d.pop("ListenAddress", UNSET)

        connection_security = d.pop("ConnectionSecurity", UNSET)

        tls_cert_file = d.pop("TLSCertFile", UNSET)

        tls_key_file = d.pop("TLSKeyFile", UNSET)

        use_lets_encrypt = d.pop("UseLetsEncrypt", UNSET)

        lets_encrypt_certificate_cache_file = d.pop("LetsEncryptCertificateCacheFile", UNSET)

        forward_80_to_443 = d.pop("Forward80To443", UNSET)

        read_timeout = d.pop("ReadTimeout", UNSET)

        write_timeout = d.pop("WriteTimeout", UNSET)

        maximum_login_attempts = d.pop("MaximumLoginAttempts", UNSET)

        segment_developer_key = d.pop("SegmentDeveloperKey", UNSET)

        google_developer_key = d.pop("GoogleDeveloperKey", UNSET)

        enable_o_auth_service_provider = d.pop("EnableOAuthServiceProvider", UNSET)

        enable_incoming_webhooks = d.pop("EnableIncomingWebhooks", UNSET)

        enable_outgoing_webhooks = d.pop("EnableOutgoingWebhooks", UNSET)

        enable_commands = d.pop("EnableCommands", UNSET)

        enable_only_admin_integrations = d.pop("EnableOnlyAdminIntegrations", UNSET)

        enable_post_username_override = d.pop("EnablePostUsernameOverride", UNSET)

        enable_post_icon_override = d.pop("EnablePostIconOverride", UNSET)

        enable_testing = d.pop("EnableTesting", UNSET)

        enable_developer = d.pop("EnableDeveloper", UNSET)

        enable_security_fix_alert = d.pop("EnableSecurityFixAlert", UNSET)

        enable_insecure_outgoing_connections = d.pop("EnableInsecureOutgoingConnections", UNSET)

        enable_multifactor_authentication = d.pop("EnableMultifactorAuthentication", UNSET)

        enforce_multifactor_authentication = d.pop("EnforceMultifactorAuthentication", UNSET)

        allow_cors_from = d.pop("AllowCorsFrom", UNSET)

        session_length_web_in_days = d.pop("SessionLengthWebInDays", UNSET)

        session_length_mobile_in_days = d.pop("SessionLengthMobileInDays", UNSET)

        session_length_sso_in_days = d.pop("SessionLengthSSOInDays", UNSET)

        session_cache_in_minutes = d.pop("SessionCacheInMinutes", UNSET)

        websocket_secure_port = d.pop("WebsocketSecurePort", UNSET)

        websocket_port = d.pop("WebsocketPort", UNSET)

        webserver_mode = d.pop("WebserverMode", UNSET)

        enable_custom_emoji = d.pop("EnableCustomEmoji", UNSET)

        restrict_custom_emoji_creation = d.pop("RestrictCustomEmojiCreation", UNSET)

        environment_config_service_settings = cls(
            site_url=site_url,
            listen_address=listen_address,
            connection_security=connection_security,
            tls_cert_file=tls_cert_file,
            tls_key_file=tls_key_file,
            use_lets_encrypt=use_lets_encrypt,
            lets_encrypt_certificate_cache_file=lets_encrypt_certificate_cache_file,
            forward_80_to_443=forward_80_to_443,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            maximum_login_attempts=maximum_login_attempts,
            segment_developer_key=segment_developer_key,
            google_developer_key=google_developer_key,
            enable_o_auth_service_provider=enable_o_auth_service_provider,
            enable_incoming_webhooks=enable_incoming_webhooks,
            enable_outgoing_webhooks=enable_outgoing_webhooks,
            enable_commands=enable_commands,
            enable_only_admin_integrations=enable_only_admin_integrations,
            enable_post_username_override=enable_post_username_override,
            enable_post_icon_override=enable_post_icon_override,
            enable_testing=enable_testing,
            enable_developer=enable_developer,
            enable_security_fix_alert=enable_security_fix_alert,
            enable_insecure_outgoing_connections=enable_insecure_outgoing_connections,
            enable_multifactor_authentication=enable_multifactor_authentication,
            enforce_multifactor_authentication=enforce_multifactor_authentication,
            allow_cors_from=allow_cors_from,
            session_length_web_in_days=session_length_web_in_days,
            session_length_mobile_in_days=session_length_mobile_in_days,
            session_length_sso_in_days=session_length_sso_in_days,
            session_cache_in_minutes=session_cache_in_minutes,
            websocket_secure_port=websocket_secure_port,
            websocket_port=websocket_port,
            webserver_mode=webserver_mode,
            enable_custom_emoji=enable_custom_emoji,
            restrict_custom_emoji_creation=restrict_custom_emoji_creation,
        )

        environment_config_service_settings.additional_properties = d
        return environment_config_service_settings

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
