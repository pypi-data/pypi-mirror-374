from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.cloud_storage_status_aws_s3 import CloudStorageStatusAwsS3
    from ..models.cloud_storage_status_azure_blob import CloudStorageStatusAzureBlob
    from ..models.cloud_storage_status_gcp_storage import CloudStorageStatusGcpStorage


T = TypeVar("T", bound="CloudStorageStatus")


@_attrs_define
class CloudStorageStatus:
    """
    Attributes:
        aws_s3 (CloudStorageStatusAwsS3):
        azure_blob (CloudStorageStatusAzureBlob):
        gcp_storage (CloudStorageStatusGcpStorage):
    """

    aws_s3: "CloudStorageStatusAwsS3"
    azure_blob: "CloudStorageStatusAzureBlob"
    gcp_storage: "CloudStorageStatusGcpStorage"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        aws_s3 = self.aws_s3.to_dict()

        azure_blob = self.azure_blob.to_dict()

        gcp_storage = self.gcp_storage.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "aws_s3": aws_s3,
                "azure_blob": azure_blob,
                "gcp_storage": gcp_storage,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cloud_storage_status_aws_s3 import CloudStorageStatusAwsS3
        from ..models.cloud_storage_status_azure_blob import CloudStorageStatusAzureBlob
        from ..models.cloud_storage_status_gcp_storage import CloudStorageStatusGcpStorage

        d = dict(src_dict)
        aws_s3 = CloudStorageStatusAwsS3.from_dict(d.pop("aws_s3"))

        azure_blob = CloudStorageStatusAzureBlob.from_dict(d.pop("azure_blob"))

        gcp_storage = CloudStorageStatusGcpStorage.from_dict(d.pop("gcp_storage"))

        cloud_storage_status = cls(
            aws_s3=aws_s3,
            azure_blob=azure_blob,
            gcp_storage=gcp_storage,
        )

        cloud_storage_status.additional_properties = d
        return cloud_storage_status

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
