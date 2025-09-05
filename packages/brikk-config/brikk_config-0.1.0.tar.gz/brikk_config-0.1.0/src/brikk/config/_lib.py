from __future__ import annotations

import json
import os
from typing import Any, Callable, Mapping, Protocol, TypeVar, runtime_checkable

from brikk.config._types import Loader

T = TypeVar("T", covariant=True)


@runtime_checkable
class _PydanticValidator(Protocol[T]):
    def model_validate(self, obj: Any, *, from_attributes: bool) -> T: ...


def load(
    validator: _PydanticValidator[T] | Callable[[Mapping[str, Any]], T],
    loaders: list[Loader],
) -> T:
    _ret = {key: val for loader in loaders for key, val in loader.load().items()}
    if isinstance(validator, _PydanticValidator):
        return validator.model_validate(_ret, from_attributes=False)
    return validator(_ret)


class EnvLoader:
    def __init__(
        self,
        environ: Mapping[str, str] | None = None,
        env_prefix: str = "BRIKK_",
        env_nested_delimiter: str = "__",
    ) -> None:
        self.__environ = environ
        self.__env_prefix = env_prefix
        self.__env_nested_delimiter = env_nested_delimiter

    def load(self) -> Mapping[str, Any]:
        _environ = self.__environ or os.environ

        _ret = {}
        for key, value in (
            (key.upper().strip(self.__env_prefix + "_").lower(), value)
            for key, value in _environ.items()
            if key.upper().startswith(self.__env_prefix)
        ):
            if self.__env_nested_delimiter not in key:
                _ret[key] = value
            else:
                keys = key.split(self.__env_nested_delimiter)

                _value = _ret
                for _key in keys[:-1]:
                    if _key not in _value:
                        _value[_key] = {}
                    _value = _value[_key]
                _value[keys[-1]] = value

        return _ret


class JsonLoader:
    def __init__(self, path: str) -> None:
        self.__path = path

    def load(self) -> Mapping[str, Any]:
        with open(self.__path, "rb") as fp:
            return json.load(fp)
