#!/usr/bin/python3.5
from mutex import LamportMutex
from process_daemon import DaemonProcess
from logger import Logger
import settings
import parser
import sys


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


if __name__ == "__main__":
    logger = Logger()
    try:
        id, port, ids, ports, mutex_path, debug, daemon = parser.parse_arguments(sys.argv, logger)
        logger = Logger(debug=debug, out='{}/{}.txt'.format(settings.logs_path, id))
        if daemon:
            daemon = DaemonProcess(pidfile="{}/{}.pid".format(settings.pids_path, id),
                                   path=mutex_path,
                                   id=id,
                                   port=port,
                                   ids=ids,
                                   ports=ports,
                                   logger=logger,
                                   debug=debug)
            daemon.start()
        else:
            mutex = LamportMutex(path=mutex_path,
                                 id=id,
                                 port=port,
                                 ids=ids,
                                 ports=ports,
                                 logger=logger)
            run_interactive_app()
    except ValueError:
        exit(0)
