from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EnvironmentConfigGoogleSettings")


@_attrs_define
class EnvironmentConfigGoogleSettings:
    """
    Attributes:
        enable (Union[Unset, bool]):
        secret (Union[Unset, bool]):
        id (Union[Unset, bool]):
        scope (Union[Unset, bool]):
        auth_endpoint (Union[Unset, bool]):
        token_endpoint (Union[Unset, bool]):
        user_api_endpoint (Union[Unset, bool]):
    """

    enable: Union[Unset, bool] = UNSET
    secret: Union[Unset, bool] = UNSET
    id: Union[Unset, bool] = UNSET
    scope: Union[Unset, bool] = UNSET
    auth_endpoint: Union[Unset, bool] = UNSET
    token_endpoint: Union[Unset, bool] = UNSET
    user_api_endpoint: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enable = self.enable

        secret = self.secret

        id = self.id

        scope = self.scope

        auth_endpoint = self.auth_endpoint

        token_endpoint = self.token_endpoint

        user_api_endpoint = self.user_api_endpoint

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enable is not UNSET:
            field_dict["Enable"] = enable
        if secret is not UNSET:
            field_dict["Secret"] = secret
        if id is not UNSET:
            field_dict["Id"] = id
        if scope is not UNSET:
            field_dict["Scope"] = scope
        if auth_endpoint is not UNSET:
            field_dict["AuthEndpoint"] = auth_endpoint
        if token_endpoint is not UNSET:
            field_dict["TokenEndpoint"] = token_endpoint
        if user_api_endpoint is not UNSET:
            field_dict["UserApiEndpoint"] = user_api_endpoint

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        enable = d.pop("Enable", UNSET)

        secret = d.pop("Secret", UNSET)

        id = d.pop("Id", UNSET)

        scope = d.pop("Scope", UNSET)

        auth_endpoint = d.pop("AuthEndpoint", UNSET)

        token_endpoint = d.pop("TokenEndpoint", UNSET)

        user_api_endpoint = d.pop("UserApiEndpoint", UNSET)

        environment_config_google_settings = cls(
            enable=enable,
            secret=secret,
            id=id,
            scope=scope,
            auth_endpoint=auth_endpoint,
            token_endpoint=token_endpoint,
            user_api_endpoint=user_api_endpoint,
        )

        environment_config_google_settings.additional_properties = d
        return environment_config_google_settings

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
