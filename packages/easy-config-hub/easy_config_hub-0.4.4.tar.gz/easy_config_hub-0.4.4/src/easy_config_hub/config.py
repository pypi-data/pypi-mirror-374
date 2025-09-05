from __future__ import annotations
from pathlib import Path
import typing
import json
from .setting import SettingBase


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
        elif isinstance(value, SettingBase):
            target_cls._settings[key] = value


class ConfigBase(metaclass=ConfigMeta):
    """Base configuration class."""
    
    def __init__(self):
        self._nested_configs: dict[str, ConfigBase]
        self._settings: dict[str, SettingBase]
        
        for name, config_class in self._nested_configs.items():
            setattr(self, name, config_class)
    
    def get_all_configs(self) -> dict[str, ConfigBase]:
        return self._nested_configs
    
    def get_all_settings(self) -> dict[str, SettingBase]:
        return self._settings
        
    def to_dict(self) -> dict[str, typing.Any]:
        """Convert config to dictionary recursively."""
        result = {}

        # Process all attributes including inherited ones
        for key, value in vars(self.__class__).items():
            if key.startswith("_"):
                continue

            if isinstance(value, SettingBase):
                if value.level is not value.Level.READ_ONLY:
                    result[key] = value.to_dict()
            elif issubclass(value, ConfigBase):
                result[key] = value().to_dict()

        return result
    
    def from_dict(self, data: dict[str, dict]):
        for key, value in data.items():
            if s := self._settings.get(key):
                s.from_dict(value)
            elif c := self._nested_configs.get(key):
                c.from_dict(value)
        
        return self

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
    

class MainConfigBase(ConfigBase):
    def __init__(self, save_load_path: str | Path):
        super().__init__()
        self.save_load_path = Path(save_load_path)
        
        self.load()
    
    def load(self, file_path: str | Path=None):
        """Load config from JSON file.

        Args:
            file_path: Path to a JSON file. If not provided, will use the path provided to the constructor.
        """
        file_path = Path(file_path) if file_path else self.save_load_path
        if file_path.suffix:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            if not file_path.suffix == '.json':
                raise NameError('Config save/load file should be .json')
        
        else:
            file_path.mkdir(parents=True, exist_ok=True)
            file_path /= 'settings.json'
        
        if not file_path.exists():
            self.save(file_path)
            return self
        
        with file_path.open('r') as f:
            data = json.load(f)
        
        return self.from_dict(data)

    def save(self, file_path: str | Path=None) -> None:
        """Save config to JSON file."""
        file_path = Path(file_path) if file_path else self.save_load_path
        
        with file_path.open("w") as f:
            json.dump(self.to_dict(), f, indent=4)