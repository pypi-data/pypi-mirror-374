from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.timezone import Timezone


T = TypeVar("T", bound="UserReport")


@_attrs_define
class UserReport:
    """
    Attributes:
        id (Union[Unset, str]):
        create_at (Union[Unset, int]): The time in milliseconds a user was created
        update_at (Union[Unset, int]): The time in milliseconds a user was last updated
        delete_at (Union[Unset, int]): The time in milliseconds a user was deleted
        username (Union[Unset, str]):
        auth_data (Union[Unset, str]):
        auth_service (Union[Unset, str]):
        email (Union[Unset, str]):
        nickname (Union[Unset, str]):
        first_name (Union[Unset, str]):
        last_name (Union[Unset, str]):
        position (Union[Unset, str]):
        roles (Union[Unset, str]):
        locale (Union[Unset, str]):
        timezone (Union[Unset, Timezone]):
        disable_welcome_email (Union[Unset, bool]):
        last_login (Union[Unset, int]): Last time the user was logged in
        last_status_at (Union[Unset, int]): Last time the user's status was updated
        last_post_date (Union[Unset, int]): Last time the user made a post within the given date range
        days_active (Union[Unset, int]): Total number of days a user posted within the given date range
        total_posts (Union[Unset, int]): Total number of posts made by a user within the given date range
    """

    id: Union[Unset, str] = UNSET
    create_at: Union[Unset, int] = UNSET
    update_at: Union[Unset, int] = UNSET
    delete_at: Union[Unset, int] = UNSET
    username: Union[Unset, str] = UNSET
    auth_data: Union[Unset, str] = UNSET
    auth_service: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    nickname: Union[Unset, str] = UNSET
    first_name: Union[Unset, str] = UNSET
    last_name: Union[Unset, str] = UNSET
    position: Union[Unset, str] = UNSET
    roles: Union[Unset, str] = UNSET
    locale: Union[Unset, str] = UNSET
    timezone: Union[Unset, "Timezone"] = UNSET
    disable_welcome_email: Union[Unset, bool] = UNSET
    last_login: Union[Unset, int] = UNSET
    last_status_at: Union[Unset, int] = UNSET
    last_post_date: Union[Unset, int] = UNSET
    days_active: Union[Unset, int] = UNSET
    total_posts: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        create_at = self.create_at

        update_at = self.update_at

        delete_at = self.delete_at

        username = self.username

        auth_data = self.auth_data

        auth_service = self.auth_service

        email = self.email

        nickname = self.nickname

        first_name = self.first_name

        last_name = self.last_name

        position = self.position

        roles = self.roles

        locale = self.locale

        timezone: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.timezone, Unset):
            timezone = self.timezone.to_dict()

        disable_welcome_email = self.disable_welcome_email

        last_login = self.last_login

        last_status_at = self.last_status_at

        last_post_date = self.last_post_date

        days_active = self.days_active

        total_posts = self.total_posts

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
        if auth_data is not UNSET:
            field_dict["auth_data"] = auth_data
        if auth_service is not UNSET:
            field_dict["auth_service"] = auth_service
        if email is not UNSET:
            field_dict["email"] = email
        if nickname is not UNSET:
            field_dict["nickname"] = nickname
        if first_name is not UNSET:
            field_dict["first_name"] = first_name
        if last_name is not UNSET:
            field_dict["last_name"] = last_name
        if position is not UNSET:
            field_dict["position"] = position
        if roles is not UNSET:
            field_dict["roles"] = roles
        if locale is not UNSET:
            field_dict["locale"] = locale
        if timezone is not UNSET:
            field_dict["timezone"] = timezone
        if disable_welcome_email is not UNSET:
            field_dict["disable_welcome_email"] = disable_welcome_email
        if last_login is not UNSET:
            field_dict["last_login"] = last_login
        if last_status_at is not UNSET:
            field_dict["last_status_at"] = last_status_at
        if last_post_date is not UNSET:
            field_dict["last_post_date"] = last_post_date
        if days_active is not UNSET:
            field_dict["days_active"] = days_active
        if total_posts is not UNSET:
            field_dict["total_posts"] = total_posts

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.timezone import Timezone

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        create_at = d.pop("create_at", UNSET)

        update_at = d.pop("update_at", UNSET)

        delete_at = d.pop("delete_at", UNSET)

        username = d.pop("username", UNSET)

        auth_data = d.pop("auth_data", UNSET)

        auth_service = d.pop("auth_service", UNSET)

        email = d.pop("email", UNSET)

        nickname = d.pop("nickname", UNSET)

        first_name = d.pop("first_name", UNSET)

        last_name = d.pop("last_name", UNSET)

        position = d.pop("position", UNSET)

        roles = d.pop("roles", UNSET)

        locale = d.pop("locale", UNSET)

        _timezone = d.pop("timezone", UNSET)
        timezone: Union[Unset, Timezone]
        if isinstance(_timezone, Unset):
            timezone = UNSET
        else:
            timezone = Timezone.from_dict(_timezone)

        disable_welcome_email = d.pop("disable_welcome_email", UNSET)

        last_login = d.pop("last_login", UNSET)

        last_status_at = d.pop("last_status_at", UNSET)

        last_post_date = d.pop("last_post_date", UNSET)

        days_active = d.pop("days_active", UNSET)

        total_posts = d.pop("total_posts", UNSET)

        user_report = cls(
            id=id,
            create_at=create_at,
            update_at=update_at,
            delete_at=delete_at,
            username=username,
            auth_data=auth_data,
            auth_service=auth_service,
            email=email,
            nickname=nickname,
            first_name=first_name,
            last_name=last_name,
            position=position,
            roles=roles,
            locale=locale,
            timezone=timezone,
            disable_welcome_email=disable_welcome_email,
            last_login=last_login,
            last_status_at=last_status_at,
            last_post_date=last_post_date,
            days_active=days_active,
            total_posts=total_posts,
        )

        user_report.additional_properties = d
        return user_report

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
