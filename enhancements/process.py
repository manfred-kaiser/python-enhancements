import fcntl
import logging
import pathlib
import os
import sys


def pid_lock(pid_file, exit_code=0, message='another instance is running'):
    try:
        pid_dir = os.path.dirname(pid_file)
        if os.path.isdir(pid_dir):
            if not os.access(pid_dir, os.W_OK):
                logging.error("directory '%s' not writeable", pid_dir)
                sys.exit(1)
        else:
            try:
                pathlib.Path(pid_dir).mkdir(parents=True, exist_ok=True)
            except PermissionError:
                logging.error('can not create output directory')
                sys.exit(1)

        fp = open(pid_file, 'w')
        fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        logging.info("another instance is running")
        sys.exit(exit_code)
    except Exception:
        logging.exception("Unknown error creating pid file")
        sys.exit(2)
