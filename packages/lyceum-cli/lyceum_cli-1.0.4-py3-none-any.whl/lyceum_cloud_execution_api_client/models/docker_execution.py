from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.docker_execution_docker_env_type_0 import DockerExecutionDockerEnvType0


T = TypeVar("T", bound="DockerExecution")


@_attrs_define
class DockerExecution:
    """
    Attributes:
        docker_image (str): Docker image to execute (e.g., 'ubuntu:latest')
        docker_cmd (Union[None, Unset, list[str]]): Command to run in container
        docker_env (Union['DockerExecutionDockerEnvType0', None, Unset]): Environment variables
        execution_type (Union[Unset, str]): Hardware profile: cpu, a100, h100 Default: 'cpu'.
        callback_url (Union[None, Unset, str]): Webhook URL for completion notification
        timeout (Union[Unset, int]): Execution timeout in seconds Default: 300.
        file_name (Union[None, Unset, str]): Name for the execution
        docker_registry_credentials (Union[None, Unset, dict[str, Any]]): Docker registry credentials JSON
        docker_registry_credential_type (Union[None, Unset, str]): Registry credential type: basic, aws, etc.
    """

    docker_image: str
    docker_cmd: Union[None, Unset, list[str]] = UNSET
    docker_env: Union["DockerExecutionDockerEnvType0", None, Unset] = UNSET
    execution_type: Union[Unset, str] = "cpu"
    callback_url: Union[None, Unset, str] = UNSET
    timeout: Union[Unset, int] = 300
    file_name: Union[None, Unset, str] = UNSET
    docker_registry_credentials: Union[None, Unset, dict[str, Any]] = UNSET
    docker_registry_credential_type: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.docker_execution_docker_env_type_0 import DockerExecutionDockerEnvType0

        docker_image = self.docker_image

        docker_cmd: Union[None, Unset, list[str]]
        if isinstance(self.docker_cmd, Unset):
            docker_cmd = UNSET
        elif isinstance(self.docker_cmd, list):
            docker_cmd = self.docker_cmd

        else:
            docker_cmd = self.docker_cmd

        docker_env: Union[None, Unset, dict[str, Any]]
        if isinstance(self.docker_env, Unset):
            docker_env = UNSET
        elif isinstance(self.docker_env, DockerExecutionDockerEnvType0):
            docker_env = self.docker_env.to_dict()
        else:
            docker_env = self.docker_env

        execution_type = self.execution_type

        callback_url: Union[None, Unset, str]
        if isinstance(self.callback_url, Unset):
            callback_url = UNSET
        else:
            callback_url = self.callback_url

        timeout = self.timeout

        file_name: Union[None, Unset, str]
        if isinstance(self.file_name, Unset):
            file_name = UNSET
        else:
            file_name = self.file_name

        docker_registry_credentials: Union[None, Unset, dict[str, Any]]
        if isinstance(self.docker_registry_credentials, Unset):
            docker_registry_credentials = UNSET
        else:
            docker_registry_credentials = self.docker_registry_credentials

        docker_registry_credential_type: Union[None, Unset, str]
        if isinstance(self.docker_registry_credential_type, Unset):
            docker_registry_credential_type = UNSET
        else:
            docker_registry_credential_type = self.docker_registry_credential_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "docker_image": docker_image,
            }
        )
        if docker_cmd is not UNSET:
            field_dict["docker_cmd"] = docker_cmd
        if docker_env is not UNSET:
            field_dict["docker_env"] = docker_env
        if execution_type is not UNSET:
            field_dict["execution_type"] = execution_type
        if callback_url is not UNSET:
            field_dict["callback_url"] = callback_url
        if timeout is not UNSET:
            field_dict["timeout"] = timeout
        if file_name is not UNSET:
            field_dict["file_name"] = file_name
        if docker_registry_credentials is not UNSET:
            field_dict["docker_registry_credentials"] = docker_registry_credentials
        if docker_registry_credential_type is not UNSET:
            field_dict["docker_registry_credential_type"] = docker_registry_credential_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.docker_execution_docker_env_type_0 import DockerExecutionDockerEnvType0

        d = dict(src_dict)
        docker_image = d.pop("docker_image")

        def _parse_docker_cmd(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                docker_cmd_type_0 = cast(list[str], data)

                return docker_cmd_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        docker_cmd = _parse_docker_cmd(d.pop("docker_cmd", UNSET))

        def _parse_docker_env(data: object) -> Union["DockerExecutionDockerEnvType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                docker_env_type_0 = DockerExecutionDockerEnvType0.from_dict(data)

                return docker_env_type_0
            except:  # noqa: E722
                pass
            return cast(Union["DockerExecutionDockerEnvType0", None, Unset], data)

        docker_env = _parse_docker_env(d.pop("docker_env", UNSET))

        execution_type = d.pop("execution_type", UNSET)

        def _parse_callback_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        callback_url = _parse_callback_url(d.pop("callback_url", UNSET))

        timeout = d.pop("timeout", UNSET)

        def _parse_file_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        file_name = _parse_file_name(d.pop("file_name", UNSET))

        def _parse_docker_registry_credentials(data: object) -> Union[None, Unset, dict[str, Any]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, dict[str, Any]], data)

        docker_registry_credentials = _parse_docker_registry_credentials(d.pop("docker_registry_credentials", UNSET))

        def _parse_docker_registry_credential_type(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        docker_registry_credential_type = _parse_docker_registry_credential_type(d.pop("docker_registry_credential_type", UNSET))

        docker_execution = cls(
            docker_image=docker_image,
            docker_cmd=docker_cmd,
            docker_env=docker_env,
            execution_type=execution_type,
            callback_url=callback_url,
            timeout=timeout,
            file_name=file_name,
            docker_registry_credentials=docker_registry_credentials,
            docker_registry_credential_type=docker_registry_credential_type,
        )

        docker_execution.additional_properties = d
        return docker_execution

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
