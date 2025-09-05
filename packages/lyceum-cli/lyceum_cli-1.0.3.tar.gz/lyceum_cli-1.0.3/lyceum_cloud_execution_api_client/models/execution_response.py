from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.execution_response_result_files_type_0 import ExecutionResponseResultFilesType0


T = TypeVar("T", bound="ExecutionResponse")


@_attrs_define
class ExecutionResponse:
    """
    Attributes:
        execution_id (str):
        status (str):
        user_id (str):
        output (Union[Unset, str]):
        error (Union[Unset, str]):
        user_error (Union[None, Unset, str]):
        execution_time (Union[Unset, float]):
        exit_code (Union[Unset, int]):
        result_vars (Union[None, Unset, str]):
        result_files (Union['ExecutionResponseResultFilesType0', None, Unset]):
        execution_type (Union[None, Unset, str]):  Default: 'cpu'.
    """

    execution_id: str
    status: str
    user_id: str
    output: Union[Unset, str] = UNSET
    error: Union[Unset, str] = UNSET
    user_error: Union[None, Unset, str] = UNSET
    execution_time: Union[Unset, float] = UNSET
    exit_code: Union[Unset, int] = UNSET
    result_vars: Union[None, Unset, str] = UNSET
    result_files: Union["ExecutionResponseResultFilesType0", None, Unset] = UNSET
    execution_type: Union[None, Unset, str] = "cpu"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.execution_response_result_files_type_0 import ExecutionResponseResultFilesType0

        execution_id = self.execution_id

        status = self.status

        user_id = self.user_id

        output = self.output

        error = self.error

        user_error: Union[None, Unset, str]
        if isinstance(self.user_error, Unset):
            user_error = UNSET
        else:
            user_error = self.user_error

        execution_time = self.execution_time

        exit_code = self.exit_code

        result_vars: Union[None, Unset, str]
        if isinstance(self.result_vars, Unset):
            result_vars = UNSET
        else:
            result_vars = self.result_vars

        result_files: Union[None, Unset, dict[str, Any]]
        if isinstance(self.result_files, Unset):
            result_files = UNSET
        elif isinstance(self.result_files, ExecutionResponseResultFilesType0):
            result_files = self.result_files.to_dict()
        else:
            result_files = self.result_files

        execution_type: Union[None, Unset, str]
        if isinstance(self.execution_type, Unset):
            execution_type = UNSET
        else:
            execution_type = self.execution_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "execution_id": execution_id,
                "status": status,
                "user_id": user_id,
            }
        )
        if output is not UNSET:
            field_dict["output"] = output
        if error is not UNSET:
            field_dict["error"] = error
        if user_error is not UNSET:
            field_dict["user_error"] = user_error
        if execution_time is not UNSET:
            field_dict["execution_time"] = execution_time
        if exit_code is not UNSET:
            field_dict["exit_code"] = exit_code
        if result_vars is not UNSET:
            field_dict["result_vars"] = result_vars
        if result_files is not UNSET:
            field_dict["result_files"] = result_files
        if execution_type is not UNSET:
            field_dict["execution_type"] = execution_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.execution_response_result_files_type_0 import ExecutionResponseResultFilesType0

        d = dict(src_dict)
        execution_id = d.pop("execution_id")

        status = d.pop("status")

        user_id = d.pop("user_id")

        output = d.pop("output", UNSET)

        error = d.pop("error", UNSET)

        def _parse_user_error(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        user_error = _parse_user_error(d.pop("user_error", UNSET))

        execution_time = d.pop("execution_time", UNSET)

        exit_code = d.pop("exit_code", UNSET)

        def _parse_result_vars(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        result_vars = _parse_result_vars(d.pop("result_vars", UNSET))

        def _parse_result_files(data: object) -> Union["ExecutionResponseResultFilesType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                result_files_type_0 = ExecutionResponseResultFilesType0.from_dict(data)

                return result_files_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ExecutionResponseResultFilesType0", None, Unset], data)

        result_files = _parse_result_files(d.pop("result_files", UNSET))

        def _parse_execution_type(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        execution_type = _parse_execution_type(d.pop("execution_type", UNSET))

        execution_response = cls(
            execution_id=execution_id,
            status=status,
            user_id=user_id,
            output=output,
            error=error,
            user_error=user_error,
            execution_time=execution_time,
            exit_code=exit_code,
            result_vars=result_vars,
            result_files=result_files,
            execution_type=execution_type,
        )

        execution_response.additional_properties = d
        return execution_response

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
