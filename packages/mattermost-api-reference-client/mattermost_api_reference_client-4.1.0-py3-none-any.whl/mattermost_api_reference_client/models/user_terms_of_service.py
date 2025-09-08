from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UserTermsOfService")


@_attrs_define
class UserTermsOfService:
    """
    Attributes:
        user_id (Union[Unset, str]): The unique identifier of the user who performed this terms of service action.
        terms_of_service_id (Union[Unset, str]): The unique identifier of the terms of service the action was performed
            on.
        create_at (Union[Unset, int]): The time in milliseconds that this action was performed.
    """

    user_id: Union[Unset, str] = UNSET
    terms_of_service_id: Union[Unset, str] = UNSET
    create_at: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_id = self.user_id

        terms_of_service_id = self.terms_of_service_id

        create_at = self.create_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if terms_of_service_id is not UNSET:
            field_dict["terms_of_service_id"] = terms_of_service_id
        if create_at is not UNSET:
            field_dict["create_at"] = create_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        user_id = d.pop("user_id", UNSET)

        terms_of_service_id = d.pop("terms_of_service_id", UNSET)

        create_at = d.pop("create_at", UNSET)

        user_terms_of_service = cls(
            user_id=user_id,
            terms_of_service_id=terms_of_service_id,
            create_at=create_at,
        )

        user_terms_of_service.additional_properties = d
        return user_terms_of_service

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
