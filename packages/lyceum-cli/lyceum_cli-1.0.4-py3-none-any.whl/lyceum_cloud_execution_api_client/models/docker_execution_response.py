from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="DockerExecutionResponse")


@_attrs_define
class DockerExecutionResponse:
    """
    Attributes:
        execution_id (str):
        status (str):
        stream_url (str):
        execution_type (str):
    """

    execution_id: str
    status: str
    stream_url: str
    execution_type: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        execution_id = self.execution_id

        status = self.status

        stream_url = self.stream_url

        execution_type = self.execution_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "execution_id": execution_id,
                "status": status,
                "stream_url": stream_url,
                "execution_type": execution_type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        execution_id = d.pop("execution_id")

        status = d.pop("status")

        stream_url = d.pop("stream_url")

        execution_type = d.pop("execution_type")

        docker_execution_response = cls(
            execution_id=execution_id,
            status=status,
            stream_url=stream_url,
            execution_type=execution_type,
        )

        docker_execution_response.additional_properties = d
        return docker_execution_response

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
