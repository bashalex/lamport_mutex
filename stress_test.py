#!/usr/bin/python3.5
from daemons_master import kill_all
from utils.logger import Logger
from time import sleep
import sys
import os


if __name__ == "__main__":
    logger = Logger()
    if len(sys.argv) != 3:
        logger.error("Run with 2 arguments:")
        logger.error("\t- number of processes (int)" +
                     "\n\t- duration in seconds (int)")
        logger.error('for example: ./stress_test.py 10 15')
        exit(0)
    try:
        num_of_processes, duration = int(sys.argv[1]), int(sys.argv[2])
    except ValueError:
        logger.error("arguments must be ints")
        num_of_processes, duration = None, None
        exit(0)
    path_mutex = 'mutex.txt'
    ports = [8000 + i for i in range(num_of_processes)]
    for i in range(num_of_processes):
        command = './main.py {0} {1} "{2}" "{3}" {4} {5} {6} {7}'.format(
            i,
            ports[i],
            [id for id in range(num_of_processes) if id != i],
            [port for port in ports if port != ports[i]],
            path_mutex,
            True,
            True,
            True
        )
        os.system(command)
    logger.warn("wait {} seconds".format(duration))
    sleep(duration)
    logger.warn("kill all daemons...")
    kill_all()
    logger.warn("kill all daemons...OK")
