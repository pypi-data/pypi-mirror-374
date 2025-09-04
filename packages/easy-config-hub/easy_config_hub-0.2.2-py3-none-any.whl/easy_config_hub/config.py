from __future__ import annotations
from pathlib import Path
import typing
import json
from setting import Setting


class ConfigMeta(type):
    """Metaclass for Config to enable proper inheritance and access patterns."""

    def __new__(mcs, name: str, bases: tuple, namespace: dict) -> typing.Type:
        cls = super().__new__(mcs, name, bases, namespace)
        setattr(cls, '_config_name', name)
        cls._at_class_creation()

        # Process nested Config classes to make them proper attributes
        for key, value in list(cls.__dict__.items()):
            cls._handle_key_value(key, value)

        return cls
    
    @classmethod
    def _at_class_creation(cls):
        pass
    
    @classmethod
    def _handle_key_value(cls, key, value):
        if isinstance(value, type) and issubclass(value, Config):
            # Replace the class reference with an instance
            setattr(cls, key, value())
            
class Config(metaclass=ConfigMeta):
    """Base configuration class."""

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
            elif isinstance(value, Config):
                result[key] = value.to_dict()

        return result

    # def to_dict_with_metadata(self) -> dict[str, ]:   # TODO: May be

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> Config:
        """Create config instance from dictionary."""
        instance = cls()

        for key, value in data.items():
            attr = getattr(instance.__class__, key, None)

            if isinstance(attr, Setting):
                setattr(instance.__class__, key, value)
            elif isinstance(attr, Config) and isinstance(value, dict):
                # Recursively set nested config
                attr.__class__.from_dict(value)

        return instance

    def save(self, file_path: str | Path) -> None:
        """Save config to JSON file."""
        with open(file_path, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    @classmethod
    def load(cls, file_path: str | Path) -> Config:
        """Load config from JSON file."""
        with open(file_path, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def get_settings_dict(self) -> dict[str | Config, Setting]:
        result = {}

        for key, value in vars(self.__class__).items():
            if key.startswith("_"):
                continue

            if isinstance(value, Setting):
                result[key] = value
            elif isinstance(value, Config):
                result[key] = value.get_settings_dict()

        return result

    def get_all_settings(self) -> dict[str, Setting]:
        """Get all settings recursively with their full paths."""
        result = {}

        def collect_settings(config, prefix=""):
            for key, value in vars(config.__class__).items():
                if key.startswith("_"):
                    continue

                full_path = f"{prefix}{key}" if prefix else key

                if isinstance(value, Setting):
                    result[full_path] = value
                elif isinstance(value, Config):
                    collect_settings(value, f"{full_path}.")

        collect_settings(self)
        return result

    def __str__(self) -> str:
        def handle_dict(dict_: dict[str, Setting | dict], indent: int = 1) -> str:
            s = ""
            for key, value in dict_.items():
                if isinstance(value, dict):
                    s += "\n" + "  " * indent + f"{key}:\n"
                    s += handle_dict(value, indent + 1)
                else:
                    s += "  " * indent + f"{value._attribute_name}: {str(value)}\n"
            return s

        return f"{self._config_name}:\n" + handle_dict(self.get_settings_dict())