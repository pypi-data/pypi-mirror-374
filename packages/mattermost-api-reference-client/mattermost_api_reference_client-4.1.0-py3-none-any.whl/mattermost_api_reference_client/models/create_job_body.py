from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_job_body_data import CreateJobBodyData


T = TypeVar("T", bound="CreateJobBody")


@_attrs_define
class CreateJobBody:
    """
    Attributes:
        type_ (str): The type of job to create
        data (Union[Unset, CreateJobBodyData]): An object containing any additional data required for this job type
    """

    type_: str
    data: Union[Unset, "CreateJobBodyData"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        data: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.data, Unset):
            data = self.data.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
            }
        )
        if data is not UNSET:
            field_dict["data"] = data

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_job_body_data import CreateJobBodyData

        d = dict(src_dict)
        type_ = d.pop("type")

        _data = d.pop("data", UNSET)
        data: Union[Unset, CreateJobBodyData]
        if isinstance(_data, Unset):
            data = UNSET
        else:
            data = CreateJobBodyData.from_dict(_data)

        create_job_body = cls(
            type_=type_,
            data=data,
        )

        create_job_body.additional_properties = d
        return create_job_body

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
