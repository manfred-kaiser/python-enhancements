ExtendedConfigParser
====================

Der ExtendedConfigParser ist ein erweitertet Python Config Parser (https://docs.python.org/3/library/configparser.html) und besitzt somit die gleichen Funktionen und Eigenschaften.

Darüberhinaus bietet der ExtendedConfigParser folgende zusätzlichen Funktionen, wie zum Beispiel Standardkonfigurationsdateien im Package und eine Produktionskonfiguration.


Standard Konfigurationsdatei
----------------------------

Der ExtendedConfigParser besitzt die Möglichkeit eine Standard Konfigurationsdatei
aus einem Package auszulesen. Wird kein Package angegeben wird das Package,
von dem aus der Config Parser aufgerufen wurde, verwendet.

.. code-block:: python

    from enhancements.config import ExtendedConfigParser

    config = ExtendedConfigParser()


Alternativ kann mit dem Parameter ``package`` ein bestimmtes Python Package für die Suche nach einer
Standard Konfigurationsdatei angegeben werden.

Ebenso können mit den Parametern ``productionconfig`` und ``defaultini`` alternaitve Konfigurationsdateien
für die Produktionsumgebung und als Standardkonfiguration verwendet werden.

Eine weitere Möglichkeit die Produktive Konfigurationsdatei anzugeben ist diese in der "default.ini" zu definieren:

.. code::

    [productionconfig]
    configpath = /etc/appname/production.ini

Es wird dann geprüft, ob die angegebene Datei existiert und geladen.
Sollte diese Datei nicht existieren, wird eine Warnung ausgegeben.


Zusätzliche Methoden des ExtendedConfigParser
---------------------------------------------

Der ExtendedConfigParser bietet folgende Methoden zusätzlich zu allen Methoden des Python Config Parsers an:

``copy``
~~~~~~~~

Mit der Methode ``copy`` kann ein ExtendedConfigParser kopiert werden um voneinander unabhängige ConfigParser Objekte zu erzeugen.

``append``
~~~~~~~~~~

Hilfsmethode für den ModuleParser, damit dieser über Kommandozeilenparameter Konfigurationsdateien laden kann.
``append`` kann als Alternative zu ``read`` verwendet werden.

.. warning::

    Bitte verwenden Sie die Methode ``append`` nur, wenn die Methode ``read`` für sie nicht
    in Frage kommt.

``getlist``
~~~~~~~~~~~

Mit ``getlist`` ist es Möglich eine Liste aus einer Konfigurationsdatei zu lesen.
Der Standard Python Config Parser bietet leider keine entsprechende Methode.

``getmodule``
~~~~~~~~~~~~~

Die Methode ``gemodule`` liefert ein Module zurück.

``getmodule`` kann sowohl auf einen Bereich (Section) als auch auf eine Option angewendet werden.

Bei der Verwendung als Option kann der Klassenname inkl. Pfad direkt zur Option hinzugefügt werden.

Soll ein Modul über einen Bereich (Section) geladen werden, muss dieser Bereich folgende Einträge aufweisen:

.. code-block::ini

    [MeinModul]
    class = package.Klasse
    enabled = True

.. note::

    Bitte beachten Sie, dass Sie eine Klasse und keine Instanz bekommen.
    Sie müssen sich um die Instanzierung des Moduls selber kümmern.


``getplugins``
~~~~~~~~~~~~~~

Ähnlich wie ``getmodule`` kann ``getplugins`` dazu verwendet werden Module zu laden.

``getplugins`` erwartet aber einen Präfix und liefert eine Liste der gefundenen Module zurück.

.. code-block::ini

    [Plugin:PluginName]
    class = package.PluginKlasse
    enabled = True
