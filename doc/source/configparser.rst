ExtendedConfigParser
====================

The ExtendedConfigParser is an extended Python Config Parser (https://docs.python.org/3/library/configparser.html) and has the same functions and features.

In addition, the ExtendedConfigParser offers the following additional functions, such as standard configuration files in the package and a production configuration.

Default configuration file
--------------------------

The ExtendedConfigParser has the possibility to read a standard configuration file from a package.
If no package is specified the package, from which the config parser was called is used.

.. code-block:: python

    from enhancements.config import ExtendedConfigParser

    config = ExtendedConfigParser()


Alternatively, the ``package`` parameter can be used to specify a specific Python package to search for a default configuration file.

Likewise, the parameters ``productionconfig`` and ``defaultini`` can be used to specify alternate configuration
files for the production environment and as default configuration.

Another possibility to specify the production configuration file is to define it in the "default.ini":

.. code::

    [productionconfig]
    configpath = /etc/appname/production.ini

If the specified file exists, it will be loaded.
If this file does not exist, a warning is issued.


Additional methods of the ExtendedConfigParser
---------------------------------------------

The ExtendedConfigParser provides the following methods in addition to all Python Config Parser methods:

``copy``
~~~~~~~~

With the ``copy`` method an ExtendedConfigParser can be copied to create independent ConfigParser objects.

``append``
~~~~~~~~~~

Auxiliary method for the ModuleParser to load configuration files via command line parameters.
``append`` can be used as an alternative to ``read``.


``getlist``
~~~~~~~~~~~

With ``getlist`` it is possible to read a list from a configuration file.

The standard Python config parser does not provide a corresponding method.

``getmodule``
~~~~~~~~~~~~~

The ``getmodule`` method returns a module.

``getmodule`` can be applied to both a section and an option.

When used as an option, the class name including path can be added directly to the option.

If a module is to be loaded via a section, this section must have the following entries:

.. code-block::ini

    [MeinModul]
    class = package.ModuleClass
    enabled = True

.. note::

It should be noted that ``getmodule`` returns a class and not an instance

The instantiation of the class must be done by the application itself.




``getplugins``
~~~~~~~~~~~~~~

Similar to ``getmodules``, ``getplugins`` can be used to load modules.

However, ``getplugins`` expects a prefix and returns a list of the modules found.

.. code-block::ini

    [Plugin:PluginName]
    class = package.PluginClass
    enabled = True
