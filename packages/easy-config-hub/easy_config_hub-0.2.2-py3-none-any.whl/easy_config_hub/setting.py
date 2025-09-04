from __future__ import annotations
from typing import Type, Protocol
from abc import ABC, abstractmethod
from enum import Flag, auto
import typing
from type_enforcer import TypeEnforcer

# JSON serializable primitive types
type JsonPrimitiveTypes = str | int | float | bool | dict | list | None

# This is a type alias for all types that can be serialized to JSON
type JsonSerializableTypes = (
    JsonPrimitiveTypes | dict[typing.Any, typing.Any] | list[typing.Any]
)


class SettingValue(ABC):
    @abstractmethod
    def to_dict(self) -> dict:
        pass

    @abstractmethod
    def from_dict(self, dict_: dict):
        pass


class SettingValueProtocol(Protocol):
    def to_dict(self) -> dict: ...

    @abstractmethod
    def from_dict(self, dict_: dict): ...



class Level(Flag):
    USER = auto()
    USER_DEV = auto()   # For users with dev_mode
    DEVELOPER = auto()  # For plugin developers
    ADVANCED = auto()
    READ_ONLY = auto()
    HIDDEN = auto()
    
class SettingType(Flag):
    PERFORMANCE = auto()
    COSMETIC = auto()
    QOL = auto()
    OTHER = auto()

class Setting[T: SettingValue | SettingValueProtocol | JsonSerializableTypes](
    TypeEnforcer[T]
):
    JsonSerializableTypes = JsonSerializableTypes
    SettingValue = SettingValue
    SettingValueProtocol = SettingValueProtocol
    
    Level = Level
    SettingType = SettingType

    def __init__(
        self,
        value: T,
        name: str = "",
        unit: str = "",     # TODO: Better units
        options=None,
        level: Level=Level.USER,
        type_: SettingType=SettingType.OTHER,
        description="",
        strongly_typed: bool = True,
    ):
        """Class to create setting in the Config. Is strongly typed.
        Create with `Setting[value_type](value)`.

        Value type must either be `Setting.SettingValue`, of `Setting.JsonSerializableTypes` type or use `Setting.SettingValueProtocol`

        By default Setting will not try parsing `value` into instance of `value_type`. Set `strongly_typed` to `False` to change it.

        Value of the class can be accessed by calling the instance:

        ```number = Setting[int](15, 'Some Number')
        number()   # returns a number._value (15)
        ```
        """
        super().__init__(value, strongly_typed)
        self.name = name
        self.unit = unit
        self.options = options
        self.level = level
        self.type_ = type_
        self.description = description

        self._type: Type[T] | None = None

    def __call__(self) -> T:
        return self._value

    def __set__(self, instance, value: T) -> None:
        self._check_type(value, self._type)

    def __str__(self) -> str:
        return f"{self.name}: {self._type.__name__}({self()}{f' {self.unit}' if self.unit else ''})"    # type: ignore

    def to_dict(self) -> dict[str, JsonSerializableTypes]:
        """Convert setting to dictionary."""
        result = {
            "name": self.name,
            "options": self.options,
            "description": self.description,
            "type": self.type_,
        }
        if self._check_type(self._type, JsonSerializableTypes):
            result["value"] = self._value
        else:
            result["value"] = self._value.to_dict()
        
        return result