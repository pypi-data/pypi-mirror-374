import abc
import inspect
from typing import Dict

from large_scale_deploy.tools.errors import ParseError


class StringRepr:

    def __repr__(self):
        return str(self)


class KeyValue(StringRepr, metaclass=abc.ABCMeta):

    def __init__(self, key: str, value: str):
        self.key = key
        self.value = value

    @classmethod
    @abc.abstractmethod
    def get_delimiter(cls) -> str:
        pass

    def __str__(self):
        return str(self.key) + self.get_delimiter() + str(self.value)

    @classmethod
    def parse(cls, src_str: str):
        parts = src_str.split(cls.get_delimiter())
        if len(parts) != 2:
            raise ParseError(f"String: {src_str} can't parse to key value by {cls.get_delimiter()}")
        return cls(parts[0], parts[1])


class Var(KeyValue):

    def __init__(self, option: str, value: str):
        super().__init__(option, value)
        self.option = option
        self.value = value

    @classmethod
    def get_delimiter(cls):
        return "="


class JsonDict(metaclass=abc.ABCMeta):

    @staticmethod
    def _is_json_dict_in_typing_list(instance, sign_class):
        return isinstance(instance, list) and \
            isinstance(getattr(sign_class, "__args__"), tuple) and \
            len(sign_class.__args__) == 1 and \
            issubclass(sign_class.__args__[0], JsonDict)

    @classmethod
    def from_json(cls, json_dict: Dict):
        sigs = inspect.signature(cls.__init__)
        args = []
        for arg_name, parameter in sigs.parameters.items():
            if arg_name == "self":
                continue
            value = json_dict.get(arg_name)
            if value is None:
                args.append(None)
                continue
            sign_class = parameter.annotation
            if isinstance(sign_class, type) and issubclass(sign_class, JsonDict):
                value = sign_class.from_json(value)
            elif cls._is_json_dict_in_typing_list(value, sign_class):
                value = [sign_class.__args__[0].from_json(item) for item in value]
            args.append(value)
        return cls(*args)

    def to_json(self):
        members = {}
        for key, value in vars(self).items():
            if key.startswith('__'):
                continue
            if isinstance(value, JsonDict):
                value = value.to_json()
            elif isinstance(value, list):
                new_value = []
                for item in value:
                    if isinstance(item, JsonDict):
                        new_value.append(item.to_json())
                    else:
                        new_value.append(item)
                value = new_value
            members[key] = value
        return members
