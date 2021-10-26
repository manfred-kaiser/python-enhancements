Context Manager
===============

Context managers in Python can be used to influence the execution of a script.

A detailed documentation of what a context manager is and how to create them can be found at: https://docs.python.org/3/library/contextlib.html

The Enhancmend library contains a collection of context managers that you can use in your programs.


Memory Limit
------------

With the Memory Limit Context Manager it is possible to influence the execution of a script in such a way,
that the code handled by the Contex Manager can be aborted as soon as more memory is required than specified.

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

With the ExceptionHandler it is possible to store exceptions and process them later.

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
