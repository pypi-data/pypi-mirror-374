from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.timezone import Timezone
    from ..models.update_user_body_props import UpdateUserBodyProps
    from ..models.user_notify_props import UserNotifyProps


T = TypeVar("T", bound="UpdateUserBody")


@_attrs_define
class UpdateUserBody:
    """
    Attributes:
        id (str):
        email (str):
        username (str):
        first_name (Union[Unset, str]):
        last_name (Union[Unset, str]):
        nickname (Union[Unset, str]):
        locale (Union[Unset, str]):
        position (Union[Unset, str]):
        timezone (Union[Unset, Timezone]):
        props (Union[Unset, UpdateUserBodyProps]):
        notify_props (Union[Unset, UserNotifyProps]):
    """

    id: str
    email: str
    username: str
    first_name: Union[Unset, str] = UNSET
    last_name: Union[Unset, str] = UNSET
    nickname: Union[Unset, str] = UNSET
    locale: Union[Unset, str] = UNSET
    position: Union[Unset, str] = UNSET
    timezone: Union[Unset, "Timezone"] = UNSET
    props: Union[Unset, "UpdateUserBodyProps"] = UNSET
    notify_props: Union[Unset, "UserNotifyProps"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        email = self.email

        username = self.username

        first_name = self.first_name

        last_name = self.last_name

        nickname = self.nickname

        locale = self.locale

        position = self.position

        timezone: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.timezone, Unset):
            timezone = self.timezone.to_dict()

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
                "id": id,
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
        if locale is not UNSET:
            field_dict["locale"] = locale
        if position is not UNSET:
            field_dict["position"] = position
        if timezone is not UNSET:
            field_dict["timezone"] = timezone
        if props is not UNSET:
            field_dict["props"] = props
        if notify_props is not UNSET:
            field_dict["notify_props"] = notify_props

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.timezone import Timezone
        from ..models.update_user_body_props import UpdateUserBodyProps
        from ..models.user_notify_props import UserNotifyProps

        d = dict(src_dict)
        id = d.pop("id")

        email = d.pop("email")

        username = d.pop("username")

        first_name = d.pop("first_name", UNSET)

        last_name = d.pop("last_name", UNSET)

        nickname = d.pop("nickname", UNSET)

        locale = d.pop("locale", UNSET)

        position = d.pop("position", UNSET)

        _timezone = d.pop("timezone", UNSET)
        timezone: Union[Unset, Timezone]
        if isinstance(_timezone, Unset):
            timezone = UNSET
        else:
            timezone = Timezone.from_dict(_timezone)

        _props = d.pop("props", UNSET)
        props: Union[Unset, UpdateUserBodyProps]
        if isinstance(_props, Unset):
            props = UNSET
        else:
            props = UpdateUserBodyProps.from_dict(_props)

        _notify_props = d.pop("notify_props", UNSET)
        notify_props: Union[Unset, UserNotifyProps]
        if isinstance(_notify_props, Unset):
            notify_props = UNSET
        else:
            notify_props = UserNotifyProps.from_dict(_notify_props)

        update_user_body = cls(
            id=id,
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            nickname=nickname,
            locale=locale,
            position=position,
            timezone=timezone,
            props=props,
            notify_props=notify_props,
        )

        update_user_body.additional_properties = d
        return update_user_body

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
