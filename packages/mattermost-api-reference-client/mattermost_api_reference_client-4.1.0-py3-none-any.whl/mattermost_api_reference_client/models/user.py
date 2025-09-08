from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.timezone import Timezone
    from ..models.user_notify_props import UserNotifyProps
    from ..models.user_props import UserProps


T = TypeVar("T", bound="User")


@_attrs_define
class User:
    """
    Attributes:
        id (Union[Unset, str]):
        create_at (Union[Unset, int]): The time in milliseconds a user was created
        update_at (Union[Unset, int]): The time in milliseconds a user was last updated
        delete_at (Union[Unset, int]): The time in milliseconds a user was deleted
        username (Union[Unset, str]):
        first_name (Union[Unset, str]):
        last_name (Union[Unset, str]):
        nickname (Union[Unset, str]):
        email (Union[Unset, str]):
        email_verified (Union[Unset, bool]):
        auth_service (Union[Unset, str]):
        roles (Union[Unset, str]):
        locale (Union[Unset, str]):
        notify_props (Union[Unset, UserNotifyProps]):
        props (Union[Unset, UserProps]):
        last_password_update (Union[Unset, int]):
        last_picture_update (Union[Unset, int]):
        failed_attempts (Union[Unset, int]):
        mfa_active (Union[Unset, bool]):
        timezone (Union[Unset, Timezone]):
        terms_of_service_id (Union[Unset, str]): ID of accepted terms of service, if any. This field is not present if
            empty.
        terms_of_service_create_at (Union[Unset, int]): The time in milliseconds the user accepted the terms of service
    """

    id: Union[Unset, str] = UNSET
    create_at: Union[Unset, int] = UNSET
    update_at: Union[Unset, int] = UNSET
    delete_at: Union[Unset, int] = UNSET
    username: Union[Unset, str] = UNSET
    first_name: Union[Unset, str] = UNSET
    last_name: Union[Unset, str] = UNSET
    nickname: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    email_verified: Union[Unset, bool] = UNSET
    auth_service: Union[Unset, str] = UNSET
    roles: Union[Unset, str] = UNSET
    locale: Union[Unset, str] = UNSET
    notify_props: Union[Unset, "UserNotifyProps"] = UNSET
    props: Union[Unset, "UserProps"] = UNSET
    last_password_update: Union[Unset, int] = UNSET
    last_picture_update: Union[Unset, int] = UNSET
    failed_attempts: Union[Unset, int] = UNSET
    mfa_active: Union[Unset, bool] = UNSET
    timezone: Union[Unset, "Timezone"] = UNSET
    terms_of_service_id: Union[Unset, str] = UNSET
    terms_of_service_create_at: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        create_at = self.create_at

        update_at = self.update_at

        delete_at = self.delete_at

        username = self.username

        first_name = self.first_name

        last_name = self.last_name

        nickname = self.nickname

        email = self.email

        email_verified = self.email_verified

        auth_service = self.auth_service

        roles = self.roles

        locale = self.locale

        notify_props: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.notify_props, Unset):
            notify_props = self.notify_props.to_dict()

        props: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.props, Unset):
            props = self.props.to_dict()

        last_password_update = self.last_password_update

        last_picture_update = self.last_picture_update

        failed_attempts = self.failed_attempts

        mfa_active = self.mfa_active

        timezone: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.timezone, Unset):
            timezone = self.timezone.to_dict()

        terms_of_service_id = self.terms_of_service_id

        terms_of_service_create_at = self.terms_of_service_create_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if create_at is not UNSET:
            field_dict["create_at"] = create_at
        if update_at is not UNSET:
            field_dict["update_at"] = update_at
        if delete_at is not UNSET:
            field_dict["delete_at"] = delete_at
        if username is not UNSET:
            field_dict["username"] = username
        if first_name is not UNSET:
            field_dict["first_name"] = first_name
        if last_name is not UNSET:
            field_dict["last_name"] = last_name
        if nickname is not UNSET:
            field_dict["nickname"] = nickname
        if email is not UNSET:
            field_dict["email"] = email
        if email_verified is not UNSET:
            field_dict["email_verified"] = email_verified
        if auth_service is not UNSET:
            field_dict["auth_service"] = auth_service
        if roles is not UNSET:
            field_dict["roles"] = roles
        if locale is not UNSET:
            field_dict["locale"] = locale
        if notify_props is not UNSET:
            field_dict["notify_props"] = notify_props
        if props is not UNSET:
            field_dict["props"] = props
        if last_password_update is not UNSET:
            field_dict["last_password_update"] = last_password_update
        if last_picture_update is not UNSET:
            field_dict["last_picture_update"] = last_picture_update
        if failed_attempts is not UNSET:
            field_dict["failed_attempts"] = failed_attempts
        if mfa_active is not UNSET:
            field_dict["mfa_active"] = mfa_active
        if timezone is not UNSET:
            field_dict["timezone"] = timezone
        if terms_of_service_id is not UNSET:
            field_dict["terms_of_service_id"] = terms_of_service_id
        if terms_of_service_create_at is not UNSET:
            field_dict["terms_of_service_create_at"] = terms_of_service_create_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.timezone import Timezone
        from ..models.user_notify_props import UserNotifyProps
        from ..models.user_props import UserProps

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        create_at = d.pop("create_at", UNSET)

        update_at = d.pop("update_at", UNSET)

        delete_at = d.pop("delete_at", UNSET)

        username = d.pop("username", UNSET)

        first_name = d.pop("first_name", UNSET)

        last_name = d.pop("last_name", UNSET)

        nickname = d.pop("nickname", UNSET)

        email = d.pop("email", UNSET)

        email_verified = d.pop("email_verified", UNSET)

        auth_service = d.pop("auth_service", UNSET)

        roles = d.pop("roles", UNSET)

        locale = d.pop("locale", UNSET)

        _notify_props = d.pop("notify_props", UNSET)
        notify_props: Union[Unset, UserNotifyProps]
        if isinstance(_notify_props, Unset):
            notify_props = UNSET
        else:
            notify_props = UserNotifyProps.from_dict(_notify_props)

        _props = d.pop("props", UNSET)
        props: Union[Unset, UserProps]
        if isinstance(_props, Unset):
            props = UNSET
        else:
            props = UserProps.from_dict(_props)

        last_password_update = d.pop("last_password_update", UNSET)

        last_picture_update = d.pop("last_picture_update", UNSET)

        failed_attempts = d.pop("failed_attempts", UNSET)

        mfa_active = d.pop("mfa_active", UNSET)

        _timezone = d.pop("timezone", UNSET)
        timezone: Union[Unset, Timezone]
        if isinstance(_timezone, Unset):
            timezone = UNSET
        else:
            timezone = Timezone.from_dict(_timezone)

        terms_of_service_id = d.pop("terms_of_service_id", UNSET)

        terms_of_service_create_at = d.pop("terms_of_service_create_at", UNSET)

        user = cls(
            id=id,
            create_at=create_at,
            update_at=update_at,
            delete_at=delete_at,
            username=username,
            first_name=first_name,
            last_name=last_name,
            nickname=nickname,
            email=email,
            email_verified=email_verified,
            auth_service=auth_service,
            roles=roles,
            locale=locale,
            notify_props=notify_props,
            props=props,
            last_password_update=last_password_update,
            last_picture_update=last_picture_update,
            failed_attempts=failed_attempts,
            mfa_active=mfa_active,
            timezone=timezone,
            terms_of_service_id=terms_of_service_id,
            terms_of_service_create_at=terms_of_service_create_at,
        )

        user.additional_properties = d
        return user

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
