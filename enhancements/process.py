import fcntl
import logging
import pathlib
import os


def pid_lock(pid_file, message='another instance is running'):
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
        logging.info("another instance is running")
    except Exception:
        logging.exception("Unknown error creating pid file")
    return False
