from __future__ import annotations
from typing import Type, Protocol, Generic, TypeVar, get_args
from abc import ABC, abstractmethod
from enum import Flag, auto
import typing
from .type_enforcer import TypeEnforcer

# JSON serializable primitive types
type JsonPrimitiveTypes = str | int | float | bool | dict | list | None

# This is a type alias for all types that can be serialized to JSON
type JsonSerializableTypes = (
    JsonPrimitiveTypes | dict[typing.Any, typing.Any] | list[typing.Any]
)


class OutOfBoundsError(Exception): ...


class SettingValue(ABC):
    @abstractmethod
    def to_dict(self) -> dict: ...
    @abstractmethod
    def from_dict(self, dict_: dict): ...


class SettingValueProtocol(Protocol):
    @abstractmethod
    def to_dict(self) -> dict: ...
    @abstractmethod
    def from_dict(self, dict_: dict): ...


class Level(Flag):
    USER = auto()
    USER_DEV = auto()  # For users with dev_mode
    DEVELOPER = auto()  # For plugin developers
    ADVANCED = auto()
    READ_ONLY = auto()  # Cannot be modified
    READ_ONLY_USER = auto()  # Cannot be modifies by users, can be by code
    HIDDEN = auto()


class SettingType(Flag):
    PERFORMANCE = auto()
    COSMETIC = auto()
    QOL = auto()
    OTHER = auto()


T = TypeVar(
    "T", SettingValue, SettingValueProtocol, JsonSerializableTypes
)  # For nuitka:2.7 (2.8dev)


class SettingBase(Generic[T], TypeEnforcer[T]):
    JsonSerializableTypes = JsonSerializableTypes
    SettingValue = SettingValue
    SettingValueProtocol = SettingValueProtocol

    Level = Level
    SettingType = SettingType

    def __init__(
        self,
        *values: T,
        name: str = "",
        unit: str = "",  # TODO: Better units
        level: Level = Level.USER,
        setting_type: SettingType = SettingType.OTHER,
        description: str = "",
        strongly_typed: bool = True,
        try_parse_after_failure: bool = False,
    ):
        super().__init__(
            *values,
            name=name,
            strongly_typed=strongly_typed,
            try_parse_after_failure=try_parse_after_failure,
        )
        self.name = name
        self.unit = unit
        
        self.level = level
        self.setting_type = setting_type
        self.description = description
        
        self.is_active = True
        self.is_hide_inactive = False
        self.is_hidden = False

        self.dependent_settings = []
        self.dependent_settings_values: dict[T, Setting] = {}
        self.dependent_settings_func: list[tuple[typing.Callable, Setting]] = []

        self._boundaries_handler: typing.Callable = None
        
        self.__post_init__()

    def __post_init__(self):
        pass

    def add_dependent_setting(
        self,
        setting: Setting,
        value: T | None = None,
        value_fn: typing.Callable | None = None,
        hide_inactive: bool = False,
    ) -> typing.Self:
        """Add dependent setting to this setting.

        If value is provided, the setting will be activated when this setting's value is equal to the provided value.
        If value_func is provided, the setting will be activated when the function returns True for this setting's value.

        If hide_inactive is True, the setting will be hidden if it is not active.
        """
        if value:
            self.dependent_settings_values[value] = setting
        elif value_fn:
            self.dependent_settings_func.append((value_fn, setting))
        else:
            raise ValueError("Value or value_func should be provided")
        self.dependent_settings.append(setting)

        setting.set_hide_inactive(hide_inactive)
        if value in self.values or any([value_fn(value) for value in self.values]):
            setting.set_active(True)
        else:
            setting.set_active(False)
        return self
    
    def set_active(self, value: bool = True):
        self.is_active = value
        self.set_hidden(not value)
        return self

    def set_hide_inactive(self, value: bool = True):
        self.is_hide_inactive = value
        self.set_hidden(not self.is_active, respect_is_hide_inactive=value)

    def set_hidden(self, value: bool = True, respect_is_hide_inactive=True):
        """Set setting as hidden.

        If respect_is_hide_inactive is True, then if self.is_hide_inactive is True, the setting will be hidden if it is not active.
        Otherwise, the setting's hidden state will be set to the given value.
        """
        if self.is_hide_inactive and respect_is_hide_inactive:
            self.is_hidden = not self.is_active
        else:
            self.is_hidden = value
        return self

    def set_boundaries_handler(self, fn: typing.Callable) -> typing.Self:
        self._boundaries_handler = fn
        return self

    def set_boundaries_handler_for_value(
        self, fn: typing.Callable, value: T, overwrite_default=False
    ) -> typing.Self:
        return self

    def __set_name__(self, owner: Type, name: str):
        super().__set_name__(owner, name)
        self.name = (
            f"{owner.__name__}.{name} ({self.name})"
            if self.name
            else f"{owner.__name__}.{name}"
        )

    def __call__(self) -> T:
        return self.values
    
    def set_values(self, *values: T) -> typing.Self:
        if self.level is Level.READ_ONLY:
            raise PermissionError(f"Cannot modify a READ_ONLY setting: {self}")
        elif self._boundaries_handler and not all([self._boundaries_handler(value) for value in values]):
            raise OutOfBoundsError(
                f"Value {values} is out of bounds of given boundaries handler: {self}"
            )
        else:
            self.values = values
            self.enforce()

        return self
    
    def __set__(self, instance, *values: T) -> None:
        self.set_values(*values)
    
    def __str__(self) -> str:
        return f"{self.name}: {self._type}({str(self.values)})"  # type: ignore


class Setting(Generic[T], SettingBase[T]):
    def __init__(
        self,
        value: T,
        name: str = "",
        unit: str = "",  # TODO: Better units
        options=None,
        level: Level = Level.USER,
        setting_type: SettingType = SettingType.OTHER,
        description: str = "",
        strongly_typed: bool = True,
        try_parse_after_failure: bool = False,
    ):
        """Class to create setting in the Config. Is strongly typed.
        Create with `Setting[value_type](value)`.

        Value type must either be `Setting.SettingValue`, of `Setting.JsonSerializableTypes` type or use `Setting.SettingValueProtocol`

        By default Setting will not try parsing `value` into instance of `value_type`. Set `strongly_typed` to `False` to change it.

        Value of the class can be accessed by calling the instance:

        ```number = Setting[int](15, 'Some Number')
        number()   # returns a number.value (15)
        ```
        """
        super().__init__(
            value,
            name=name,
            unit=unit,
            level=level,
            setting_type=setting_type,
            description=description,
            strongly_typed=strongly_typed,
            try_parse_after_failure=try_parse_after_failure,
        )
        self.value = self.values[0]
        
        self.options = options

        self.default_value = self.value
    
    def __call__(self):
        return self.value
    
    def set_value(self, value: T) -> typing.Self:
        self.set_values(value)
        self.value = self.values[0]
        return self
    
    def __set__(self, instance, value: T) -> None:
        self.set_value(value)
    
    def __str__(self) -> str:
        return f"{self.name}: {self._type}({str(self.value)}{f' {self.unit}' if self.unit else ''})"  # type: ignore

    def to_dict(self) -> dict[str, JsonSerializableTypes]:
        """Convert setting to dictionary."""
        result = {
            "name": self.name,
            "options": self.options,
            "description": self.description,
            "type": self.setting_type,
        }
        if self._check_type(self._type, JsonSerializableTypes):
            result["value"] = self.value
        else:
            result["value"] = self.value.to_dict()

        return result


class VersionSetting(SettingBase[str | int]):
    def __post_init__(self):
        self.name = "Version"
        if len(self.values) == 1 and isinstance(self.values[1], str):
            self.version = self.values[0]
            self.major, self.minor, self.patch_status = self.version.split(".")
            self.major, self.minor = int(self.major), int(self.minor)
            self.patch, self.status = (
                -1,
                "" if "-" not in self.patch_status else self.patch_status.split("-"),
            )
            
            if not self.patch == -1:
                patch = ""
                for i, char in enumerate(self.patch_status):
                    if char.isnumeric():
                        patch += char
                    else:
                        self.patch = int(patch)
                        self.status = self.patch_status[i:]
                        break
        
        else:
            self.major, self.minor, *self.patch_status = self.values
            if isinstance(self.patch_status, list):
                self.patch, self.status = self.patch_status
            else:
                self.patch = int(self.patch_status)
                self.status = ''
            
            self.version = f'{self.major}.{self.minor}.{self.patch}{'-' + self.status if self.status else ''}'
            print(self.version)
    
    def __call__(self):
        return self.version
    
    def __str__(self) -> str:
        return f"{self.name}: {str(self.version)}"  # type: ignore


class RangeSetting(Generic[T], SettingBase[T]):
    def __init__(
        self,
        min_: T,
        max_: T,
        step: T,
        value: T,
        name: str = "",
        unit: str = "",  # TODO: Better units
        level: Level = Level.USER,
        setting_type: SettingType = SettingType.OTHER,
        description: str = "",
        strongly_typed: bool = True,
        try_parse_after_failure: bool = False,
    ):
        super().__init__(
            value, min_, max_, step,
            name=name,
            unit=unit,
            level=level,
            setting_type=setting_type,
            description=description,
            strongly_typed=strongly_typed,
            try_parse_after_failure=try_parse_after_failure,
        )
        self.value = value
        self.min = min_
        self.max = max_
        self.step_ = step
    
    def set_value(self, value: T) -> typing.Self:
        self.set_values(value)
        self.value = self.values[0]
        return self
    
    def __call__(self):
        return self.value
    
    def __set__(self, instance, value: T) -> None:
        self.set_value(value)
    
    def __str__(self) -> str:
        return f"{self.name}: {self._type}({str(self.value)}{f' {self.unit}' if self.unit else ''})"

    def step(self, steps: int = 1):
        value = self.value + self.step_ * steps
        if value < self.min or value > self.max:
            raise OutOfBoundsError(
                f"Cannot change value by {steps} steps. Calculated value: {value}, min: {self.min}, max: {self.max}"
            )
        self.set_value(value)


class CalculatedSetting(Setting[typing.Callable]):
    def __post_init__(self):
        self.fn = self.value
        return super().__post_init__()
    
    def __call__(self):
        return self.fn()