ReturnCode
==========

Die Klasse ReturnCode kann verwendet werden, um ReturnCodes für Programme oder Funktionen zu definieren.

Mit dieser Klasse kann sichergestellt werden, dass ein ReturnCode nur dann geändert wird, wenn dieser eine höhere Priorität besitzt,
als der bereits gepeicherte.

Standardmäßig wird der neue Wert nur dann gesetzt, wenn der neue Wert größer ist, als der aktuelle Wert.



Beispiel
------------

.. code-block:: python

    from enhancements.returncode import BaseReturnCode

    class CustomScanResult(BaseReturnCode):
        class Result(BaseReturnCode.Result):
            pass

        Success = Result('success', 10)
        Skip = Result('skip', 11, skip=True)
        Error = Result('error', 12)


Die Klasse muss von ``BaseReturnCode`` erben und eine innere Klasse ``Result`` besitzen, die von ``BaseReturnCode.Result`` erbt.

Die Ergebnisse müssen dann die abgeleitete Result Klasse verwenden.

.. note::

    Sollte die Result Klasse fehlen oder die Werte nicht die abgeleiteten Klasse verwenden, wird eine Exception geworfen und die Erstellung
    der Klasse wird abgebrochen.

    Der Grund für das Erstellen einer abgeleiteten Result Klasse ist, dass nicht ausversehen Ergebnisse von einer anderen Result Klasse verwendet werden.
