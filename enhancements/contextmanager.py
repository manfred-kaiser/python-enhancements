# -*- coding: utf-8 -*-

import contextlib
import resource
from typing import Iterator


@contextlib.contextmanager
def memorylimit(limit: int, restype: int = resource.RLIMIT_AS) -> Iterator[None]:
    soft_limit, hard_limit = resource.getrlimit(restype)
    resource.setrlimit(restype, (limit, hard_limit))  # set soft limit
    try:
        yield
    finally:
        resource.setrlimit(restype, (soft_limit, hard_limit))  # restore
