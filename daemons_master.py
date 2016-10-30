#!/usr/bin/python3.5
import sys
from os import listdir
from os.path import isfile, join

import settings
from utils.logger import Logger
from utils.process_daemon import DaemonProcess


def kill_all():
    pids = [f for f in listdir(settings.pids_path) if isfile(join(settings.pids_path, f))]
    pids = [_pid[:-4] for _pid in pids if _pid[-4:] == '.pid']
    if len(pids) == 0:
        print('No alive daemons :(')
    [kill_daemon(_pid) for _pid in pids]


def kill_daemon(_pid):
    daemon = DaemonProcess("{}/{}.pid".format(settings.pids_path, _pid))
    print('kill daemon {}'.format(_pid))
    daemon.stop()


def process_lock_mutex(_pid):
    daemon = DaemonProcess("{}/{}.pid".format(settings.pids_path, _pid))
    daemon.lock()


def process_unlock_mutex(_pid):
    daemon = DaemonProcess("{}/{}.pid".format(settings.pids_path, _pid))
    daemon.unlock()


if __name__ == "__main__":
    """
    Allow to control spawned daemons
    Arguments:
        - command (kill | lock | unlock)
        - pid (int or 'all')
    Example 1: kill all daemons
        ./daemons_master.py kill all
    Example 2: Make process with id = 1 lock mutex
        ./daemons_master.py lock 1
    Example 3: Make process with id = 0 unlock mutex
        ./daemons_master.py unlock 0
    """
    logger = Logger()
    if len(sys.argv) != 3:
        logger.error("Run with 2 arguments:")
        logger.error("\t- command (kill | lock | unlock)" +
                     "\n\t- pid (int or 'all')")
        logger.error('for example: ./daemons_master.py kill 0')
        exit(0)
    try:
        pid = int(sys.argv[2])
    except ValueError:
        if sys.argv[1] == 'kill' and 'all' == sys.argv[2]:
            pid = -1
        else:
            pid = None
            exit(0)
    if 'kill' == sys.argv[1]:
        if pid == -1:
            kill_all()
        else:
            kill_daemon(pid)
    elif 'lock' == sys.argv[1]:
        process_lock_mutex(pid)
    elif 'unlock' == sys.argv[1]:
        process_unlock_mutex(pid)
    else:
        if len(sys.argv) != 3:
            logger.error("Wrong arguments")
            logger.error("\t- command (kill | lock | unlock)" +
                         "\n\t- pid (int or 'all')")
            logger.error('for example: ./daemons_master.py kill 0')
            exit(0)
