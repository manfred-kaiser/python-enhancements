# -*- coding: utf-8 -*-

import contextlib
import resource
import traceback
from typing import Any, Iterator, Text


@contextlib.contextmanager
def memorylimit(limit: int, restype: int = resource.RLIMIT_AS) -> Iterator[None]:
    soft_limit, hard_limit = resource.getrlimit(restype)
    resource.setrlimit(restype, (limit, hard_limit))  # set soft limit
    try:
        yield
    finally:
        resource.setrlimit(restype, (soft_limit, hard_limit))  # restore


class ExceptionHandler:
    """Catch and handle exceptions in the finally block

    Useage:

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

    """
    def __init__(self) -> None:
        self.exception_happened = False
        self.exc_type = None
        self.exc_value = None
        self.exc_traceback = None

    def __enter__(self) -> 'ExceptionHandler':
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, exc_traceback: Any) -> None:
        # If no exception happened the `exc_type` is None
        self.exception_happened = exc_type is not None
        self.exc_type = exc_type
        self.exc_value = exc_value
        self.exc_traceback = exc_traceback

    def __str__(self) -> Text:
        return "".join(traceback.format_exception(self.exc_type, self.exc_value, self.exc_traceback))
