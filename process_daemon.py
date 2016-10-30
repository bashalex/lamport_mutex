from signal import signal, SIGUSR1, SIGUSR2
from mutex import LamportMutex
from daemon import Daemon
import sys
import os


class DaemonProcess(Daemon):
    mutex = None

    def __init__(self, pidfile, path=None, id=None, port=None,
                 ids=None, ports=None, logger=None, debug=False):
        """
        :param path: path to the mutex file. for example mutex.txt
        :param logger: instance of logger
        :param id: self id
        :param port: self port
        :param ids: ids of other processes
        :param ports: ports of other processes
        """
        self.id = id
        self.mutex_path = path
        self.port = port
        self.ids = ids
        self.ports = ports
        self.logger = logger
        signal(SIGUSR1, self.__lock)
        signal(SIGUSR2, self.__unlock)
        super().__init__(pidfile, debug)

    def signal_term_handler(self, signum, frame):
        self.mutex.tear_down()
        super().signal_term_handler(signum, frame)

    def run(self):
        self.mutex = LamportMutex(path=self.mutex_path,
                                  id=self.id,
                                  port=self.port,
                                  ids=self.ids,
                                  ports=self.ports,
                                  logger=self.logger)

    def get_pid(self):
        try:
            with open(self.pidfile, 'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None

        return pid

    def lock(self):
        pid = self.get_pid()

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return

        os.kill(pid, SIGUSR1)

    def unlock(self):
        pid = self.get_pid()

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return

        os.kill(pid, SIGUSR2)

    def __lock(self, signum, frame):
        self.mutex.lock()

    def __unlock(self, signum, frame):
        self.mutex.unlock()
