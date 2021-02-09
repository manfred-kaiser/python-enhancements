Modul Entwicklung
=================

Mit dem ModuleParser ist es möglich Module zu laden, mit denen es möglich ist bestehende Appliaktionen zu erweitern.

Standardmäßig bieter der ModuleParser diese Möglichkeit nicht an. Um Module laden zu können, muss der ModuleParser entsprechend initialisiert werden.

.. note::

    Es  ist empfehlenswert, Die Klasse :class:`~enhancements.modules.Module` nicht direkt zu verwenden, sondern eine eigene Basisklasse für Module zu erstellen,
    von der dann alle Module erben können. Auf diese Weise kann man besser kontrollieren, welche Module geladen werden dürfen.

.. code-block:: python

    class MyModule(Module):

        def execute(self, data):
            raise NotImplementedError("execute method must be implemented")

Diese Klasse kann als Basisklasse beim ModuleParser angegeben werden. Dadurch ist es möglich die Module auf bestimmte Modultypen einzuschränken.
Um mehr als eine Basisklasse zu erlauben ist es möglich ein Tuple von Basisklassen anzugeben. Hierdurch ist es möglich Module unterschiedlicher Typen zu laden.

.. code-block:: python

    from enhancements.modules import Module, ModuleParser
    from mypkg.modules import MyModule

    def main():
        parser = ModuleParser(baseclass=MyModule, description='Module Example')


Neben der definition der Basisklassen kann auch ein Standardmodul geladen werden, das immer geladen werden soll.

.. note::

    Es ist zu beachten, dass dieses Modul immer geladen wird. Auch wenn andere Module geladen werden.
    Soll das Default-Modul ersetzt werden, kann dies mit dem Parameter ``replace_default=True`` angegeben werden.

Anschließend ist es möglich beim Programmstart Module zu übergeben. Diese können mit dem Parameter ``--module`` bzw. ``-m`` angegeben werden.


.. code-block:: bash

    myapp --module Module1


Es können auch mehrere Module angegeben werden. Diese werden in der angegebenen Reihenfolge ausgeführt.

.. code-block:: bash

    myapp -m Module1 -m Module2 -m Mdoule3


.. note::

   Es ist auch möglich, ein Modul mehrmals zu verwenden.


Module können aus einem PIP-Paket oder einer Python-Datei stammen.

Bei der Verwendung von PIP Paketen kann die Klasse wie unter Python üblich angegeben werden.

.. code-block:: bash

    myapp -m mymodule.MyModule

Alternativ ist es auch möglich ein Modul aus einer einzelnen Python-Datei zu verwenden.
In diesem Fall kann der absolute bzw. relative Pfad zur Datei angegeben werden,
Die Modul-Klasse kann durch einen ``:`` vom Dateinamen getrennt werden.

.. code-block:: bash

    myapp -m /home/user/function.py:MyModule

.. warning::

    Beachten Sie, dass beim Importieren eines Moduls der enthaltene Code ausgeführt wird.
    Bei Dateien, die als Scripte ausgeführt werden, kann dies dazu führen, dass das Script selber ausgeführt wird,
    was zu unvorhersehbaren Programmabläufen führen kann!

    Stellen Sie sicher, dass die Datei nur als Modul verwendet werden kann, oder falls diese auch als Script ausgeführt werden soll,
    dass diese folgende Überprüfung für den Script Teil beinhaltet:

    .. code-block:: python

        if __name__ == '__main__':

Entwicklung eigener Module
--------------------------

Module sind Python-Klassen die von :class:`~enhancements.modules.Module` abgeleitet sind.

Es ist ebenfalls möglich den Modulen Kommandozeilenparameter zu übergeben.
Diese Parameter können in der Methode :func:`~enhancements.modules.Module.parser_arguments` angegeben werden.

.. note::

    Die Module können nur auf die Argumente, die in der Methode ``parser_arguments`` definiert sind, zugreifen.
    Sollen Argumente verwendet werden, die von einem anderen Argument Parser stammen, verwendet werden,
    müssen diese in der ``__init__`` Methode übergeben werden.

Um ein Module zu erstellen ist es notwendig eine Basisklasse zu definieren, die die Schnittstellen des Moduls definiert.


Folgendes Beispiel zeigt ein HexDump Modul, das einen Parameter 'hexwidth' definiert.

.. code-block:: python

    # -*- coding: utf-8 -*-

    import binascii
    from enhancements.modules import Module

    class ExampleModule(Module):

        def execute(self, data):
            pass

    class HexDump(ExampleModule):

        @classmethod
        def parser_arguments(cls):
            cls.parser().add_argument(
                '--hexwidth',
                dest='hexwidth',
                type=int,
                default=16,
                help='width of the hexdump in chars'
            )

        def execute(self, data):
            if isinstance(data, str):
                data = bytes(data, 'UTF-8')
            result = []

            for i in range(0, len(data), self.args.hexwidth):
                s = data[i:i + self.args.hexwidth]
                hexa = list(map(''.join, zip(*[iter(binascii.hexlify(s).decode('utf-8'))]*2)))
                while self.args.hexwidth - len(hexa) > 0:
                    hexa.append(' ' * 2)
                text = ''.join([chr(x) if 0x20 <= x < 0x7F else '.' for x in  s])
                addr = '%04X:    %s    %s' % (i, " ".join(hexa), text)
                result.append(addr)

            print('\n'.join(result))


Dieses Module kann anschließend in einem eigenem Programm verwendet werden.
Folgendes Beispiel stellt ein einfaches Programm dar, mit dem eine Datei als Hex Dump ausgegeben werden kann.

.. note::

    Die Module werden nicht vom ModuleParser initalisiert! Dies muss in der Anwendung selber durchgeführt werden.
    Am einfachsten kann man die Module folgendermaßen initialisieren:

    .. code-block:: python

        modules = [module() for module in args.modules]

.. code-block:: python

    from enhancements.modules import ModuleParser
    from enhancements.examples import ExampleModule

    parser = ModuleParser(baseclass=ExampleModule, description='Module Example')
    parser.add_argument(
        'file',
    )
    args = parser.parse_args()

    modules = [module() for module in args.modules]

    if os.path.isfile(args.file):
        with open(args.file, 'rb') as hexfile:
            data = hexfile.read()
        for module in modules:
            module.execute(data)
    else:
        print("File not found")


Module erweitern
----------------

Neben dem ModuleParser kann auch ein Modul selber durch weitere Module erweitert werden.
Dies bietet den Vorteil, dass dadurch auch Module erweitert werden können und eine Anwendung
dadurch sehr modular gestaltet werden kann.

In folgendem Beispiel werden Basisklassen für Main-Module und für Sub-Module definiert um diese besser
voneinander trennen zu können.

Anschließend werden 2 Submodule (SubModule1, SubModule2) definiert, die dann dem MainModule1 zugewiesen werden können.

Module können sowohl dem ModuleParser als einem Modul zugewiesen werden. Hierfür wird die Methode "add_module" verwendet.

.. note::

    Es ist zu beachten, dass sich die Module um das initialisieren und ausführen der Module kümmern müssen.
    Theoretisch ist es auch möglich, dass die Submodule außerhalb eines Module initialisiert werden.
    Dies ist aber nicht zu empfehlen!

.. code-block:: python

    from enhancements.modules import Module, ModuleParser


    class MainModule(Module):

        def execute(self):
            pass

    class SubModule(Module):

        def execute(self):
            print("{} ausgeführt mit Parametern: {}".format(self.__class__, self.args))

    class SubModule1(SubModule):

        @classmethod
        def parser_arguments(cls):
            cls.parser().add_argument(
                '--value-1',
                dest='submodule_1_value',
                default=1,
                type=int,
                help='Value for sub module 1'
            )


    class SubModule2(SubModule):
        @classmethod
        def parser_arguments(cls):
            cls.parser().add_argument(
                '--value-2',
                dest='submodule_2_value',
                default=2,
                type=int,
                help='Value for sub module 2'
            )


    class MainModule1(MainModule):

        @classmethod
        def parser_arguments(cls):
            cls.add_module(
                '--submodule',
                dest='submodule',
                default=SubModule1,
                help='Submodule for main module',
                baseclass=SubModule
            )

        def execute(self):
            print(self.__class__)
            print(self.args)
            self.args.submodule().execute()


    def main():
        parser = ModuleParser(baseclass=MainModule, description='Module Example')
        args = parser.parse_args()
        modules = [module() for module in args.modules]
        for m in modules:
            m.execute()


Verwendung von Modulen im Code
------------------------------

Bisher wurde beschrieben, wie Module über die Kommandozeile mit Kommandozeilenparameter konfiguriert werden können.

Es kann aber auch vorkommen, dass ein Modul ohne die Verwendung von Kommandozeilenparametern verwendet werden soll.

Aus diesem Grund ist es möglich, dass man die entsprechenden Parameter beim Initialisieren der Klasse mitgeben kann.

Jeder Kommandozeilenparameter besitzt eine Eigenschaft ``dest``. Dieser wird als Name für den Parameter, der beim Initialisieren der Klasse
angegeben werden kann, verwendet.

Die Basisklasse für die Module erwartet 3 Parameter:

 * args = Kommandozeilenargumente als Array => Standard = None
 * namespace = Der Namespace, der für das Parsen verwendet werden soll
 * \*\*kwargs = Parameter, die anstelle der Kommandozeilenparameter verwendet werden sollen

Folgendes Beispiel zeigt, wie das ``SubModule1`` aus dem letzten Beispiel alleine verwendet werden kann:

.. code-block:: python

    m = SubModule1(submodule_1_value=15)
    m.execute()


.. warning::

    Bei der Verwenung von Modulen im Code ist darauf zu achten, dass die richtigen Datentypen verwendet werden.
    Sollte die Eigenschaft ``type`` gesetzt sein, prüft das Modul, ob der übergebene Wert diesem Datentyp entspricht.


Zusätzliche Parameter für die __init__-Methode
----------------------------------------------

Die __init__-Methode kann auch um eigene Parameter erweitert werden. In folgendem Beispiel wird die Klasse ``SubModule1`` um einen zusätzlichen Parameter
erweitert. Dieser ist sowohl bei der Verwendung mit Kommandozeilenparametern als auch bei der Verwendung im Code anzugeben.

.. code-block:: python

    class SubModule1(SubModule):

        def __init__(self, myval, args=None, namespace=None, **kwargs):
            super().__init__(args, namespace, **kwargs)
            print(myval)

        @classmethod
        def parser_arguments(cls):
            cls.parser().add_argument(
                '--value-1',
                dest='submodule_1_value',
                default=1,
                type=int,
                help='Value for sub module 1'
            )

    if __name__ == '__main__':
        m = SubModule1(1, submodule_1_value=15)
        m.execute()
