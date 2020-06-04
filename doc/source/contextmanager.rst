Context Manager
===============

Context Manager in Python können verwendet werden um die Ausführung eines Scriptes zu beeinflussen.

Eine ausführliche Dokumenation, was ein Context Manager ist und wie diese erstllt werden finden Sie unter: https://docs.python.org/3/library/contextlib.html

Die Enhancmend-Library beinhalten eine Sammlung an Context Managern, die sie in Ihren Programmen verwenden können.


Memory Limit
------------

Mit dem Memory Limit Context Manager ist es möglich die Ausführung eines Scriptes so zu beeinflussen,
dass der vom Contex Manager behandelte Code abgebrochen werden kann, sobald mehr Arbeitsspeicher benötigt wird als angegeben.

.. code-block:: python

    from enhancements.contextmanager import memorylimit

    with memorylimit(1 << 30): # 1 GB
        # read large file or do some other actions
        with open('large_file.csv') as f:
            content = f.readlines()
        return content
    return None


Time Limit
----------

Mit dem Time Limit Context Manager ist es möglich eine Aktion nach einer bestimmten Zeit zu beenden.
Dies kann sinnvoll sein, wenn eine bestimmte Ausführungszeit eingehalten werden muss oder Berechnungen automatisch abzubrechen,
wenn diese zu lange dauern.

Folgendes Beispiel gibt in einer Endlosschleife jede Sekunde ein "OK" aus.
Durch den Context Manager wird diese Schleife aber nach 10 Sekunden abgebrochen.

.. code-block:: python

    import time
    from enhancements.contextmanager import time_limit
    from enhancements.exceptions import ContextManagerTimeout

    try:
        # abbruch nach 10 sekunden
        with time_limit(10):
            while True:
                print("OK")
                time.sleep(1)
    except ContextManagerTimeout:
        print("Abgebrochen")


.. note::

    Eine Alternative zu dem "time_limit" Context Manager ist das Pyhton Package "stopit" (https://pypi.org/project/stopit/).
    Dieses bietet mehr Konfigurationsmöglichkeiten und funktioniert auch in Fällen,
    in denen der "time_limit" Context Manager nicht zuverlässig funktioniert.

    "stopit" kann mittels ``pip`` installiert werden:

    .. code-block:: bash

        pip install stopit
