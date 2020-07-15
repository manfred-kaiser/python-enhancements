import fcntl
import logging
import pathlib
import os
from typing import Text


def pid_lock(pid_file: Text, message: Text = 'another instance is running') -> bool:
    try:
        pid_dir = os.path.dirname(pid_file)
        if os.path.isdir(pid_dir):
            if not os.access(pid_dir, os.W_OK):
                logging.error("directory '%s' not writeable", pid_dir)
                return False
        else:
            try:
                pathlib.Path(pid_dir).mkdir(parents=True, exist_ok=True)
            except PermissionError:
                logging.error('can not create output directory')
                return False

        fp = open(pid_file, 'w')
        fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except IOError:
        logging.info(message)
    except Exception:
        logging.exception("Unknown error creating pid file")
    return False
