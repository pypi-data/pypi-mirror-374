from collections.abc import Mapping
from io import BytesIO
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from .. import types
from ..types import File

T = TypeVar("T", bound="ImportTeamBody")


@_attrs_define
class ImportTeamBody:
    """
    Attributes:
        file (File): A file to be uploaded in zip format.
        filesize (int): The size of the zip file to be imported.
        import_from (str): String that defines from which application the team was exported to be imported into
            Mattermost.
    """

    file: File
    filesize: int
    import_from: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        file = self.file.to_tuple()

        filesize = self.filesize

        import_from = self.import_from

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "file": file,
                "filesize": filesize,
                "importFrom": import_from,
            }
        )

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        files.append(("file", self.file.to_tuple()))

        files.append(("filesize", (None, str(self.filesize).encode(), "text/plain")))

        files.append(("importFrom", (None, str(self.import_from).encode(), "text/plain")))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        file = File(payload=BytesIO(d.pop("file")))

        filesize = d.pop("filesize")

        import_from = d.pop("importFrom")

        import_team_body = cls(
            file=file,
            filesize=filesize,
            import_from=import_from,
        )

        import_team_body.additional_properties = d
        return import_team_body

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
