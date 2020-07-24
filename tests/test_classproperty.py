# type: ignore

import pytest
from enhancements.classproperty import classproperty


class TestClass(metaclass=classproperty.meta):

    _test_property = None

    @classproperty
    def name(cls):
        return cls.__name__

    @classproperty
    def test(cls):
        return cls._test_property

    @test.setter
    def test(cls, value):
        cls._test_property = value


class TestClassInvalid():

    @classproperty
    def name(cls):
        return cls.__name__


def test_classproperty():
    assert TestClass.name == TestClass.__name__
    assert TestClass.test is None
    TestClass.test = 1
    assert TestClass.test == 1


def test_classproperty_failed():
    with pytest.raises(TypeError):
        print(TestClassInvalid.name)
    with pytest.raises(AttributeError):
        TestClass.name = 1
