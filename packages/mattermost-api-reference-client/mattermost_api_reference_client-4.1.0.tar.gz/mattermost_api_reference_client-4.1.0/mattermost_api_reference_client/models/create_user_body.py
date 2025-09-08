from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_user_body_props import CreateUserBodyProps
    from ..models.timezone import Timezone
    from ..models.user_notify_props import UserNotifyProps


T = TypeVar("T", bound="CreateUserBody")


@_attrs_define
class CreateUserBody:
    """
    Attributes:
        email (str):
        username (str):
        first_name (Union[Unset, str]):
        last_name (Union[Unset, str]):
        nickname (Union[Unset, str]):
        position (Union[Unset, str]):
        timezone (Union[Unset, Timezone]):
        auth_data (Union[Unset, str]): Service-specific authentication data, such as email address.
        auth_service (Union[Unset, str]): The authentication service, one of "email", "gitlab", "ldap", "saml",
            "office365", "google", and "".
        password (Union[Unset, str]): The password used for email authentication.
        locale (Union[Unset, str]):
        props (Union[Unset, CreateUserBodyProps]):
        notify_props (Union[Unset, UserNotifyProps]):
    """

    email: str
    username: str
    first_name: Union[Unset, str] = UNSET
    last_name: Union[Unset, str] = UNSET
    nickname: Union[Unset, str] = UNSET
    position: Union[Unset, str] = UNSET
    timezone: Union[Unset, "Timezone"] = UNSET
    auth_data: Union[Unset, str] = UNSET
    auth_service: Union[Unset, str] = UNSET
    password: Union[Unset, str] = UNSET
    locale: Union[Unset, str] = UNSET
    props: Union[Unset, "CreateUserBodyProps"] = UNSET
    notify_props: Union[Unset, "UserNotifyProps"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        username = self.username

        first_name = self.first_name

        last_name = self.last_name

        nickname = self.nickname

        position = self.position

        timezone: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.timezone, Unset):
            timezone = self.timezone.to_dict()

        auth_data = self.auth_data

        auth_service = self.auth_service

        password = self.password

        locale = self.locale

        props: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.props, Unset):
            props = self.props.to_dict()

        notify_props: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.notify_props, Unset):
            notify_props = self.notify_props.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email": email,
                "username": username,
            }
        )
        if first_name is not UNSET:
            field_dict["first_name"] = first_name
        if last_name is not UNSET:
            field_dict["last_name"] = last_name
        if nickname is not UNSET:
            field_dict["nickname"] = nickname
        if position is not UNSET:
            field_dict["position"] = position
        if timezone is not UNSET:
            field_dict["timezone"] = timezone
        if auth_data is not UNSET:
            field_dict["auth_data"] = auth_data
        if auth_service is not UNSET:
            field_dict["auth_service"] = auth_service
        if password is not UNSET:
            field_dict["password"] = password
        if locale is not UNSET:
            field_dict["locale"] = locale
        if props is not UNSET:
            field_dict["props"] = props
        if notify_props is not UNSET:
            field_dict["notify_props"] = notify_props

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_user_body_props import CreateUserBodyProps
        from ..models.timezone import Timezone
        from ..models.user_notify_props import UserNotifyProps

        d = dict(src_dict)
        email = d.pop("email")

        username = d.pop("username")

        first_name = d.pop("first_name", UNSET)

        last_name = d.pop("last_name", UNSET)

        nickname = d.pop("nickname", UNSET)

        position = d.pop("position", UNSET)

        _timezone = d.pop("timezone", UNSET)
        timezone: Union[Unset, Timezone]
        if isinstance(_timezone, Unset):
            timezone = UNSET
        else:
            timezone = Timezone.from_dict(_timezone)

        auth_data = d.pop("auth_data", UNSET)

        auth_service = d.pop("auth_service", UNSET)

        password = d.pop("password", UNSET)

        locale = d.pop("locale", UNSET)

        _props = d.pop("props", UNSET)
        props: Union[Unset, CreateUserBodyProps]
        if isinstance(_props, Unset):
            props = UNSET
        else:
            props = CreateUserBodyProps.from_dict(_props)

        _notify_props = d.pop("notify_props", UNSET)
        notify_props: Union[Unset, UserNotifyProps]
        if isinstance(_notify_props, Unset):
            notify_props = UNSET
        else:
            notify_props = UserNotifyProps.from_dict(_notify_props)

        create_user_body = cls(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            nickname=nickname,
            position=position,
            timezone=timezone,
            auth_data=auth_data,
            auth_service=auth_service,
            password=password,
            locale=locale,
            props=props,
            notify_props=notify_props,
        )

        create_user_body.additional_properties = d
        return create_user_body

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
