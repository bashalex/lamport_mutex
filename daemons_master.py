#!/usr/bin/python3.5
import sys
from os import listdir
from os.path import isfile, join

import settings
from utils.logger import Logger
from utils.process_daemon import DaemonProcess


def kill_daemon(pid):
    daemon = DaemonProcess("{}/{}.pid".format(settings.pids_path, pid))
    print('kill daemon {}'.format(pid))
    daemon.stop()


def process_lock_mutex(pid):
    daemon = DaemonProcess("{}/{}.pid".format(settings.pids_path, pid))
    daemon.lock()


def process_unlock_mutex(pid):
    daemon = DaemonProcess("{}/{}.pid".format(settings.pids_path, pid))
    daemon.unlock()


if __name__ == "__main__":
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
            exit(0)
    if 'kill' == sys.argv[1]:
        if pid == -1:
            pids = [f for f in listdir(settings.pids_path) if isfile(join(settings.pids_path, f))]
            pids = [pid[:-4] for pid in pids if pid[-4:] == '.pid']
            if len(pids) == 0:
                print('No alive daemons :(')
            [kill_daemon(pid) for pid in pids]
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

