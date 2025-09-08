from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.user_thread import UserThread


T = TypeVar("T", bound="UserThreads")


@_attrs_define
class UserThreads:
    """
    Attributes:
        total (Union[Unset, int]): Total number of threads (used for paging)
        threads (Union[Unset, list['UserThread']]): Array of threads
    """

    total: Union[Unset, int] = UNSET
    threads: Union[Unset, list["UserThread"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total = self.total

        threads: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.threads, Unset):
            threads = []
            for threads_item_data in self.threads:
                threads_item = threads_item_data.to_dict()
                threads.append(threads_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if total is not UNSET:
            field_dict["total"] = total
        if threads is not UNSET:
            field_dict["threads"] = threads

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user_thread import UserThread

        d = dict(src_dict)
        total = d.pop("total", UNSET)

        threads = []
        _threads = d.pop("threads", UNSET)
        for threads_item_data in _threads or []:
            threads_item = UserThread.from_dict(threads_item_data)

            threads.append(threads_item)

        user_threads = cls(
            total=total,
            threads=threads,
        )

        user_threads.additional_properties = d
        return user_threads

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
