from collections.abc import Mapping
from io import BytesIO
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from .. import types
from ..types import UNSET, File, Unset

T = TypeVar("T", bound="BodyUploadBulkFilesApiV2ExternalStorageUploadBulkPost")


@_attrs_define
class BodyUploadBulkFilesApiV2ExternalStorageUploadBulkPost:
    """
    Attributes:
        files (list[File]):
        folder_prefix (Union[None, Unset, str]):
    """

    files: list[File]
    folder_prefix: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        files = []
        for files_item_data in self.files:
            files_item = files_item_data.to_tuple()

            files.append(files_item)

        folder_prefix: Union[None, Unset, str]
        if isinstance(self.folder_prefix, Unset):
            folder_prefix = UNSET
        else:
            folder_prefix = self.folder_prefix

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "files": files,
            }
        )
        if folder_prefix is not UNSET:
            field_dict["folder_prefix"] = folder_prefix

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        for files_item_element in self.files:
            files.append(("files", files_item_element.to_tuple()))

        if not isinstance(self.folder_prefix, Unset):
            if isinstance(self.folder_prefix, str):
                files.append(("folder_prefix", (None, str(self.folder_prefix).encode(), "text/plain")))
            else:
                files.append(("folder_prefix", (None, str(self.folder_prefix).encode(), "text/plain")))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        files = []
        _files = d.pop("files")
        for files_item_data in _files:
            files_item = File(payload=BytesIO(files_item_data))

            files.append(files_item)

        def _parse_folder_prefix(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        folder_prefix = _parse_folder_prefix(d.pop("folder_prefix", UNSET))

        body_upload_bulk_files_api_v2_external_storage_upload_bulk_post = cls(
            files=files,
            folder_prefix=folder_prefix,
        )

        body_upload_bulk_files_api_v2_external_storage_upload_bulk_post.additional_properties = d
        return body_upload_bulk_files_api_v2_external_storage_upload_bulk_post

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
