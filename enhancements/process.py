import fcntl
import sys


def pid_lock(pid_file, exit_code=0, message='another instance is running'):
    fp = open(pid_file, 'w')
    try:
        fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        print("another instance is running", file=sys.stderr)
        sys.exit(exit_code)
