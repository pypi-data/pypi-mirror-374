from __future__ import annotations
from pathlib import Path
import typing
import json
from .setting import Setting


class ConfigMeta(type):
    """Metaclass for Config to enable proper inheritance and access patterns."""

    def __new__(mcs, name: str, bases: tuple, namespace: dict) -> typing.Type:
        cls = super().__new__(mcs, name, bases, namespace)
        cls._config_name = name
        cls._at_class_creation(cls, name)
        
        # Process nested Config classes to make them proper attributes
        for key, value in cls.__dict__.items():
            cls._handle_key_value(cls, key, value)
            
        return cls
    
    @classmethod
    def _at_class_creation(cls, target_cls, name: str):
        target_cls._nested_configs = {}
        target_cls._settings = {}
    
    @classmethod
    def _handle_key_value(cls, target_cls, key, value):
        if isinstance(value, type) and isinstance(value, ConfigMeta):
            target_cls._nested_configs[key] = value()
        elif isinstance(value, Setting):
            target_cls._settings[key] = value


class ConfigBase(metaclass=ConfigMeta):
    """Base configuration class."""
    
    def __init__(self):
        self._nested_configs: dict[str, ConfigBase]
        self._settings: dict[str, Setting]
        
        for name, config_class in self._nested_configs.items():
            setattr(self, name, config_class)
    
    def get_all_configs(self) -> dict[str, ConfigBase]:
        return self._nested_configs
    
    def get_all_settings(self) -> dict[str, Setting]:
        return self._settings
        
    def to_dict(self) -> dict[str, typing.Any]:
        """Convert config to dictionary recursively."""
        result = {}

        # Process all attributes including inherited ones
        for key, value in vars(self.__class__).items():
            if key.startswith("_"):
                continue

            if isinstance(value, Setting):
                if hasattr(value(), "to_dict") and callable(value().to_dict):
                    result[key] = value().to_dict()
                else:
                    result[key] = value()
            elif issubclass(value, ConfigBase):
                result[key] = value().to_dict()

        return result

    # def to_dict_with_metadata(self) -> dict[str, ]:   # TODO: May be

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> ConfigBase:
        """Create config instance from dictionary."""
        instance = cls()

        for key, value in data.items():
            attr = getattr(instance.__class__, key, None)

            if isinstance(attr, Setting):
                setattr(instance.__class__, key, value)
            elif isinstance(attr, ConfigBase) and isinstance(value, dict):
                # Recursively set nested config
                attr.__class__.from_dict(value)

        return instance

    def save(self, file_path: str | Path) -> None:
        """Save config to JSON file."""
        with open(file_path, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    @classmethod
    def load(cls, file_path: str | Path) -> ConfigBase:
        """Load config from JSON file."""
        with open(file_path, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def to_str(self, tabs) -> str:
        s = f"{self._config_name}:\n"
        for name, setting in self._settings.items():
            s += f'{'  '*tabs}{name}: {setting}\n'
        if self._settings:
            s += '\n'
        for config in self._nested_configs.values():
            s += '  '*tabs + config.to_str(tabs+1)
        return s
            
    def __str__(self) -> str:
        return self.to_str(1)