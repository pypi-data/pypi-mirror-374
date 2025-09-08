from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SubmitPerformanceReportBodyCountersItem")


@_attrs_define
class SubmitPerformanceReportBodyCountersItem:
    """
    Attributes:
        metric (str): The name of the counter
        value (float): The value to increment the counter by
        timestamp (Union[Unset, int]): The time that the counter was incremented
        labels (Union[Unset, list[str]]): Labels to be applied to this metric when recorded by the metrics backend
    """

    metric: str
    value: float
    timestamp: Union[Unset, int] = UNSET
    labels: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        metric = self.metric

        value = self.value

        timestamp = self.timestamp

        labels: Union[Unset, list[str]] = UNSET
        if not isinstance(self.labels, Unset):
            labels = self.labels

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "metric": metric,
                "value": value,
            }
        )
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp
        if labels is not UNSET:
            field_dict["labels"] = labels

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        metric = d.pop("metric")

        value = d.pop("value")

        timestamp = d.pop("timestamp", UNSET)

        labels = cast(list[str], d.pop("labels", UNSET))

        submit_performance_report_body_counters_item = cls(
            metric=metric,
            value=value,
            timestamp=timestamp,
            labels=labels,
        )

        submit_performance_report_body_counters_item.additional_properties = d
        return submit_performance_report_body_counters_item

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
