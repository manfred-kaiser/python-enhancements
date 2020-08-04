import inspect

from typing import (
    Any,
    Dict,
    Union,
    Text,
    Type,
    Tuple,
    Optional,
    List
)

from enhancements.config import ExtendedConfigParser


class MissingInnerResultClass(Exception):
    pass


class ReturnCodeMeta(type):

    def __new__(cls, name: Text, bases: Tuple[type], dct: Dict[str, Any]):
        x: Type['BaseReturnCode'] = super().__new__(cls, name, bases, dct)
        if 'Result' not in x.__dict__:
            raise MissingInnerResultClass()
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
        return x


class BaseReturnCode(metaclass=ReturnCodeMeta):

    config: ExtendedConfigParser
    CONFIGFILE: Optional[Text] = None

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

    def __init__(self, result: 'BaseReturnCode.Result', message: Optional[Union[Text, List[Text]]] = None, rawoutput: Optional[Text] = None) -> None:
        self._result: 'BaseReturnCode.Result' = result
        self.message = []
        if message:
            if isinstance(message, list):
                self.message.extend(message)
            else:
                self.message.append(message)
        self.rawoutput = rawoutput

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
            if result < value:
                result = value
        return result

    def set_result(self, value: 'BaseReturnCode.Result', force: bool = False):
        if self._result < value or force:
            self._result = value

    @classmethod
    def get_results(cls):
        return {int(getattr(cls, x)): getattr(cls, x) for x in cls.__dict__ if isinstance(getattr(cls, x), cls.Result)}

    @classmethod
    def get_result_types(cls):
        results = inspect.getmembers(cls, lambda a: isinstance(a, cls.Result))
        return [r[1].string for r in results]

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
