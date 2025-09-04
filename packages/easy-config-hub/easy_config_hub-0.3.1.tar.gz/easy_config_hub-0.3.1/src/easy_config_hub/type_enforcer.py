from typing import (
    Union,
    _UnionGenericAlias,
    TypeVar,
    Any,
    Generic,
    Sequence,
    Set,
    MutableSet,
    MutableSequence,
    Mapping,
    MutableMapping,
    get_origin,
    get_args,
)
from types import UnionType, GenericAlias


class GenericMissingError(Exception): ...


class TypeEnforcerMeta(type):
    def __new__(cls, name, bases, namespace):
        cls = super().__new__(cls, name, bases, namespace)
        cls._class_name = name
        return cls

T = TypeVar('T')    # For nuitka:2.7 (2.8dev)

class TypeEnforcer(Generic[T], metaclass=TypeEnforcerMeta):
    _first__class_getitem__was_called = False
    _enforcer_cur_type = None  # Last type that was used in Enforcer
    _cur_type = None  # Last type that was used in Enforcer
    _enforcer_generic_type = None  # Type that was used in Enforcer in subclass
    _generic_type = None  # Type that was used in Enforcer in subclass

    def __class_getitem__(cls, item):
        """
        Called when Enforcer is used as a generic class.
        It checks if the class is a subclass of Enforcer and if it has a generic type.
        If it does, it replaces the type variable with the given type.
        """
        if TypeEnforcer._does_have_generic(item):  # Set the current type
            TypeEnforcer._enforcer_generic_type = item
        else:
            TypeEnforcer._enforcer_cur_type = item

        if (
            cls._generic_type
        ):  # If class has _generic_type, means it is getting its type (Child[int])
            new_type = TypeEnforcer._replace_typevar_with_type(cls._generic_type, {T.__name__: item})   # TODO: proper mapping
            if TypeEnforcer._does_have_generic(new_type):  # Save for next class
                TypeEnforcer._enforcer_generic_type = new_type
            else:
                TypeEnforcer._enforcer_cur_type = new_type
                cls._cur_type = new_type

        return super().__class_getitem__(item)

    @staticmethod
    def _replace_typevar_with_type(gen_type, type_map: dict[TypeVar, type]):
        """
        Replaces the type variable with the given type in the given generic type.
        """
        origin = get_origin(gen_type)
        if not origin:
            if isinstance(gen_type, TypeVar):
                return type_map.get(gen_type.__name__, gen_type)
            return gen_type
        
        args = list(get_args(gen_type))
        for i, t in enumerate(get_args(gen_type)):
            if isinstance(t, TypeVar):
                args[i] = type_map.get(t.__name__, gen_type)
            elif isinstance(t, _UnionGenericAlias):  # If it's generic and union
                args[i] = TypeEnforcer._replace_typevar_with_type(t, type_map)
            elif isinstance(t, GenericAlias):  # If its generic
                args[i] = TypeEnforcer._replace_typevar_with_type(t, type_map)
            elif (
                isinstance(t, UnionType)
            ):  # Strange situation if it's generic union, but its type is just UnionType, str | dict[str | int, T]
                args[i] = TypeEnforcer._replace_typevar_with_type(t, type_map)

        if origin is UnionType:
            return Union[*args]
        else:
            return origin[*args]

    @staticmethod
    def _does_have_generic(type_):
        if isinstance(type_, TypeVar):
            return True
        args = list(get_args(type_))
        for t in args:
            if isinstance(type_, TypeVar) or TypeEnforcer._does_have_generic(t):
                return True
        return False

    def __init_subclass__(cls) -> None:
        """
        Called when a subclass is created.
        It sets the current type and the generic type for the subclass.
        """
        cls._generic_type = TypeEnforcer._enforcer_generic_type
        cls._cur_type = TypeEnforcer._enforcer_cur_type
        TypeEnforcer._enforcer_generic_type = None
        TypeEnforcer._enforcer_cur_type = None
        return super().__init_subclass__()

    def __init__(
        self,
        *values: T,
        name: str = "",
        strongly_typed: bool = True,
        try_parse_after_failure=False,
    ):
        if not self._cur_type:
            raise TypeError(
                f"Class {self._class_name} should contain generic type: {self._class_name}[type]"
            )
        self._type = self._cur_type
        self.__class__._cur_type = None

        self.values = values
        self._name = name
        self.is_strongly_typed = strongly_typed
        self.is_try_parse_after_error = try_parse_after_failure
        
        self._attribute_owner = None
        self._attribute_name = ''
        
        self.enforce()
        
    def enforce(self):
        self.values = [self.enforce_type_on_value(value, self._type) for value in self.values]
        
    def enforce_type_on_value(self, value, type_=None, strongly=None):
        strongly = strongly or self.is_strongly_typed
        type_ = type_ or self._type
        if strongly:
            parsed = self._check_type(value, type_)
            val = value
        else:
            parsed, val = self._parse_check_type(
                value, type_, self.is_try_parse_after_error
            )
        
        if parsed:
            if val is not None:
                return val
        else:
            if strongly:
                raise TypeError(
                    f"Value of {self.full_name} must be of type {type_}\n"
                    f"Given {type(value)}({repr(value)})"
                )
            else:
                raise TypeError(
                    f"Value of {self.full_name} must be of type {type_} or corresponding values must be able to convert into corresponding types.\n"
                    f"Unable to convert {type(value)}({repr(value)}) in type {type_}"
                )

    def __set_name__(self, owner, name):
        self._attribute_owner = owner
        self._attribute_name = name
        
    @property
    def full_name(self):
        if not self._attribute_name:
            return self._name if self._name else self._class_name
        else:
            return f'{self._attribute_owner.__qualname__}.{self._attribute_name}'
        
    @classmethod
    def _check_type(cls, value, type_) -> bool:
        """
        Checks if the value is of the given type.

        Args:
            `value`: The value to check.
            `type_`: The type to check against.

        Returns:
            True if the value is of the given type, False otherwise.
        """
        orig = get_origin(type_)
        args = get_args(type_)

        # Is simple type (aka int, str)
        if not orig:
            return isinstance(value, type_)

        # Is union (aka int | str)
        elif orig is UnionType or orig is Union or type(orig) is UnionType:
            return any(cls._check_type(value, arg) for arg in args)

        # Is complex type (aka dict[str, int], list[dict[str, str | int]])
        else:
            if isinstance(value, orig):
                if isinstance(value, list) or issubclass(
                    orig, (Sequence, MutableSequence, Set, MutableSet)
                ):
                    return all(map(lambda x: cls._check_type(x, args[0]), value))

                if isinstance(value, dict) or issubclass(
                    orig, (Mapping, MutableMapping)
                ):
                    return all(
                        map(lambda x: cls._check_type(x, args[0]), value.keys())
                    ) and all(
                        map(lambda x: cls._check_type(x, args[1]), value.values())
                    )

            else:
                return False

        raise TypeError(f"Type '{type_}' is not supported yet")

    @classmethod
    def _parse_check_type(
        cls, value, type_, ignore_error=False
    ) -> tuple[bool, T | Any]:
        """
        Attempts to parse a value to a specified type, supporting complex and union types.

        This method checks whether a given value can be parsed into the specified type.
        If the value is not of the specified type, it attempts to convert it. The method
        supports simple types, union types, sequences, set, and mappings. If the conversion
        is successful, it returns the parsed value; otherwise, it returns the failed value,
        see `ignore_error`.

        Args:
            `value`: The value to be checked and potentially parsed.
            `type_`: The target type to parse the value into.
            `ignore_error` (bool, optional): If set to True, the method will attempt to parse
                                        all elements in sequences and mappings even if
                                        parsing of one element fails. Defaults to False.

        Returns:
            A tuple where the first element is a boolean indicating if the parsing was
            successful, and the second element is the parsed value or the original value
            if parsing was unsuccessful.
        """

        try:
            if cls._check_type(value=value, type_=type_):
                return True, value
        except TypeError:
            pass
        
        orig = get_origin(type_)
        args = get_args(type_)

        # Is simple type (aka int, str)
        if not orig:
            if not isinstance(value, type_):
                try:
                    return True, type_(value)
                except (ValueError, TypeError):
                    return False, value
            return True, value

        # Is union (aka int | str)
        elif orig is UnionType or orig is Union or type(orig) is UnionType:
            for arg in args:
                parsed, v = cls._parse_check_type(value, arg, ignore_error)
                if parsed:
                    break
            return parsed, v

        # Is complex type (aka dict[str, int], list[dict[str, str | int]])
        else:
            if isinstance(value, orig):
                if is_list := isinstance(value, list) or issubclass(
                    orig, (Sequence, MutableSequence, Set, MutableSet)
                ):
                    result_list = []
                    parsed = True
                    for v in value:
                        values_parsed, val = cls._parse_check_type(
                            v, args[0], ignore_error
                        )
                        result_list.append(val)
                        if not values_parsed:
                            parsed = False
                            if not ignore_error:
                                break
                    return parsed, result_list if is_list else type(value)(result_list)

                if isinstance(value, dict) or issubclass(
                    orig, (Mapping, MutableMapping)
                ):
                    result_dict = {}
                    parsed = True
                    for k, v in value.items():
                        keys_parsed, key = cls._parse_check_type(
                            k, args[0], ignore_error
                        )
                        values_parsed, val = cls._parse_check_type(
                            v, args[1], ignore_error
                        )
                        result_dict[key] = val
                        if not keys_parsed or not values_parsed:
                            parsed = False
                            if not ignore_error:
                                break
                    return parsed, result_dict

            else:
                return False, value