import os
from types import ModuleType
import pytest

from enhancements import examples
from enhancements.examples import ExampleModule, HexDump
from enhancements.exceptions import ModuleFromFileException
from enhancements.modules import (
    Module,
    _split_module_string,
    _load_module_from_string,
    _get_valid_module_class,
    get_module_class,
    ModuleParser,
    ModuleError
)


class NoModuleClass():
    pass


class ExampleSubModule(ExampleModule):
    CONFIG_PREFIX = 'Examples'


def test_split_module_string():
    # split package like modulename
    modname, funcname = _split_module_string('enhancements.examples.HexDump')
    assert modname == 'enhancements.examples'
    assert funcname == 'HexDump'
    # split filename like modulename
    modname, funcname = _split_module_string('{}:HexDump'.format(examples.__file__))
    assert os.path.basename(modname) == 'examples.py'
    assert funcname == 'HexDump'


def test_load_module_from_string_from_class():
    # load a module from a package name
    test_module = _load_module_from_string('enhancements.examples')
    assert isinstance(test_module, ModuleType)

    # try to load module from forbidden file
    with pytest.raises(ModuleFromFileException):
        _load_module_from_string(examples.__file__)

    # load module from allowed file
    test_module = _load_module_from_string(
        examples.__file__,
        modules_from_file=True
    )
    assert isinstance(test_module, ModuleType)


def test_get_valid_module_class():
    # load module class from package
    handlerclass = _get_valid_module_class(examples, 'HexDump')
    assert issubclass(handlerclass, Module)

    # try to load not existing class
    with pytest.raises(ModuleError):
        _get_valid_module_class(examples, 'NonExist')


def test_get_module_class():
    # load module from string
    modules = get_module_class('enhancements.examples.HexDump')
    assert issubclass(modules[0], Module)

    # load module from class
    modules2 = get_module_class(HexDump)
    assert issubclass(modules2[0], Module)

    # try to load empty module list
    modules = get_module_class(None)
    assert isinstance(modules, list)
    assert not modules

    # try to load invalid package and class
    assert not get_module_class(1234)


def test_module_parser():
    parser = ModuleParser(baseclass=ExampleModule)
    args = parser.parse_args(['-m', 'enhancements.examples.HexDump'])
    assert len(args.modules) == 2
    hex_dump_module = args.modules[1]
    assert issubclass(hex_dump_module, ExampleModule)
    assert hex_dump_module.PARSER._actions[0].dest == 'hexwidth'

    with pytest.raises(ValueError):
        ModuleParser(baseclass=NoModuleClass)

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        parser.parse_args(['--notvalid'])
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 2


def test_module():
    # test keyword arguments in constructor
    hex_dump = HexDump(hexwidth=10)
    assert isinstance(hex_dump, Module)
    # test wrong keyword argument name
    with pytest.raises(KeyError):
        HexDump(missing_arg=1)
    # test wrong keyword argument type
    with pytest.raises(ValueError):
        HexDump(hexwidth='wrong_type')
    assert HexDump.config_section == 'HexDump'
    assert ExampleSubModule.config_section == 'Examples:ExampleSubModule'


def test_sub_modules():
    HexDump.add_module(
        '--custom-module',
        dest='custom_module',
        default=ExampleSubModule
    )
    with pytest.raises(ModuleError):
        HexDump.add_module(
            '--custom-module2',
            dest='custom_module2',
            default=ExampleSubModule,
            baseclass=1
        )
