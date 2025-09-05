from __future__ import annotations
import sys
import os
from pathlib import Path
from .config import ConfigMeta



# I take the main directory, check for child classes, save child classes and initialize them in init
# Do for each dir

def _get_set_std_dir():
    if getattr(sys, 'frozen', False):   # executable mode
        STD_DIR = Path(sys.argv[0]).parent
        print(f'Exe detected, working directory: {STD_DIR}')
    else:   # normal Python environment
        STD_DIR = Path(sys.argv[0]).parent
    STD_DIR = STD_DIR.absolute()
    os.chdir(STD_DIR)
    return STD_DIR

class DirConfigMeta(ConfigMeta):
    STD_DIR: Path = _get_set_std_dir()
    
    def _at_class_creation(cls, target_cls, name):
        target_cls._nested_classes = {}
        target_cls._to_path = {}
    
    def _handle_key_value(cls, target_cls, key, value):
        if isinstance(value, type) and issubclass(value, DirConfigBase):
            target_cls._nested_classes[key] = value
        elif isinstance(value, Path):
            setattr(target_cls, key, value)
        elif isinstance(value, str) and value not in ['__main__', cls.__module__, __file__, target_cls.__name__]:
            target_cls._to_path[key] = value
        elif isinstance(value, ConfigMeta):
            raise Exception('Only Dir configs are allowed')
        

class StdDirConfigBase(metaclass=DirConfigMeta):
    def __init__(self):
        self.STD_DIR = self.__class__.__class__.STD_DIR
        for name, dir_config in self._nested_classes.items():
            instance = dir_config(self.STD_DIR)
            setattr(self.__class__, name, instance)
            
        for name, path_str in self._to_path.items():
            path: Path = self.STD_DIR / path_str
            if path.suffix:
                path.parent.mkdir(exist_ok=True, parents=True)
            else:
                path.mkdir(exist_ok=True, parents=True)
                
            setattr(self.__class__, name, path)
        
    def to_str(self, tabs) -> str:
        s = f"{self._config_name} ({self.STD_DIR}):\n"
        for key, value in self.__class__.__dict__.items():
            if isinstance(value, Path):
                s += f'{'  '*tabs}{key}: {value}\n'
            if isinstance(value, DirConfigBase):
                s += '\n'
                s += '  '*tabs + value.to_str(tabs+1)
        return s
    
class DirConfigBase(metaclass=DirConfigMeta):
    def __init__(self, parent_dir: Path):
        self.parent_dir = parent_dir
        self.dir: Path = parent_dir / self._config_name.lower()
        
        for name, dir_config in self._nested_classes.items():
            instance = dir_config(self.dir)
            setattr(self.__class__, name, instance)
            
        for name, path_str in self._to_path.items():
            path: Path = self.dir / path_str
            if path.suffix:
                path.parent.mkdir(exist_ok=True, parents=True)
            else:
                path.mkdir(exist_ok=True, parents=True)
                
            setattr(self.__class__, name, path)
            
    def to_str(self, tabs) -> str:
        s = f"{self._config_name} ({self.dir}):\n"
        for key, value in self.__class__.__dict__.items():
            if isinstance(value, Path):
                s += f'{'  '*tabs}{key}: {value}\n'
            if isinstance(value, DirConfigBase):
                s += '  '*tabs + value.to_str(tabs+1)
        return s
    
    def __truediv__(self, other) -> Path:
        path = self.dir / other
        if path.suffix:
            path.parent.mkdir(exist_ok=True, parents=True)
        else:
            path.mkdir(exist_ok=True, parents=True)
        return path