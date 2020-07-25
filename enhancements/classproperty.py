"""
To use simply copy ClassPropertyMeta and classproperty into your project
"""
from typing import (
    Any,
    Callable,
    Text,
    Optional,
    Union
)


class ClassPropertyMeta(type):
    def __setattr__(self, key: Text, value: Any) -> None:
        obj = self.__dict__.get(key, None)
        if isinstance(obj, classproperty):
            return obj.__set__(self, value)
        return super().__setattr__(key, value)


class classproperty():
    """
    Similar to @property but used on classes instead of instances.
    The only caveat being that your class must use the
    classproperty.meta metaclass.
    Class properties will still work on class instances unless the
    class instance has overidden the class default. This is no different
    than how class instances normally work.
    Derived from: https://stackoverflow.com/a/5191224/721519

    .. code-block:: python

        class Z(object, metaclass=classproperty.meta):
            @classproperty
            def foo(cls):
                return 123
            _bar = None
            @classproperty
            def bar(cls):
                return cls._bar
            @bar.setter
            def bar(cls, value):
                return cls._bar
        Z.foo  # 123
        Z.bar  # None
        Z.bar = 222
        Z.bar  # 222
    """

    meta = ClassPropertyMeta

    def __init__(self, fget: Callable[..., Any], fset: Optional[Callable[..., None]] = None) -> None:
        self.fget: Union[Callable[..., Any], staticmethod, classmethod] = self._fix_function(fget)
        self.fset: Optional[Union[Callable[..., None], staticmethod, classmethod]] = None if fset is None else self._fix_function(fset)

    def __get__(self, instance: Any, owner: Optional[ClassPropertyMeta] = None) -> Any:
        if not issubclass(type(owner), ClassPropertyMeta):  # type: ignore
            raise TypeError(
                f"Class {owner} does not extend from the required "
                f"ClassPropertyMeta metaclass"
            )
        return self.fget.__get__(None, owner)()  # type: ignore

    def __set__(self, owner: ClassPropertyMeta, value: Any) -> Any:
        if not self.fset:
            raise AttributeError("can't set attribute")
        if not isinstance(owner, ClassPropertyMeta):  # type: ignore
            owner = type(owner)
        return self.fset.__get__(None, owner)(value)  # type: ignore

    def setter(self, fset: Callable[..., Any]) -> 'classproperty':
        self.fset = self._fix_function(fset)
        return self

    _fn_types = (type(__init__), classmethod, staticmethod)

    @classmethod
    def _fix_function(cls, fn: Callable[..., Any]) -> Union[Callable[..., Any], classmethod, staticmethod]:
        if not isinstance(fn, cls._fn_types):
            raise TypeError("Getter or setter must be a function")
        # Always wrap in classmethod so we can call its __get__ and not
        # have to deal with difference between raw functions.
        if not isinstance(fn, (classmethod, staticmethod)):
            return classmethod(fn)
        return fn
