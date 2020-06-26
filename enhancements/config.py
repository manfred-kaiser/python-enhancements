# -*- coding: utf-8 -*-


from configparser import SafeConfigParser, _UNSET
import inspect
import logging
import os
import pickle  # nosec
import pkg_resources

from enhancements.modules import get_module_class, Module


class DefaultConfigNotFound(Exception):
    pass


class ExtendedConfigParser(SafeConfigParser):

    def __init__(self, productionini=None, defaultini='default.ini', package=None, env_name='ENHANCED_CONFIG_FILE', modules_from_file=False):
        super(ExtendedConfigParser, self).__init__(allow_no_value=True)
        self.defaultini = defaultini
        self.package = package
        self.default_config = self._get_default_config()
        self.production_config = None
        self.configfiles = []
        self.modules_from_file = modules_from_file

        self._read_default_config()

        if productionini:
            self.production_config = productionini
        elif self.has_section('productionconfig') and self.has_option('productionconfig', 'configpath'):
            self.production_config = self.get('productionconfig', 'configpath')

        if env_name in os.environ:
            self.append(os.environ[env_name])

        if self.production_config:
            self.append(self.production_config)

    def _get_default_config(self):
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

        raise DefaultConfigNotFound()

    def _read_default_config(self):
        if self.default_config:
            logging.debug("Using default config: %s", self.default_config)
            self.append(self.default_config)

    def read(self, configpath):
        try:
            super(ExtendedConfigParser, self).read(configpath, encoding='utf-8')
        except Exception:
            logging.exception("error reading %s", configpath)

    def copy(self):
        """ create a copy of the current config
        """
        return pickle.loads(pickle.dumps(self))  # nosec

    def append(self, configpath):
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

    def getlist(self, section, option, sep=',', chars=None):
        return [chunk.strip(chars) for chunk in self.get(section, option).split(sep)]

    def _getmodule_option(self, section, option):
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

    def _getmodule_section(self, section):
        if not self.has_section(section):
            raise ValueError('Config section does not exist! Module not loaded.')
        if not self.has_option(section, 'enabled') or not self.has_option(section, 'class'):
            raise ValueError('Section is not a module section. Missing option enabled or class')
        if not self.getboolean(section, 'enabled'):
            return None
        return self.getmodule(section, 'class')

    def getmodule(self, section, option=None):
        if option:
            return self._getmodule_option(section, option)
        return self._getmodule_section(section)

    def getplugins(self, module_prefix):
        plugins = []
        if isinstance(module_prefix, (str, Module)) or issubclass(module_prefix, Module):
            module_prefix = module_prefix.CONFIG_PREFIX
        else:
            raise ValueError("Not a valid module prefix. Only strings and module are supported.")

        for section in self.sections():
            if section.startswith('{}:'.format(module_prefix)):
                if self.getboolean(section, 'enabled'):
                    plugins.append(self.getmodule(section, 'class'))
        return plugins

    def getboolean_or_string(self, section, option, *, raw=False, vars=None, fallback=_UNSET):
        try:
            return self.getboolean(section, option, raw=raw, vars=vars, fallback=fallback)
        except ValueError:
            return self.get(section, option, raw=raw, vars=vars, fallback=fallback)
