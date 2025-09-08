from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ConfigEmailSettings")


@_attrs_define
class ConfigEmailSettings:
    """
    Attributes:
        enable_sign_up_with_email (Union[Unset, bool]):
        enable_sign_in_with_email (Union[Unset, bool]):
        enable_sign_in_with_username (Union[Unset, bool]):
        send_email_notifications (Union[Unset, bool]):
        require_email_verification (Union[Unset, bool]):
        feedback_name (Union[Unset, str]):
        feedback_email (Union[Unset, str]):
        feedback_organization (Union[Unset, str]):
        smtp_username (Union[Unset, str]):
        smtp_password (Union[Unset, str]):
        smtp_server (Union[Unset, str]):
        smtp_port (Union[Unset, str]):
        connection_security (Union[Unset, str]):
        invite_salt (Union[Unset, str]):
        password_reset_salt (Union[Unset, str]):
        send_push_notifications (Union[Unset, bool]):
        push_notification_server (Union[Unset, str]):
        push_notification_contents (Union[Unset, str]):
        enable_email_batching (Union[Unset, bool]):
        email_batching_buffer_size (Union[Unset, int]):
        email_batching_interval (Union[Unset, int]):
    """

    enable_sign_up_with_email: Union[Unset, bool] = UNSET
    enable_sign_in_with_email: Union[Unset, bool] = UNSET
    enable_sign_in_with_username: Union[Unset, bool] = UNSET
    send_email_notifications: Union[Unset, bool] = UNSET
    require_email_verification: Union[Unset, bool] = UNSET
    feedback_name: Union[Unset, str] = UNSET
    feedback_email: Union[Unset, str] = UNSET
    feedback_organization: Union[Unset, str] = UNSET
    smtp_username: Union[Unset, str] = UNSET
    smtp_password: Union[Unset, str] = UNSET
    smtp_server: Union[Unset, str] = UNSET
    smtp_port: Union[Unset, str] = UNSET
    connection_security: Union[Unset, str] = UNSET
    invite_salt: Union[Unset, str] = UNSET
    password_reset_salt: Union[Unset, str] = UNSET
    send_push_notifications: Union[Unset, bool] = UNSET
    push_notification_server: Union[Unset, str] = UNSET
    push_notification_contents: Union[Unset, str] = UNSET
    enable_email_batching: Union[Unset, bool] = UNSET
    email_batching_buffer_size: Union[Unset, int] = UNSET
    email_batching_interval: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enable_sign_up_with_email = self.enable_sign_up_with_email

        enable_sign_in_with_email = self.enable_sign_in_with_email

        enable_sign_in_with_username = self.enable_sign_in_with_username

        send_email_notifications = self.send_email_notifications

        require_email_verification = self.require_email_verification

        feedback_name = self.feedback_name

        feedback_email = self.feedback_email

        feedback_organization = self.feedback_organization

        smtp_username = self.smtp_username

        smtp_password = self.smtp_password

        smtp_server = self.smtp_server

        smtp_port = self.smtp_port

        connection_security = self.connection_security

        invite_salt = self.invite_salt

        password_reset_salt = self.password_reset_salt

        send_push_notifications = self.send_push_notifications

        push_notification_server = self.push_notification_server

        push_notification_contents = self.push_notification_contents

        enable_email_batching = self.enable_email_batching

        email_batching_buffer_size = self.email_batching_buffer_size

        email_batching_interval = self.email_batching_interval

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enable_sign_up_with_email is not UNSET:
            field_dict["EnableSignUpWithEmail"] = enable_sign_up_with_email
        if enable_sign_in_with_email is not UNSET:
            field_dict["EnableSignInWithEmail"] = enable_sign_in_with_email
        if enable_sign_in_with_username is not UNSET:
            field_dict["EnableSignInWithUsername"] = enable_sign_in_with_username
        if send_email_notifications is not UNSET:
            field_dict["SendEmailNotifications"] = send_email_notifications
        if require_email_verification is not UNSET:
            field_dict["RequireEmailVerification"] = require_email_verification
        if feedback_name is not UNSET:
            field_dict["FeedbackName"] = feedback_name
        if feedback_email is not UNSET:
            field_dict["FeedbackEmail"] = feedback_email
        if feedback_organization is not UNSET:
            field_dict["FeedbackOrganization"] = feedback_organization
        if smtp_username is not UNSET:
            field_dict["SMTPUsername"] = smtp_username
        if smtp_password is not UNSET:
            field_dict["SMTPPassword"] = smtp_password
        if smtp_server is not UNSET:
            field_dict["SMTPServer"] = smtp_server
        if smtp_port is not UNSET:
            field_dict["SMTPPort"] = smtp_port
        if connection_security is not UNSET:
            field_dict["ConnectionSecurity"] = connection_security
        if invite_salt is not UNSET:
            field_dict["InviteSalt"] = invite_salt
        if password_reset_salt is not UNSET:
            field_dict["PasswordResetSalt"] = password_reset_salt
        if send_push_notifications is not UNSET:
            field_dict["SendPushNotifications"] = send_push_notifications
        if push_notification_server is not UNSET:
            field_dict["PushNotificationServer"] = push_notification_server
        if push_notification_contents is not UNSET:
            field_dict["PushNotificationContents"] = push_notification_contents
        if enable_email_batching is not UNSET:
            field_dict["EnableEmailBatching"] = enable_email_batching
        if email_batching_buffer_size is not UNSET:
            field_dict["EmailBatchingBufferSize"] = email_batching_buffer_size
        if email_batching_interval is not UNSET:
            field_dict["EmailBatchingInterval"] = email_batching_interval

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        enable_sign_up_with_email = d.pop("EnableSignUpWithEmail", UNSET)

        enable_sign_in_with_email = d.pop("EnableSignInWithEmail", UNSET)

        enable_sign_in_with_username = d.pop("EnableSignInWithUsername", UNSET)

        send_email_notifications = d.pop("SendEmailNotifications", UNSET)

        require_email_verification = d.pop("RequireEmailVerification", UNSET)

        feedback_name = d.pop("FeedbackName", UNSET)

        feedback_email = d.pop("FeedbackEmail", UNSET)

        feedback_organization = d.pop("FeedbackOrganization", UNSET)

        smtp_username = d.pop("SMTPUsername", UNSET)

        smtp_password = d.pop("SMTPPassword", UNSET)

        smtp_server = d.pop("SMTPServer", UNSET)

        smtp_port = d.pop("SMTPPort", UNSET)

        connection_security = d.pop("ConnectionSecurity", UNSET)

        invite_salt = d.pop("InviteSalt", UNSET)

        password_reset_salt = d.pop("PasswordResetSalt", UNSET)

        send_push_notifications = d.pop("SendPushNotifications", UNSET)

        push_notification_server = d.pop("PushNotificationServer", UNSET)

        push_notification_contents = d.pop("PushNotificationContents", UNSET)

        enable_email_batching = d.pop("EnableEmailBatching", UNSET)

        email_batching_buffer_size = d.pop("EmailBatchingBufferSize", UNSET)

        email_batching_interval = d.pop("EmailBatchingInterval", UNSET)

        config_email_settings = cls(
            enable_sign_up_with_email=enable_sign_up_with_email,
            enable_sign_in_with_email=enable_sign_in_with_email,
            enable_sign_in_with_username=enable_sign_in_with_username,
            send_email_notifications=send_email_notifications,
            require_email_verification=require_email_verification,
            feedback_name=feedback_name,
            feedback_email=feedback_email,
            feedback_organization=feedback_organization,
            smtp_username=smtp_username,
            smtp_password=smtp_password,
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            connection_security=connection_security,
            invite_salt=invite_salt,
            password_reset_salt=password_reset_salt,
            send_push_notifications=send_push_notifications,
            push_notification_server=push_notification_server,
            push_notification_contents=push_notification_contents,
            enable_email_batching=enable_email_batching,
            email_batching_buffer_size=email_batching_buffer_size,
            email_batching_interval=email_batching_interval,
        )

        config_email_settings.additional_properties = d
        return config_email_settings

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
