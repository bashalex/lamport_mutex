#!/usr/bin/python3.5
from queue import PriorityQueue
from mutex import LamportMutex
import sys
from logger import Logger
import parser

queue = PriorityQueue()


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

if __name__ == "__main__":
    logger = Logger()
    try:
        id, port, ids, ports, mutex_path, debug = parser.parse_arguments(sys.argv, logger)
        logger = Logger(debug=debug, out='logs/{}.txt'.format(id))
        mutex = LamportMutex(path=mutex_path,
                             logger=logger,
                             id=id,
                             port=port,
                             ids=ids,
                             ports=ports)
    except ValueError:
        exit(0)
    print("You can use following commands:")
    print("\t- lock")
    print("\t- unlock")
    print("\t- exit")
    while True:
        try:
            run_command(input())
        except KeyboardInterrupt:
            exit_program()
