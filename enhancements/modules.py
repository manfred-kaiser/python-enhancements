# -*- coding: utf-8 -*-

"""Module parsing library

Dieses Modul ist eine Erweiterung zum Standard-Argparse Modul, welches die Möglichkeit bietet
Klassen als Module zu laden.

Dieses Modul beinhaltet folgende öffentliche Klassen:

    - ModuleParser -- Einstiegspunkt um Kommandozeilenparameter zu parsen.
        Diese Klasse bietet die gleiche Funktionalität wie der ArgumentParser
        aus dem argparse Modul. Jedoch ist es möglich Module und Plugins anzugeben,
        die die Funktionalität des Parsers bzw. der Applikation erweitern
    - ModuleParserPlugin -- Basisklasse für Plugins.
        Diese Klasse dient als Basis für Plugins die die Funktionalität des ModuleParsers erweitern.
    - Module -- Basisklasse für Module, die in der Applikation verwendet werden können.
        Alle Module müssen von dieser Klasse abstammen. Stammt ein Modul nicht von dieser Klasse ab, kommt es zu
        einem ModuleError.
    - ModuleError -- Exception, die geworfen wird, wenn es beim initialisieren von Modulen oder Plugins zu Fehlern kommt.
        Diese Exception wird geworfen, wenn es zu einem Fehler gekommen ist. Details sind der Exception zu entnehmen.

Alle anderen Klassen und Funktionen in diesem Modul sind entweder aus Legacy Gründen vorhanden oder sind
implemntationsspezifisch und sollten in Produktivanwendungen nicht verwendet werden.
"""

import os
import sys
import types
import importlib
import logging
import argparse
import inspect
import traceback
from types import ModuleType
import pkg_resources

from typing import (
    Any,
    List,
    Optional, Sequence,
    Tuple,
    Dict,
    Type,
    Set,
    Text,
    Union
)

from enhancements.classproperty import classproperty, ClassPropertyMeta
from enhancements.exceptions import ModuleFromFileException


def _split_module_string(modulearg: Text, moduleloader: Optional['ModuleParser'] = None) -> Tuple[Text, Text]:
    """split a string in a module/path and the functionname

    >>> _split_module_string('enhancements.examples.ExampleModule')
    ('enhancements.examples', 'ExampleModule')
    >>> _split_module_string('enhancements.examples:ExampleModule')
    ('enhancements.examples', 'ExampleModule')
    """
    if moduleloader and isinstance(moduleloader, ModuleParser):
        # Wurde ein ModuleLoader übergeben, wird dieser verwendet, um den Pfad zum Modul zu bekommen
        modulearg = moduleloader.get_module_path(modulearg)
    # Modulname und Pfad werden voneinander getrennt
    modname, funcname = modulearg.rsplit(':' if ':' in modulearg else '.', 1)
    return modname, funcname


def _load_module_from_string(modname: Text, modules_from_file: bool = False) -> ModuleType:
    """Prüfen, ob das Modul von einem Package oder einer Datei geladen werden soll

    >>> type(_load_module_from_string('enhancements.examples'))
    <class 'module'>
    """
    if not os.path.isfile(modname):
        return importlib.import_module(modname)

    if not modules_from_file:
        raise ModuleFromFileException('loading a module from a file is not allowed')

    modname_file = 'enhanced_moduleloader_{}'.format(modname)
    if modname_file in sys.modules:
        logging.debug("using already imported module %s", modname_file)
        return sys.modules[modname_file]

    logging.warning('Loading modules from files is not recommended! Please use a python package instead.')
    loader = importlib.machinery.SourceFileLoader(modname_file, modname)  # type: ignore
    module: ModuleType = types.ModuleType(loader.name)
    loader.exec_module(module)
    return module


def _get_valid_module_class(module: ModuleType, funcname: Text) -> Type['Module']:
    """Prüfen, ob das angeforderte Modul existiert und gibt die Klasse zurück
    """
    handlerclass: Type['Module'] = getattr(module, funcname, None)
    # Prüfen, ob das angeforderte Modul eine Subklasse von Module ist
    if not handlerclass or not isinstance(handlerclass, type) or not issubclass(handlerclass, Module):
        logging.error("Module %s is not subclass of Module!", type(handlerclass))
        raise ModuleError()
    return handlerclass


def get_module_class(modulelist: Union[Type['Module'], Text, Sequence[Union[Text, Type['Module']]]], moduleloader: Optional['ModuleParser'] = None, modules_from_file: bool = False) -> List[Type['Module']]:
    """Lädt eine Klasse anhand eines Strings.

    Dieser kann bei einem Modul, dass in einem PYthon Package vorhanden ist in folgender Form übergeben werden: **mymodule.MyModule**

    Alternativ kann auch ein Modul aus einer alleinstehenden Datei geladen werden: **/home/user/function.py:MyModule**
    """
    modules: List[Type['Module']] = []
    if not modulelist:
        return modules
    try:
        # Wurde keine Liste übergeben, wird "modulelist" in eine Liste umgewandelt, damit die Verarbeitung gleich ist
        modulelist_it: Sequence[Union[Text, Type['Module']]]
        if not isinstance(modulelist, list):
            # type checking not possible with pep484 (https://github.com/python/typing/issues/256)
            modulelist_it = [modulelist]  # type: ignore
        else:
            modulelist_it = modulelist

        for modulearg in modulelist_it:
            if isinstance(modulearg, str):
                modname, funcname = _split_module_string(modulearg, moduleloader)
                files_allowed = modules_from_file or (moduleloader is not None and moduleloader.modules_from_file)
                module = _load_module_from_string(modname, files_allowed)
                handlerclass = _get_valid_module_class(module, funcname)
                if handlerclass:
                    modules.append(handlerclass)
            elif inspect.isclass(modulearg) and issubclass(modulearg, Module):
                # Wenn bereits ein Modul übergeben wurd, wird dieses gleich der Ergebnisliste hinzugefügt
                modules.append(modulearg)
            else:
                pass
    except ImportError:
        raise ModuleError
    except Exception:
        # in case of an exception delete all loaded modules
        raise ModuleError(message=traceback.format_exc())
    return modules


def load_module(moduleloader: Optional['ModuleParser'] = None, entry_point_name: Optional[str] = None) -> Type['argparse.Action']:
    """Action, um Module mit der Methode "add_module" des ModuleParsers als Kommandozeilenparameter definieren zu können
    """
    class ModuleLoaderAction(argparse.Action):
        def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace, values: Union[Text, Sequence[Any], None], option_string: Optional[Text] = None) -> None:
            if values:
                if entry_point_name:
                    entry_point_list = []
                    for entry_point in pkg_resources.iter_entry_points(entry_point_name):
                        entry_point_list.append(entry_point.name)
                        if entry_point.name == values:
                            values = entry_point.load()
                            break
                        if entry_point.module_name == values:
                            values = get_module_class(entry_point.module_name, moduleloader)
                            break
                    else:
                        try:
                            values = get_module_class(values, moduleloader)
                        except Exception:
                            raise argparse.ArgumentError(
                                self,
                                "Module '{}' not found! Valid modules are: {}".format(
                                    values,
                                    ", ".join(entry_point_list)
                                )
                            )
                else:
                    values = get_module_class(values, moduleloader)
                setattr(namespace, self.dest, values[0] if values else None)
    return ModuleLoaderAction


def append_modules(moduleloader: Optional['ModuleParser'] = None) -> Type['argparse._AppendAction']:
    """Action für den ModuleParser um Module als Kommanozeilen Parameter "--module" definieren zu können
    """
    class ModuleLoaderAppendAction(argparse._AppendAction):
        def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace, values: Union[Text, Sequence[Any], None], option_string: Optional[Text] = None) -> None:
            if values:
                value_array = get_module_class(
                    values, moduleloader,
                    modules_from_file=parser.modules_from_file if isinstance(parser, ModuleParser) else False
                )
                for module in value_array:
                    super().__call__(parser, namespace, module, option_string)  # type: ignore
    return ModuleLoaderAppendAction


class ModuleError(Exception):

    def __init__(
        self,
        moduleclass: Optional[Union[Type['Module'], Tuple[Type['Module'], ...]]] = None,
        baseclass: Optional[Union[Type['Module'], Tuple[Type['Module'], ...]]] = None,
        message: Optional[Text] = None
    ):
        super().__init__()
        self.moduleclass = moduleclass
        self.baseclass = baseclass
        self.message = message


class InvalidModuleArguments(Exception):
    pass


class _ModuleArgumentParser(argparse.ArgumentParser):
    """Enhanced ArgumentParser to suppress warnings and error during module parsing"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.exit_on_error = True

    def error(self, message: Text) -> None:  # type: ignore
        if self.exit_on_error:
            return
        super().error(message)


class Module(metaclass=ClassPropertyMeta):
    _parser: Optional[_ModuleArgumentParser] = None
    _modules: Optional[List[Tuple[argparse.Action, Any]]] = None
    CONFIG_PREFIX: Optional[Text] = None

    def __init__(self, args: Optional[Sequence[Text]] = None, namespace: Optional[argparse.Namespace] = None, **kwargs: Any) -> None:
        self.args: argparse.Namespace
        parser_retval = self.PARSER.parse_known_args(args, namespace)
        if parser_retval is None:
            raise InvalidModuleArguments()
        self.args, _ = parser_retval

        actions = {action.dest: action for action in self.PARSER._actions}
        for param_name, param_value in kwargs.items():
            action = actions.get(param_name)
            if not action:
                raise KeyError('keyword argument {} has no param'.format(param_name))
            # check if it is an instance of the argument type, ignore mypy error because of false positive
            if hasattr(action, 'type') and not isinstance(param_value, action.type):
                raise ValueError('Value {} for parameter is not an instance of {}'.format(param_value, action.type))
            setattr(self.args, param_name, param_value)

    @classmethod
    def add_module(cls, *args: Any, **kwargs: Any) -> None:
        # remove "baseclass" from arguments
        baseclass: Type[Module] = kwargs.pop('baseclass', Module)
        if not inspect.isclass(baseclass) or not issubclass(baseclass, Module):
            logging.error('Baseclass %s mast be subclass of %s not %s', baseclass, Module, type(baseclass))
            raise ModuleError()
        # add "action" to new arguments
        kwargs['action'] = load_module(entry_point_name=kwargs.get('dest'))
        if cls.MODULES is not None and cls.PARSER is not None:
            cls.MODULES.append((cls.PARSER.add_argument(*args, **kwargs), baseclass))

    @classmethod
    def parser_arguments(cls) -> None:
        pass

    @classproperty
    def MODULES(cls) -> List[Tuple[argparse.Action, Any]]:
        if '_modules' not in cls.__dict__ or cls._modules is None:
            cls._modules = []
        return cls._modules

    @classproperty
    def PARSER(cls) -> _ModuleArgumentParser:
        if '_parser' not in cls.__dict__:
            cls._parser = _ModuleArgumentParser(add_help=False, description=cls.__name__)  # type: ignore
            cls.parser_arguments()
        if not cls._parser:
            raise ValueError('failed to create ModuleParser for {}'.format(cls))
        return cls._parser

    @classproperty
    def config_section(cls) -> Text:  # pylint: disable=E0213
        if not cls.CONFIG_PREFIX:
            return cls.__name__  # type: ignore
        return "{}:{}".format(cls.CONFIG_PREFIX, cls.__name__)  # type: ignore


class ModuleParserPlugin(Module):
    pass


class ModuleParser(_ModuleArgumentParser):

    def __init__(
        self,
        default: Optional[Union[Type[Module], Tuple[Type[Module], ...]]] = None,
        baseclass: Optional[Union[Type[Module], Tuple[Type[Module], ...]]] = None,
        baseclass_as_default: bool = True,
        modules_from_file: bool = False,
        **kwargs: Any
    ) -> None:
        if baseclass is None:
            baseclass = ()

        # check if baseclass is set and baseclasses is tuple or subclass of Module
        if not isinstance(baseclass, tuple) and (not inspect.isclass(baseclass) or not issubclass(baseclass, Module)):
            raise ValueError("baseclass must be tuple or subclass of Module")

        super().__init__(add_help=False, **kwargs)
        self.modules_from_file: bool = modules_from_file
        self.__kwargs = kwargs
        self._extra_modules: List[Tuple[argparse.Action, type]] = []
        self._module_parsers: Set[argparse.ArgumentParser] = {self}
        self._plugins: Dict[Type[ModuleParserPlugin], Optional[Module]] = {}

        self.baseclasses: Tuple[Type[Module], ...] = self._get_baseclasses(baseclass)

        if default is None:
            default = self.baseclasses if baseclass_as_default else ()
        if not isinstance(default, tuple):
            default = (default, )
        self.default_class = list(default)

        if self.baseclasses:
            self.add_argument(
                '-m',
                '--module',
                dest='modules',
                action=append_modules(self),
                default=self.default_class,
                help='Module to parse, modify data'
            )

    def _get_baseclasses(self, baseclass: Union[Type[Module], Tuple[Type[Module], ...]]) -> Tuple[Type[Module], ...]:
        # set default as baseclass if baseclass is not set
        _baseclasses: List[Type[Module]] = list(baseclass) if isinstance(baseclass, tuple) else [baseclass]
        # self.baseclasses must be tuple, because issubclass requires tuple and not list
        baseclasses = tuple([bcls for bcls in _baseclasses if bcls])

        # check if all baseclasses are subclass of Module
        for bcls in baseclasses:
            if not isinstance(bcls, type) or not issubclass(bcls, Module):
                raise ModuleError(message='Baseclass mast be subclass of Module')
        if not baseclasses:
            logging.debug("modules are not supported")
        return baseclasses

    @property
    def parser(self) -> 'ModuleParser':
        return self

    def add_plugin(self, plugin: Type[ModuleParserPlugin]) -> None:
        if not inspect.isclass(plugin) or not issubclass(plugin, ModuleParserPlugin):
            raise ValueError("plugin must be a class and subclass of Module!")
        self._plugins[plugin] = None

    def add_parser(self, parser: argparse.ArgumentParser) -> None:
        for module_parser in self._module_parsers:
            if module_parser.description == parser.description:
                return
        # remove help action from parser
        parser._actions[:] = [x for x in parser._actions if not isinstance(x, argparse._HelpAction)]
        # append parser to list
        self._module_parsers.add(parser)

    def add_module(self, *args: Any, **kwargs: Any) -> None:
        # remove "baseclass" from arguments
        baseclass = kwargs.pop('baseclass', Module)
        for arg in args:
            if inspect.isclass(arg) and issubclass(arg, ModuleParserPlugin):
                logging.error('ModuleParserPlugin loaded as Module. please use add_plugin instead.')
                raise ModuleError(moduleclass=arg, baseclass=baseclass)
        if not inspect.isclass(baseclass) or not issubclass(baseclass, Module):
            logging.error('Baseclass %s mast be subclass of %s not %s', baseclass, Module, type(baseclass))
            raise ModuleError()
        # add "action" to new arguments
        kwargs['action'] = load_module(self, entry_point_name=kwargs.get('dest'))
        self._extra_modules.append((self.add_argument(*args, **kwargs), baseclass))
        logging.debug("Baseclass: %s", baseclass)

    def get_module_path(self, module: Text) -> Text:
        return module

    def get_sub_modules(
        self,
        parsed_args: argparse.Namespace,
        args: Optional[Sequence[Text]],
        namespace: Optional[argparse.Namespace],
        modules: Optional[List[Tuple[argparse.Action, Any]]],
        use_modules: bool = False
    ) -> List[argparse.ArgumentParser]:
        moduleparsers = []
        if modules:
            if not use_modules:
                modulelist = [getattr(parsed_args, m[0].dest) for m in modules if hasattr(parsed_args, m[0].dest)]
                modulebasecls = [m[1] for m in modules]
            else:
                modulelist = [m for m in modules]
                modulebasecls = [self.baseclasses for _ in modules]

            for module, baseclass in zip(modulelist, modulebasecls):
                if not issubclass(module, baseclass):
                    logging.error('module is not an instance of baseclass')
                    raise ModuleError(module, baseclass)
                if module is baseclass:
                    logging.error('module must not be baseclass!')
                    raise ModuleError(module, baseclass)
                moduleparsers.append(module.PARSER)

                try:
                    parsed_subargs, _ = module.PARSER.parse_known_args(args=args, namespace=namespace)
                    moduleparsers.extend(self.get_sub_modules(parsed_subargs, args, namespace, module.MODULES))
                except TypeError:
                    logging.exception("Unable to load modules")
        return moduleparsers

    def _check_value(self, action: Any, value: Any) -> None:
        pass

    def _create_parser(self, args: Optional[Sequence[Text]] = None, namespace: Optional[argparse.Namespace] = None) -> 'argparse.ArgumentParser':
        parsed_args_tuple = super().parse_known_args(args=args, namespace=namespace)
        if not parsed_args_tuple:
            self.exit_on_error = False
            super().parse_known_args(args=args, namespace=namespace)

        parsed_args, _ = parsed_args_tuple

        # load modules from cmd args
        if self.baseclasses:
            for module in parsed_args.modules:
                if not issubclass(module, self.baseclasses):
                    raise ModuleError(module, self.baseclasses)
                if module is self.baseclasses:
                    raise ModuleError(module, self.baseclasses)
                self.add_parser(module.PARSER)
                parsed_sub_args = module.PARSER.parse_known_args(args=args, namespace=namespace)
                submods = self.get_sub_modules(parsed_sub_args, args, namespace, parsed_args.modules, use_modules=True)
                for submod in submods:
                    self.add_parser(submod)

        # load modules from add_module method
        moduleparsers = self.get_sub_modules(parsed_args, args, namespace, self._extra_modules)
        for moduleparser in moduleparsers:
            self.add_parser(moduleparser)

        # load plugins
        for plugin in self._plugins:
            self.add_parser(plugin.PARSER)

        # initialize plugins
        for plugin in self._plugins:
            try:
                self._plugins[plugin] = plugin(args)
            except InvalidModuleArguments:
                logging.debug("Error Plugin init")
        # create complete argument parser and return arguments
        parser = argparse.ArgumentParser(parents=list(self._module_parsers), **self.__kwargs)
        return parser

    def parse_args(self, args: Optional[Sequence[Text]] = None, namespace: Optional[argparse.Namespace] = None) -> argparse.Namespace:  # type: ignore
        parser = self._create_parser(args=args, namespace=namespace)
        args_namespace = parser.parse_args(args, namespace)
        if not args_namespace:
            return argparse.Namespace()
        return args_namespace

    def parse_known_args(self, args: Optional[Sequence[Text]] = None, namespace: Optional[argparse.Namespace] = None) -> Tuple[argparse.Namespace, List[str]]:
        parser = self._create_parser(args=args, namespace=namespace)
        return parser.parse_known_args(args, namespace)
