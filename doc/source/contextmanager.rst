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


ExceptionHandler
----------------

Mit dem ExceptionHandler ist es möglich Exceptions zu speichern und diese später weiterzuverarbeiten.

.. code-block:: python

    from enhancements.contextmanager import ExceptionHandler

    try:
        with ExceptionHandler() as ex_handler:
            raise ValueError()
    except ValueError:
        print("cleanup after ValueError")
    finally:
        if ex_handler.exception_happened:
            print("raised exception: {}".format(ex_handler.exc_type.__name__))