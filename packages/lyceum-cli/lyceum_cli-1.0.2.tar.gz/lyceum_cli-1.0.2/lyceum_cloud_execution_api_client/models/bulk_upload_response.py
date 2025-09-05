from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.bulk_upload_result import BulkUploadResult


T = TypeVar("T", bound="BulkUploadResponse")


@_attrs_define
class BulkUploadResponse:
    """
    Attributes:
        total_files (int):
        successful_uploads (int):
        failed_uploads (int):
        results (list['BulkUploadResult']):
        message (str):
    """

    total_files: int
    successful_uploads: int
    failed_uploads: int
    results: list["BulkUploadResult"]
    message: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total_files = self.total_files

        successful_uploads = self.successful_uploads

        failed_uploads = self.failed_uploads

        results = []
        for results_item_data in self.results:
            results_item = results_item_data.to_dict()
            results.append(results_item)

        message = self.message

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total_files": total_files,
                "successful_uploads": successful_uploads,
                "failed_uploads": failed_uploads,
                "results": results,
                "message": message,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.bulk_upload_result import BulkUploadResult

        d = dict(src_dict)
        total_files = d.pop("total_files")

        successful_uploads = d.pop("successful_uploads")

        failed_uploads = d.pop("failed_uploads")

        results = []
        _results = d.pop("results")
        for results_item_data in _results:
            results_item = BulkUploadResult.from_dict(results_item_data)

            results.append(results_item)

        message = d.pop("message")

        bulk_upload_response = cls(
            total_files=total_files,
            successful_uploads=successful_uploads,
            failed_uploads=failed_uploads,
            results=results,
            message=message,
        )

        bulk_upload_response.additional_properties = d
        return bulk_upload_response

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
