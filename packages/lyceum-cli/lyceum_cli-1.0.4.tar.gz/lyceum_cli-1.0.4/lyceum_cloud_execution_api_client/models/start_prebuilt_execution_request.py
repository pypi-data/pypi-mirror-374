from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.start_prebuilt_execution_aws_credentials import StartPrebuiltExecutionAWSCredentials
    from ..models.start_prebuilt_execution_request_docker_run_env_type_0 import (
        StartPrebuiltExecutionRequestDockerRunEnvType0,
    )


T = TypeVar("T", bound="StartPrebuiltExecutionRequest")


@_attrs_define
class StartPrebuiltExecutionRequest:
    """
    Attributes:
        docker_image (str):
        docker_run_args (Union[None, Unset, list[str]]):
        docker_run_env (Union['StartPrebuiltExecutionRequestDockerRunEnvType0', None, Unset]):
        execution_type (Union[None, Unset, str]):
        callback_url (Union[None, Unset, str]):
        aws_credentials (Union['StartPrebuiltExecutionAWSCredentials', None, Unset]):
    """

    docker_image: str
    docker_run_args: Union[None, Unset, list[str]] = UNSET
    docker_run_env: Union["StartPrebuiltExecutionRequestDockerRunEnvType0", None, Unset] = UNSET
    execution_type: Union[None, Unset, str] = UNSET
    callback_url: Union[None, Unset, str] = UNSET
    aws_credentials: Union["StartPrebuiltExecutionAWSCredentials", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.start_prebuilt_execution_aws_credentials import StartPrebuiltExecutionAWSCredentials
        from ..models.start_prebuilt_execution_request_docker_run_env_type_0 import (
            StartPrebuiltExecutionRequestDockerRunEnvType0,
        )

        docker_image = self.docker_image

        docker_run_args: Union[None, Unset, list[str]]
        if isinstance(self.docker_run_args, Unset):
            docker_run_args = UNSET
        elif isinstance(self.docker_run_args, list):
            docker_run_args = self.docker_run_args

        else:
            docker_run_args = self.docker_run_args

        docker_run_env: Union[None, Unset, dict[str, Any]]
        if isinstance(self.docker_run_env, Unset):
            docker_run_env = UNSET
        elif isinstance(self.docker_run_env, StartPrebuiltExecutionRequestDockerRunEnvType0):
            docker_run_env = self.docker_run_env.to_dict()
        else:
            docker_run_env = self.docker_run_env

        execution_type: Union[None, Unset, str]
        if isinstance(self.execution_type, Unset):
            execution_type = UNSET
        else:
            execution_type = self.execution_type

        callback_url: Union[None, Unset, str]
        if isinstance(self.callback_url, Unset):
            callback_url = UNSET
        else:
            callback_url = self.callback_url

        aws_credentials: Union[None, Unset, dict[str, Any]]
        if isinstance(self.aws_credentials, Unset):
            aws_credentials = UNSET
        elif isinstance(self.aws_credentials, StartPrebuiltExecutionAWSCredentials):
            aws_credentials = self.aws_credentials.to_dict()
        else:
            aws_credentials = self.aws_credentials

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "docker_image": docker_image,
            }
        )
        if docker_run_args is not UNSET:
            field_dict["docker_run_args"] = docker_run_args
        if docker_run_env is not UNSET:
            field_dict["docker_run_env"] = docker_run_env
        if execution_type is not UNSET:
            field_dict["execution_type"] = execution_type
        if callback_url is not UNSET:
            field_dict["callback_url"] = callback_url
        if aws_credentials is not UNSET:
            field_dict["aws_credentials"] = aws_credentials

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.start_prebuilt_execution_aws_credentials import StartPrebuiltExecutionAWSCredentials
        from ..models.start_prebuilt_execution_request_docker_run_env_type_0 import (
            StartPrebuiltExecutionRequestDockerRunEnvType0,
        )

        d = dict(src_dict)
        docker_image = d.pop("docker_image")

        def _parse_docker_run_args(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                docker_run_args_type_0 = cast(list[str], data)

                return docker_run_args_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        docker_run_args = _parse_docker_run_args(d.pop("docker_run_args", UNSET))

        def _parse_docker_run_env(data: object) -> Union["StartPrebuiltExecutionRequestDockerRunEnvType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                docker_run_env_type_0 = StartPrebuiltExecutionRequestDockerRunEnvType0.from_dict(data)

                return docker_run_env_type_0
            except:  # noqa: E722
                pass
            return cast(Union["StartPrebuiltExecutionRequestDockerRunEnvType0", None, Unset], data)

        docker_run_env = _parse_docker_run_env(d.pop("docker_run_env", UNSET))

        def _parse_execution_type(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        execution_type = _parse_execution_type(d.pop("execution_type", UNSET))

        def _parse_callback_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        callback_url = _parse_callback_url(d.pop("callback_url", UNSET))

        def _parse_aws_credentials(data: object) -> Union["StartPrebuiltExecutionAWSCredentials", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                aws_credentials_type_0 = StartPrebuiltExecutionAWSCredentials.from_dict(data)

                return aws_credentials_type_0
            except:  # noqa: E722
                pass
            return cast(Union["StartPrebuiltExecutionAWSCredentials", None, Unset], data)

        aws_credentials = _parse_aws_credentials(d.pop("aws_credentials", UNSET))

        start_prebuilt_execution_request = cls(
            docker_image=docker_image,
            docker_run_args=docker_run_args,
            docker_run_env=docker_run_env,
            execution_type=execution_type,
            callback_url=callback_url,
            aws_credentials=aws_credentials,
        )

        start_prebuilt_execution_request.additional_properties = d
        return start_prebuilt_execution_request

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
