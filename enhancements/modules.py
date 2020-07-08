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

from enhancements.classproperty import classproperty
from enhancements.exceptions import ModuleFromFileException


def _split_module_string(modulearg, moduleloader=None):
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


def _load_module_from_string(modname, modules_from_file=False):
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
    loader = importlib.machinery.SourceFileLoader(modname_file, modname)
    module = types.ModuleType(loader.name)
    loader.exec_module(module)
    return module


def _get_valid_module_class(module, funcname):
    """Prüfen, ob das angeforderte Modul existiert und gibt die Klasse zurück
    """
    handlerclass = getattr(module, funcname, None)
    # Prüfen, ob das angeforderte Modul eine Subklasse von Module ist
    if not handlerclass or not isinstance(handlerclass, type) or not issubclass(handlerclass, Module):
        logging.error("Module %s is not subclass of Module!", type(handlerclass))
        raise ModuleError()
    return handlerclass


def get_module_class(modulelist, moduleloader=None, modules_from_file=False):
    """Lädt eine Klasse anhand eines Strings.

    Dieser kann bei einem Modul, dass in einem PYthon Package vorhanden ist in folgender Form übergeben werden: **mymodule.MyModule**

    Alternativ kann auch ein Modul aus einer alleinstehenden Datei geladen werden: **/home/user/function.py:MyModule**
    """
    modules = []
    if not modulelist:
        return modules
    try:
        # Wurde keine Liste übergeben, wird "modulelist" in eine Liste umgewandelt, damit die Verarbeitung gleich ist
        modulelist = modulelist if isinstance(modulelist, list) else [modulelist]

        for modulearg in modulelist:
            if isinstance(modulearg, type) and issubclass(modulearg, Module):
                # Wenn bereits ein Modul übergeben wurd, wird dieses gleich der Ergebnisliste hinzugefügt
                modules.append(modulearg)
            else:
                modname, funcname = _split_module_string(modulearg, moduleloader)
                module = _load_module_from_string(modname, modules_from_file)
                handlerclass = _get_valid_module_class(module, funcname)
                if handlerclass:
                    modules.append(handlerclass)

    except ImportError:
        raise ModuleError
    except Exception:
        # in case of an exception delete all loaded modules
        # TODO: raise error instead of returning empty modules
        logging.exception("Unable to load module")
        del modules[:]
    return modules


def load_module(moduleloader=None):
    """Action, um Module mit der Methode "add_module" des ModuleParsers als Kommandozeilenparameter definieren zu können
    """
    class ModuleLoaderAction(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            values = get_module_class(values, moduleloader)
            setattr(args, self.dest, values[0] if values else None)
    return ModuleLoaderAction


def append_modules(moduleloader=None):
    """Action für den ModuleParser um Module als Kommanozeilen Parameter "--module" definieren zu können
    """
    class ModuleLoaderAppendAction(argparse._AppendAction):  # pylint: disable=W0212
        def __call__(self, parser, args, values, option_string=None):
            value_array = get_module_class(
                values, moduleloader,
                modules_from_file=parser.modules_from_file if hasattr(parser, 'modules_from_file') else False
            )
            for module in value_array:
                super(ModuleLoaderAppendAction, self).__call__(parser, args, module, option_string)
    return ModuleLoaderAppendAction


class ModuleError(Exception):

    def __init__(self, moduleclass=None, baseclass=None):
        super(ModuleError, self).__init__()
        self.moduleclass = moduleclass
        self.baseclass = baseclass


class _ModuleArgumentParser(argparse.ArgumentParser):
    """Enhanced ArgumentParser to suppress warnings and error during module parsing"""

    def error(self, message):
        """enhanced error function to suppress errors on python versions < 3.9"""
        if sys.version_info >= (3, 9):
            super().error(message)
        # fallback vor python versions < 3.9.x
        if not hasattr(self, 'exit_on_error') or not self.exit_on_error:
            return
        super().error(message)

    def parse_args(self, args=None, namespace=None, force_error=False):
        """parse_args with optional parameter 'force_error' to suppress errors while parsing args"""
        exit_on_error_stored = self.exit_on_error if sys.version_info >= (3, 9) else True
        self.exit_on_error = force_error
        ret = super().parse_args(args, namespace)
        self.exit_on_error = exit_on_error_stored
        return ret

    def parse_known_args(self, args=None, namespace=None, force_error=False):
        """parse_known_args with optional parameter 'force_error' to suppress errors while parsing args"""
        exit_on_error_stored = self.exit_on_error if sys.version_info >= (3, 9) else True
        self.exit_on_error = force_error
        ret = super().parse_known_args(args, namespace)
        self.exit_on_error = exit_on_error_stored
        return ret


class Module(metaclass=classproperty.meta):
    PARSER = None
    MODULES = None
    CONFIG_PREFIX = None

    def __init__(self, args=None, namespace=None, **kwargs):
        if not self.PARSER:
            self.prepare_module()
        self.args, _ = self.PARSER.parse_known_args(args, namespace)

        actions = {action.dest: action for action in self.PARSER._actions}
        for param_name, param_value in kwargs.items():
            action = actions.get(param_name)
            if not action:
                raise KeyError('keyword argument {} has no param'.format(param_name))
            if hasattr(action, 'type') and not isinstance(param_value, action.type):
                raise ValueError('Value {} for parameter is not an instance of {}'.format(param_value, action.type))
            setattr(self.args, param_name, param_value)

    @classmethod
    def add_module(cls, *args, **kwargs):
        # remove "baseclass" from arguments
        baseclass = kwargs.pop('baseclass', Module)
        if not inspect.isclass(baseclass) or not issubclass(baseclass, Module):
            logging.error('Baseclass %s mast be subclass of %s not %s', baseclass, Module, type(baseclass))
            raise ModuleError()
        # add "action" to new arguments
        kwargs['action'] = load_module()
        cls.MODULES.append((cls.PARSER.add_argument(*args, **kwargs), baseclass))

    @classmethod
    def parser_arguments(cls):
        pass

    @classmethod
    def prepare_module(cls):
        cls.MODULES = []
        cls.PARSER = _ModuleArgumentParser(add_help=False, description=cls.__name__)
        cls.parser_arguments()

    @classmethod
    def get_modules(cls):
        return cls.MODULES

    @classproperty
    def config_section(cls):  # pylint: disable=E0213
        if not cls.CONFIG_PREFIX:
            return cls.__name__
        return "{}:{}".format(cls.CONFIG_PREFIX, cls.__name__)


class ModuleParserPlugin(Module):
    pass


class ModuleParser(_ModuleArgumentParser):

    def __init__(self, default=(), baseclass=(), replace_default=False, modules_from_file=False, **kwargs):
        # check if baseclass is set and baseclasses is tuple or subclass of Module
        if not isinstance(baseclass, tuple) and (not inspect.isclass(baseclass) or not issubclass(baseclass, Module)):
            raise ValueError("baseclass must be tuple or subclass of Module")

        super(ModuleParser, self).__init__(add_help=False, **kwargs)
        self.modules_from_file = modules_from_file
        self.__kwargs = kwargs
        self._extra_modules = []
        self._module_parsers = {self}
        self._plugins = {}

        self.default_class = default if isinstance(baseclass, default) else (baseclass,)
        self.baseclasses = self._get_baseclasses(baseclass)

        if self.baseclasses:
            self.add_argument(
                '-m',
                '--module',
                dest='modules',
                action=append_modules(self),
                default=list(self.default_class) if self.default_class and not replace_default else [],
                help='Module to parse, modify data'
            )

    def _get_baseclasses(self, baseclass):
        # set default as baseclass if baseclass is not set
        _baseclasses = list(baseclass) if isinstance(baseclass, tuple) else [baseclass]
        if not _baseclasses and self.default_class:
            _baseclasses.extend(self.default_class)
        # self.baseclasses must be tuple, because issubclass requires tuple and not list
        baseclasses = tuple([bcls for bcls in _baseclasses if bcls])

        # check if all baseclasses are subclass of Module
        for bcls in baseclasses:
            if not isinstance(bcls, type) or not issubclass(bcls, Module):
                raise ModuleError('Baseclass mast be subclass of Module')
        if not baseclasses:
            logging.debug("modules are not supported")
        return baseclasses

    @property
    def parser(self):
        return self

    def add_plugin(self, plugin):
        if not inspect.isclass(plugin) or not issubclass(plugin, ModuleParserPlugin):
            raise ValueError("plugin must be a class and subclass of Module!")
        self._plugins[plugin] = None

    def add_parser(self, parser):
        for module_parser in self._module_parsers:
            if module_parser.description == parser.description:
                return
        # remove help action from parser
        parser._actions[:] = [x for x in parser._actions if not isinstance(x, argparse._HelpAction)]  # pylint: disable=W0212
        # append parser to list
        self._module_parsers.add(parser)

    def add_module(self, *args, **kwargs):
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
        kwargs['action'] = load_module(self)
        self._extra_modules.append((self.add_argument(*args, **kwargs), baseclass))
        logging.debug("Baseclass: %s", baseclass)

    def get_module_path(self, module):
        return module

    def get_sub_modules(self, parsed_args, args, namespace, modules, use_modules=False):
        moduleparsers = []
        if modules:
            if not use_modules:
                modulelist = [getattr(parsed_args, m[0].dest) for m in modules if hasattr(parsed_args, m[0].dest)]
                modulebasecls = [m[1] for m in modules]
            else:
                modulelist = [m for m in modules]
                modulebasecls = [self.baseclasses for m in modules]

            for module, baseclass in zip(modulelist, modulebasecls):
                if not issubclass(module, baseclass):
                    logging.error('module is not an instance of baseclass')
                    raise ModuleError(module, baseclass)
                if module is baseclass:
                    logging.error('module must not be baseclass!')
                    raise ModuleError(module, baseclass)
                module.prepare_module()
                moduleparsers.append(module.PARSER)

                try:
                    parsed_subargs, _ = module.PARSER.parse_known_args(args=args, namespace=namespace)
                    moduleparsers.extend(self.get_sub_modules(parsed_subargs, args, namespace, module.get_modules()))
                except TypeError:
                    logging.exception("Unable to load modules")
        return moduleparsers

    def _check_value(self, action, value):
        pass

    def _create_parser(self, args=None, namespace=None):
        parsed_args, _ = super().parse_known_args(args=args, namespace=namespace, force_error=True)

        # load modules from cmd args
        if self.baseclasses:
            for module in parsed_args.modules:
                if not issubclass(module, self.baseclasses):
                    raise ModuleError(module, self.baseclasses)
                if module is self.baseclasses:
                    raise ModuleError(module, self.baseclasses)
                module.prepare_module()
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
            plugin.prepare_module()
            self.add_parser(plugin.PARSER)

        # initialize plugins
        for plugin in self._plugins:
            self._plugins[plugin] = plugin(args)

        # create complete argument parser and return arguments
        parser = argparse.ArgumentParser(parents=self._module_parsers, **self.__kwargs)
        return parser

    def parse_args(self, args=None, namespace=None):
        parser = self._create_parser(args=args, namespace=namespace)
        return parser.parse_args(args, namespace)

    def parse_known_args(self, args=None, namespace=None):
        parser = self._create_parser(args=args, namespace=namespace)
        return parser.parse_known_args(args, namespace)
