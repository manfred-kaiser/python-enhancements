ModuleParser
============

Das Enhancements-Package bietet ein Modulsystem, das sehr einfach in Python Anwendungen integriert werden kann.

Durch das Modulsystem ist es möglich über Kommandozeilenparameter eigene Module zu laden.

Dieses Modulsystem kann darüberhinaus mit Plugins erweitert werden, um zusätzliche Funktionen hinzuzufügen.

Ebenso ist es möglich über den ModuleParser Kommandozeilenparameter anzugeben.
Hierfür können die gleichen Parameter wie bei `argparse <https://docs.python.org/3/library/argparse.html>`_ verwendet werden.


Unterschied Modul und Plugin
----------------------------

Der ModuleParser kann Module und Plugins laden. Der Unterschied zwischen Modulen und Plugins ist, dass Plugins
die Funktionalität des ModuleParsers erweitert und Module die Applikation, die den ModuleParser einbindet.


Erstellen eines ModuleParser
----------------------------

Folgendes Beispiel erstellt erstellt einen ModuleParser und fügt Kommandoozeilenargumente hinzu.

In diesem Beispiel soll ein einfacher CLI Client erstellt werden, über den es möglich ist HTTP Anfragen zu senden.

.. code:: python

    # -*- coding: utf-8 -*-

    import requests
    from enhancements.modules import ModuleParser

    parser = ModuleParser(description='Simple HTTP Client')

    parser.add_argument(
        'method',
        action='store',
        choices=['get', 'post'],
        help='HTTP Method'
    )

    parser.add_argument(
        'url',
        action='store',
        help='URL to open'
    )

    args = parser.parse_args()

    if args.method == 'get':
        response = requests.get(args.url)
    else:
        response = requests.post(args.url)

    print("Status: {}".format(response.status_code))


Dieses Beispiel unterscheidet sich, bis auf die Verwendung des ModuleParsers nicht von einem Programm
das den ArgumentParser aus dem argparse-Module verwendet.

Plugins des ModuleParsers
-------------------------

Derzeit gibt es zwei Plugins für den ModuleParser.
Mit diesen ist es möglich ein Logging zur Applikation hinzuzufügen und Standardkonfigurationsdateien zu verwenden.

Die Konfiguration eines Plugins erfolgt über Klassen Eigenschaften. Um ein Plugin zu laden wird die Klasse übergeben.

Logging-Plugin
^^^^^^^^^^^^^^

Das Config Plugin kann über die Klasse  ``enhancements.plugins.LogModule`` eingebunden werden.

Das Logging Plugin konfiguriert das Python Logging Module, so dass Meldungen ab Info angezeigt werden.
Um auch Debug Meldungen zu sehen wird ein Kommandozeilenparameter ``-d`` bzw. ``--debug`` hinzugefügt.

Ebenso wird ein Parameter ``--logfile`` hinzugefügt, mit dem es möglich ist eine Datei anzugeben, in die das Log geschrieben werden soll.

Das Logging-Plugin kann so konfiguriert werden, das standardmäßig immer eine Logdatei geschrieben wird. In diesem Fall kann der Parameter ``--logfile``
dazu verwendet werden um das Log in eine andere Datei zu schreiben. Für den Fall das keine Logdatei erstellt werden soll kann der Parameter ``--no-logfile`` verwendet werden.

.. code:: python

    # -*- coding: utf-8 -*-

    import logging
    from enhancements.modules import ModuleParser
    from enhancements.plugins import LogModule

    parser = ModuleParser(description='Logging Example')

    # optionale Konfiguration der Logdatei
    LogModule.LOGFILE = '/var/log/example.log'

    parser.add_plugin(LogModule)

    args = parser.parse_args()

    logging.debug("Das ist eine Debug Meldung")
    logging.info("Das ist eine Info Meldung")


Config-Plugin
^^^^^^^^^^^^^^

Das Config Plugin kann über die Klasse  ``enhancements.plugins.ConfigModule`` eingebunden werden.

Mit diesem Plugin ist es möglich Konfigurationsdateien für Applikationen zu verwalten. Dieses Plugin basiert auf dem Python ConfigParser Modul,
erweitert dieses jedoch um die Möglichkeit eine Standardkonfiguration im Package der Applikation zu hinterlegen.

Darüberhinaus ist es möglich Module über die Konfigurationsdatei zu laden.

Auf die Konfigurationsdatei kann über die geparsten Kommandozeilenargumente über ``.config`` zugegriffen werden.
Hierbei ist das ConfigParser Objekt direkt verfügbar.


.. note::

    Um folgendes Beispiel zu testen, erstellen Sie ein neues Package.
    Das Config-Plugin ist nicht dafür gedacht ausserhalb eines Packages
    verwendet zu werden.


Erstellen Sie in Ihrem Package ein Konfiguration in die Datei ``data/default.ini``.

.. code:: ini

    [productionconfig]
    configpath = /etc/appname/production.ini

    [network]
    ip = 192.168.0.1

In der Datei ``cli.py`` fügen Sie folgenden Code ein:

.. code:: python

    # -*- coding: utf-8 -*-

    from enhancements.modules import ModuleParser
    from enhancements.plugins import ConfigModule

    def main():
        parser = ModuleParser(description='Config Example')

        parser.add_plugin(ConfigModule)

        args = parser.parse_args()

        print(args.config.get('network', 'ip'))

Nachdem das Package erstellt wurde, können Sie dieses installieren und das entsprechende CLI Tool ausführen.

In der Konfigurationsdatei des Packages wurd eine Bereich mit dem Namen ``[productionconfig]`` und dem Schlüssel ``configpath`` definiert.
Diese Konfiguration ist optional. Wird diese angegeben, wird geprüft, ob diese Datei existiert und geladen.

.. note::

    In der Production-Konfigurationsdatei müssen nur die Werte angegeben werden, die sich von der Standard-Konfiguratinsdatei des Packages unterscheiden.
