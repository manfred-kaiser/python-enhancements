# -*- coding: utf-8 -*-

from configparser import ConfigParser
import inspect
import logging
import os
import pickle  # nosec
import pkg_resources
from typing import (
    cast,
    Any,
    Optional,
    List,
    Union,
    Text,
    Type
)

from enhancements.modules import get_module_class, Module


class DefaultConfigNotFound(Exception):
    pass


class ExtendedConfigParser(ConfigParser):

    def __init__(
        self,
        productionini: Optional[Text] = None,
        defaultini: Text = 'default.ini',
        package: Optional[Text] = None,
        env_name: Text = 'ENHANCED_CONFIG_FILE',
        modules_from_file: bool = False,
        ignore_missing_default_config: bool = False
    ):
        super().__init__(allow_no_value=True)
        self.defaultini: Text = defaultini
        self.package: Optional[Text] = package
        self.ignore_missing_default_config: bool = ignore_missing_default_config
        self.default_config: Optional[Text] = self._get_default_config()
        self.production_config: Optional[Text] = None
        self.configfiles: List[Text] = []
        self.modules_from_file: bool = modules_from_file

        self._read_default_config()

        if productionini:
            self.production_config = productionini
        elif self.has_section('productionconfig') and self.has_option('productionconfig', 'configpath'):
            self.production_config = self.get('productionconfig', 'configpath')

        if env_name in os.environ:
            self.production_config = os.environ[env_name]

        if self.production_config:
            self.append(self.production_config)

    def _get_default_config(self) -> Optional[Text]:
        packages = []
        if self.package:
            packages.append(self.package)
        for frame in inspect.stack():
            frame_packagename = frame[0].f_globals['__name__'].split('.')[0]
            if frame_packagename != 'enhancements':
                packages.append(frame_packagename)
                break
        for packagename in packages:
            defaultconfig = pkg_resources.resource_filename(packagename, '/'.join(('data', self.defaultini)))
            if os.path.isfile(defaultconfig):
                return defaultconfig
        if not self.ignore_missing_default_config:
            raise DefaultConfigNotFound()
        logging.debug("mising default config")
        return None

    def _read_default_config(self) -> None:
        if self.default_config:
            logging.debug("Using default config: %s", self.default_config)
            self.append(self.default_config)

    def read(self, filenames: Any, encoding: Optional[Text] = 'utf-8') -> List[Text]:
        try:
            return super().read(filenames, encoding=encoding)
        except Exception:
            logging.exception("error reading %s", filenames)
            return []

    def copy(self) -> 'ExtendedConfigParser':
        """ create a copy of the current config
        """
        return cast('ExtendedConfigParser', pickle.loads(pickle.dumps(self)))  # nosec

    def append(self, configpath: Text) -> None:
        self.configfiles.append(configpath)
        if not configpath:
            return
        if os.path.isfile(configpath):
            logging.debug("using production configfile: %s", configpath)
            self.read(configpath)
        else:
            logging.warning(
                "production config file '%s' does not exist or is not readable.",
                configpath
            )

    def getlist(self, section: Text, option: Text, sep: Text = ',', chars: Optional[Text] = None) -> List[Text]:
        return [chunk.strip(chars) for chunk in self.get(section, option).split(sep) if chunk]

    def _getmodule_option(self, section: Text, option: Text) -> Type[Module]:
        """ get a module class from config file
        """
        module = self.get(section, option)
        values = get_module_class(module, modules_from_file=self.modules_from_file)
        if not values:
            raise ValueError(
                'Not a valid module class! section: {}, option: {}, value: {}'.format(
                    section,
                    option,
                    module
                )
            )
        return values[0]

    def _getmodule_section(self, section: Text) -> Optional[Type[Module]]:
        if not self.has_section(section):
            raise ValueError('Config section does not exist! Module not loaded.')
        if not self.has_option(section, 'enabled') or not self.has_option(section, 'class'):
            raise ValueError('Section is not a module section. Missing option enabled or class')
        if not self.getboolean(section, 'enabled'):
            return None
        return self.getmodule(section, 'class')

    def getmodule(self, section: Text, option: Optional[Text] = None) -> Optional[Type[Module]]:
        if option:
            return self._getmodule_option(section, option)
        return self._getmodule_section(section)

    def getplugins(self, module_prefix: Union[Text, Module, Type[Module]]) -> List[Type[Module]]:
        plugins = []
        if isinstance(module_prefix, str):
            pass
        elif isinstance(module_prefix, Module) or (inspect.isclass(module_prefix) and issubclass(module_prefix, Module)):
            if module_prefix.CONFIG_PREFIX:
                module_prefix = module_prefix.CONFIG_PREFIX
            else:
                raise ValueError("Not a valid module prefix. Only strings and module are supported.")
        else:
            raise ValueError("Not a valid module prefix. Only strings and module are supported.")

        for section in self.sections():
            if section.startswith('{}:'.format(module_prefix)):
                if self.getboolean(section, 'enabled'):
                    module = self.getmodule(section, 'class')
                    if module:
                        plugins.append(module)
        return plugins

    def getboolean_or_string(self, section: Text, option: Text) -> Union[bool, Text]:
        try:
            return self.getboolean(section, option)
        except ValueError:
            return self.get(section, option)
