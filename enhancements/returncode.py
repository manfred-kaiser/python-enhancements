import operator
from typing import (
    Any,
    Callable,
    Dict,
    Text,
    Type,
    Tuple,
    Optional
)

from enhancements.config import ExtendedConfigParser


class MissingInnerResultClass(Exception):
    pass


class WrongResultSubclass(Exception):
    pass


class WrongResultValue(Exception):
    pass


class ReturnCodeMeta(type):

    def __new__(cls, name: Text, bases: Tuple[type], dct: Dict[str, Any]):
        x: Type['BaseReturnCode'] = super().__new__(cls, name, bases, dct)
        if 'Result' not in x.__dict__:
            raise MissingInnerResultClass('{} must have a inner Result class'.format(x.__name__))
        result_basesclasses = [b.__qualname__ for b in x.Result.__bases__]
        if 'BaseReturnCode.Result' not in result_basesclasses and 'int' not in result_basesclasses:
            raise WrongResultSubclass()
        x.Result.BASERESULT = x
        if x.CONFIGFILE:
            configfile = ExtendedConfigParser(defaultini=x.CONFIGFILE)
            x.config = configfile
            for section in configfile.sections():
                if not section.startswith('Result:'):
                    continue

                result_name = section.split(':', 1)[1]
                result_value: 'BaseReturnCode.Result' = x.Result(
                    result_name,
                    configfile.getint(section, 'value'),
                    configfile.getboolean(section, 'skip')
                )
                setattr(x, result_name.capitalize(), result_value)
                setattr(x, result_name.lower(), x.Action(x, result_value))
        baseclass_dict = {b.__qualname__: b for b in x.__bases__}
        baseclass: Optional[Type['BaseReturnCode']] = baseclass_dict.get('BaseReturnCode', None)
        if baseclass:
            for r in [a for a in x.__dict__.values() if isinstance(a, baseclass.Result)]:
                if not isinstance(r, x.Result):
                    raise WrongResultValue()
        return x


class BaseReturnCode(metaclass=ReturnCodeMeta):

    config: ExtendedConfigParser
    CONFIGFILE: Optional[Text] = None
    COMPERATOR: Callable[[Any, Any], bool] = operator.gt

    class Action():
        def __init__(self, cls: Type['BaseReturnCode'], result: 'BaseReturnCode.Result') -> None:
            self.cls: Type['BaseReturnCode'] = cls
            self.result: 'BaseReturnCode.Result' = result

        def __call__(self) -> 'BaseReturnCode':
            return self.cls(self.result)

    class Result(int):

        BASERESULT: Optional[Type['BaseReturnCode']] = None

        def __init__(self, name: Text, value: int, skip: bool = False):
            super().__init__()
            self.string: Text = name
            self.skip: bool = skip

        def __new__(cls, name: Text, value: int, skip: bool = False, *args: Any, **kwargs: Any) -> 'BaseReturnCode.Result':
            result: 'BaseReturnCode.Result' = super().__new__(cls, value)  # type: ignore
            result.string = name
            result.skip = skip
            return result

        def __str__(self):
            return self.string

        def __hash__(self):
            return int(self)

        def __eq__(self, other: Any) -> bool:
            return super().__eq__(self.convert(other))

        def __ne__(self, other: Any) -> bool:
            return super().__ne__(self.convert(other))

        def __lt__(self, other: Any) -> bool:
            return super().__lt__(self.convert(other))

        def __gt__(self, other: Any) -> bool:
            return super().__gt__(self.convert(other))

        def __le__(self, other: Any) -> bool:
            return super().__le__(self.convert(other))

        def __ge__(self, other: Any) -> bool:
            return super().__ge__(self.convert(other))

        @classmethod
        def convert(cls, value: Any) -> 'BaseReturnCode.Result':
            if not cls.BASERESULT:
                raise ValueError('Class not configured')
            return cls.BASERESULT.convert(value)

    def __init__(self, result: 'BaseReturnCode.Result') -> None:
        self._result: 'BaseReturnCode.Result' = self.convert(result)

    @property
    def result(self) -> 'BaseReturnCode.Result':
        return self._result

    @result.setter
    def result(self, value: 'BaseReturnCode.Result') -> None:
        self.set_result(value)

    @classmethod
    def min(cls) -> 'BaseReturnCode.Result':
        return cls.convert(min(cls.get_results().keys()))

    @classmethod
    def max(cls) -> 'BaseReturnCode.Result':
        return cls.convert(max(cls.get_results().keys()))

    @classmethod
    def get_score(cls, *returnvalues: 'BaseReturnCode.Result') -> 'BaseReturnCode.Result':
        if cls.CONFIGFILE:
            result = cls.convert(cls.config.get('Result', 'initial'))
        else:
            result = cls.min()
        for value_arg in returnvalues:
            value: 'BaseReturnCode.Result' = cls.convert(value_arg)
            if value.skip:
                continue
            if cls._compare(value, result):
                result = value
        return result

    @classmethod
    def _compare(cls, a: Any, b: Any) -> bool:
        return cls.COMPERATOR(a, b)

    def set_result(self, value: 'BaseReturnCode.Result', force: bool = False) -> bool:
        if self._compare(value, self._result) or force:
            new_value = self.convert(value)
            if new_value.skip and not force:
                return False
            self._result = new_value
            return True
        return False

    @classmethod
    def get_results(cls):
        return {int(x): x for x in cls.__dict__.values() if isinstance(x, cls.Result)}

    @classmethod
    def get_result_types(cls):
        return [x.string for x in cls.__dict__.values() if isinstance(x, cls.Result)]

    @classmethod
    def convert(cls, value: Any) -> 'BaseReturnCode.Result':
        results = cls.get_results()
        if isinstance(value, cls.Result):
            return value
        elif isinstance(value, int):
            if value in results:
                return results[value]
        elif isinstance(value, str):
            for rating, result in results.items():
                if value.lower() == result.string.lower():
                    return results[rating]
        raise ValueError("Not a valid return code")
