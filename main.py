#!/usr/bin/python3.5
import sys

import settings
from mutex import LamportMutex
from time import sleep
from utils import parser
from utils.logger import Logger
from utils.process_daemon import DaemonProcess


def run_command(command):
    if command == 'lock':
        mutex.lock()
    elif command == 'unlock':
        mutex.unlock()
    elif command == 'exit':
        exit_program()
    else:
        logger.error("wrong command")


def exit_program():
    mutex.tear_down()
    exit(0)


def run_interactive_app():
    print("You can use following commands:")
    print("\t- lock")
    print("\t- unlock")
    print("\t- exit")
    while True:
        try:
            run_command(input())
        except KeyboardInterrupt:
            exit_program()


def run_stress_mode():
    logger.warn("wait other processes...")
    while not mutex.api.ping_all():
        continue
    logger.warn("run stress mode")
    while 1:
        try:
            if mutex.lock():
                mutex.unlock()
        except KeyboardInterrupt:
            exit_program()


if __name__ == "__main__":
    """
    Spawn new process in one of two modes: interactive or daemon
    Arguments:
        - id (int) - id of new process
        - port (int) - port for socket
        - list of other ids
        - list of other ports
        - path to mutex file
        - debug (boolean)
        - daemon (boolean)
        - stress_mode (boolean)
    Example:
        ./main.py 0 8800 "1, 2" "8801, 8802" mutex.txt false true false
    """
    logger = Logger()
    try:
        id, port, ids, ports, mutex_path, debug, daemon, stress_mode =\
                                            parser.parse_arguments(sys.argv, logger)
        logger = Logger(debug=debug, out='{}/{}.log'.format(settings.logs_path, id))
        if daemon:
            daemon = DaemonProcess(pidfile="{}/{}.pid".format(settings.pids_path, id),
                                   path=mutex_path,
                                   id=id,
                                   port=port,
                                   ids=ids,
                                   ports=ports,
                                   logger=logger,
                                   debug=debug,
                                   stress_mode=stress_mode)
            daemon.start()
        else:
            mutex = LamportMutex(path=mutex_path,
                                 id=id,
                                 port=port,
                                 ids=ids,
                                 ports=ports,
                                 logger=logger)
            sleep(1)  # sleep for a while because socket doesn't open immediately
            if stress_mode:
                run_stress_mode()
            else:
                run_interactive_app()
    except ValueError:
        exit(0)
