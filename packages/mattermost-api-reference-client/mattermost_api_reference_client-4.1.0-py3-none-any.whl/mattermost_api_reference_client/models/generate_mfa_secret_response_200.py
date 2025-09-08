from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GenerateMfaSecretResponse200")


@_attrs_define
class GenerateMfaSecretResponse200:
    """
    Attributes:
        secret (Union[Unset, str]): The MFA secret as a string
        qr_code (Union[Unset, str]): A base64 encoded QR code image
    """

    secret: Union[Unset, str] = UNSET
    qr_code: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        secret = self.secret

        qr_code = self.qr_code

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if secret is not UNSET:
            field_dict["secret"] = secret
        if qr_code is not UNSET:
            field_dict["qr_code"] = qr_code

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        secret = d.pop("secret", UNSET)

        qr_code = d.pop("qr_code", UNSET)

        generate_mfa_secret_response_200 = cls(
            secret=secret,
            qr_code=qr_code,
        )

        generate_mfa_secret_response_200.additional_properties = d
        return generate_mfa_secret_response_200

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
