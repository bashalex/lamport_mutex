#!/usr/bin/python3.5
from os.path import isfile, join
from utils.logger import Logger
from os import listdir
import settings

# events
RELEASE = 'release'
ACQUIRE = 'acquire'
REQUEST = 'request'

if __name__ == "__main__":
    logger = Logger(debug=True)
    logs = [f for f in listdir(settings.logs_path) if isfile(join(settings.logs_path, f)) and f[-4:] == '.log']
    logger.ok("all log files: " + ", ".join(logs))
    events = []
    for log in logs:
        with open("{}/{}".format(settings.logs_path, log), 'r') as f:
            requested = True
            acquired = False
            lines = f.readlines()
            logger.debug("read {} logs from {}".format(len(lines), log))
            for line in lines:
                if line.startswith('id, logic_time'):  # first line, skip
                    continue
                if line.startswith('warning'):  # skip warnings
                    continue
                if line.startswith('error'):  # skip errors
                    continue
                info, event = line.rstrip().split(":")
                pid, logic_time, timestamp = info.split(",")
                pid, logic_time, timestamp = int(pid), int(logic_time), float(timestamp)
                events.append((pid, logic_time, event))
                if event == REQUEST:
                    requested = True
                if acquired and event == RELEASE:
                    acquired = False
                    requested = False
                elif acquired and event == ACQUIRE:
                    logger.error("acquire already locked mutex!")
                    exit(0)
                elif not acquired and event == ACQUIRE:
                    if not requested:
                        logger.error("acquire not requested mutex!")
                        exit(0)
                    acquired = True
                elif not acquired and event == RELEASE:
                    logger.error("release not acquired mutex!")
                    exit(0)
                elif acquired and event == REQUEST:
                    logger.error("request while mutex already acquired!")
                    exit(0)
            logger.ok("logs in {} are correct".format(log))
    logger.debug("analyze all {} events".format(len(events)))
    acquired = False
    for event in sorted(events, key=lambda x: x[1]):
        if not acquired and event == ACQUIRE:
            acquired = True
        elif acquired and event == ACQUIRE:
            logger.error("somebody acquired mutex while it's already locked")
            exit(0)
        elif not acquired and event == RELEASE:
            logger.error("release not acquired mutex")
            exit(0)
        elif acquired and event == RELEASE:
            acquired = False
    logger.ok("logic times of all events are correct")
