ReturnCode
==========

The ReturnCode class can be used to define ReturnCodes for programs or functions.

This class can be used to ensure that a ReturnCode is only changed if it has a higher priority,
than the already stored one.

By default, the new value is only set if the new value is greater than the current value.



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


The class must inherit from ``BaseReturnCode`` and have an inner class ``Result`` that inherits from ``BaseReturnCode.Result``.

The results must then use the derived Result class.

.. note::

    If the Result class is missing or the values do not use the derived class, an exception is thrown and the creation of the class is aborted.

    The reason for creating a derived Result class is to avoid accidentally using results from another Result class.
