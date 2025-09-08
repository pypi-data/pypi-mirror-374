from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.migrate_auth_to_saml_body_matches import MigrateAuthToSamlBodyMatches


T = TypeVar("T", bound="MigrateAuthToSamlBody")


@_attrs_define
class MigrateAuthToSamlBody:
    """
    Attributes:
        from_ (str): The current authentication type for the matched users.
        matches (MigrateAuthToSamlBodyMatches): Users map.
        auto (bool):
    """

    from_: str
    matches: "MigrateAuthToSamlBodyMatches"
    auto: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from_ = self.from_

        matches = self.matches.to_dict()

        auto = self.auto

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "from": from_,
                "matches": matches,
                "auto": auto,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.migrate_auth_to_saml_body_matches import MigrateAuthToSamlBodyMatches

        d = dict(src_dict)
        from_ = d.pop("from")

        matches = MigrateAuthToSamlBodyMatches.from_dict(d.pop("matches"))

        auto = d.pop("auto")

        migrate_auth_to_saml_body = cls(
            from_=from_,
            matches=matches,
            auto=auto,
        )

        migrate_auth_to_saml_body.additional_properties = d
        return migrate_auth_to_saml_body

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
