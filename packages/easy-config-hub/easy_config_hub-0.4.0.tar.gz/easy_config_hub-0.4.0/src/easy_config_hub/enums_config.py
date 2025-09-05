from enum import Enum, Flag, auto
from .config import ConfigMeta


En = Enum
Fl = Flag
a = au = auto

class EnumsConfigMeta(ConfigMeta):
    def _at_class_creation(cls, target_cls, name): ...
    def _handle_key_value(cls, target_cls, key, value): ...
    
class EnumsConfig(metaclass=EnumsConfigMeta): ...