from collections.abc import Mapping
from io import BytesIO
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import File

T = TypeVar("T", bound="BodyUploadFileApiV1UploadFilePost")


@_attrs_define
class BodyUploadFileApiV1UploadFilePost:
    """
    Attributes:
        file (File):
        path (str):
        checksums_json (str):
    """

    file: File
    path: str
    checksums_json: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        file = self.file.to_tuple()

        path = self.path

        checksums_json = self.checksums_json

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "file": file,
                "path": path,
                "checksums_json": checksums_json,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        file = File(payload=BytesIO(d.pop("file")))

        path = d.pop("path")

        checksums_json = d.pop("checksums_json")

        body_upload_file_api_v1_upload_file_post = cls(
            file=file,
            path=path,
            checksums_json=checksums_json,
        )

        body_upload_file_api_v1_upload_file_post.additional_properties = d
        return body_upload_file_api_v1_upload_file_post

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
