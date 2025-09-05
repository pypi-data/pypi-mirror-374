from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CodeExecution")


@_attrs_define
class CodeExecution:
    """
    Attributes:
        code (str):
        timeout (Union[Unset, int]):  Default: 60.
        requirements_content (Union[None, Unset, str]):
        kernel_state (Union[None, Unset, str]):
        prior_imports (Union[None, Unset, list[str]]): List of import calls as strings to prepend before code execution
        nbcode (Union[None, Unset, str]):
        file_name (Union[None, Unset, str]):
        execution_type (Union[None, Unset, str]):  Default: 'cpu'.
        import_files (Union[None, Unset, str]):
    """

    code: str
    timeout: Union[Unset, int] = 60
    requirements_content: Union[None, Unset, str] = UNSET
    kernel_state: Union[None, Unset, str] = UNSET
    prior_imports: Union[None, Unset, list[str]] = UNSET
    nbcode: Union[None, Unset, str] = UNSET
    file_name: Union[None, Unset, str] = UNSET
    execution_type: Union[None, Unset, str] = "cpu"
    import_files: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        code = self.code

        timeout = self.timeout

        requirements_content: Union[None, Unset, str]
        if isinstance(self.requirements_content, Unset):
            requirements_content = UNSET
        else:
            requirements_content = self.requirements_content

        kernel_state: Union[None, Unset, str]
        if isinstance(self.kernel_state, Unset):
            kernel_state = UNSET
        else:
            kernel_state = self.kernel_state

        prior_imports: Union[None, Unset, list[str]]
        if isinstance(self.prior_imports, Unset):
            prior_imports = UNSET
        elif isinstance(self.prior_imports, list):
            prior_imports = self.prior_imports

        else:
            prior_imports = self.prior_imports

        nbcode: Union[None, Unset, str]
        if isinstance(self.nbcode, Unset):
            nbcode = UNSET
        else:
            nbcode = self.nbcode

        file_name: Union[None, Unset, str]
        if isinstance(self.file_name, Unset):
            file_name = UNSET
        else:
            file_name = self.file_name

        execution_type: Union[None, Unset, str]
        if isinstance(self.execution_type, Unset):
            execution_type = UNSET
        else:
            execution_type = self.execution_type

        import_files: Union[None, Unset, str]
        if isinstance(self.import_files, Unset):
            import_files = UNSET
        else:
            import_files = self.import_files

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "code": code,
            }
        )
        if timeout is not UNSET:
            field_dict["timeout"] = timeout
        if requirements_content is not UNSET:
            field_dict["requirements_content"] = requirements_content
        if kernel_state is not UNSET:
            field_dict["kernel_state"] = kernel_state
        if prior_imports is not UNSET:
            field_dict["prior_imports"] = prior_imports
        if nbcode is not UNSET:
            field_dict["nbcode"] = nbcode
        if file_name is not UNSET:
            field_dict["file_name"] = file_name
        if execution_type is not UNSET:
            field_dict["execution_type"] = execution_type
        if import_files is not UNSET:
            field_dict["import_files"] = import_files

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        code = d.pop("code")

        timeout = d.pop("timeout", UNSET)

        def _parse_requirements_content(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        requirements_content = _parse_requirements_content(d.pop("requirements_content", UNSET))

        def _parse_kernel_state(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        kernel_state = _parse_kernel_state(d.pop("kernel_state", UNSET))

        def _parse_prior_imports(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                prior_imports_type_0 = cast(list[str], data)

                return prior_imports_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        prior_imports = _parse_prior_imports(d.pop("prior_imports", UNSET))

        def _parse_nbcode(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        nbcode = _parse_nbcode(d.pop("nbcode", UNSET))

        def _parse_file_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        file_name = _parse_file_name(d.pop("file_name", UNSET))

        def _parse_execution_type(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        execution_type = _parse_execution_type(d.pop("execution_type", UNSET))

        def _parse_import_files(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        import_files = _parse_import_files(d.pop("import_files", UNSET))

        code_execution = cls(
            code=code,
            timeout=timeout,
            requirements_content=requirements_content,
            kernel_state=kernel_state,
            prior_imports=prior_imports,
            nbcode=nbcode,
            file_name=file_name,
            execution_type=execution_type,
            import_files=import_files,
        )

        code_execution.additional_properties = d
        return code_execution

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
