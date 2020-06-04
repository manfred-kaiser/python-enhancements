# -*- coding: utf-8 -*-

import contextlib
import resource
import signal

from enhancements.exceptions import ContextManagerTimeout


@contextlib.contextmanager
def memorylimit(limit, restype=resource.RLIMIT_AS):
    soft_limit, hard_limit = resource.getrlimit(restype)
    resource.setrlimit(restype, (limit, hard_limit))  # set soft limit
    try:
        yield
    finally:
        resource.setrlimit(restype, (soft_limit, hard_limit))  # restore


@contextlib.contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise ContextManagerTimeout("Timed out!")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
