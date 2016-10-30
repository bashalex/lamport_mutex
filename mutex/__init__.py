from queue import PriorityQueue
from utils.logger import Logger
from time import time
from rpc import API
import fcntl


class LamportMutex:

    __queue = PriorityQueue()
    __mutex = None

    def __on_request(self, sender, sender_time):
        self.__logger.debug('add {} request to the queue'.format((sender_time, sender)))
        self.__queue.put((sender_time, sender))
        self.__logger.debug('send confirmation to {}'.format(sender))
        self.api.confirm(sender)

    def __on_release(self, sender, sender_time):
        request = self.__queue.get()
        if request[0] != sender_time and request[1] != sender:
            self.__logger.error('{} released mutex, but last request in the queue is {}'.format(sender, request))
        else:
            self.__logger.debug('{} release mutex.'.format(sender))

    def __init__(self, path, id, port, ids, ports, logger=None):
        """
        :param path: path to the mutex file. for example mutex.txt
        :param logger: instance of logger
        :param id: self id
        :param port: self port
        :param ids: ids of other processes
        :param ports: ports of other processes
        """
        self.__path = path
        self.__logger = logger if logger is not None else Logger()
        self.__id = id
        self.api = API(id, port, ids, ports, self.__on_request, self.__on_release, logger)

    def lock(self):
        """
        unlock mutex
        :return status whether mutex was locked
        """
        logic_time = self.api.current_time()
        self.__queue.put((logic_time, self.__id))  # add self request to the queue
        self.__logger.debug("put request into the queue")
        self.__logger.log("request", logic_time, time(), self.__id)
        confirmation_time = self.api.request(1)  # request confirmation
        if confirmation_time == -1:
            self.__logger.error('timeout')
            return False
        self.__logger.debug("all confirmations received")
        while 1:  # wait until the first request in queue is our
            with self.__queue.mutex:
                if self.__queue.queue[0][1] == self.__id:
                    break
        self.__logger.debug("our request is first in the queue")
        # mutex is ready to use
        self.__acquire()
        return True

    def unlock(self):
        """
        unlock mutex
        """
        self.__queue.get()
        self.__release()

    def __acquire(self):
        if self.__mutex is not None:
            self.__logger.error("attempt to acquire already acquired mutex")
            return
        logic_time = self.api.acquire()
        self.__mutex = open(self.__path, 'a')
        try:
            fcntl.flock(self.__mutex, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self.__logger.error("attempt to lock already locked file")
        self.__mutex.write("{} {} acquire\n".format(self.__id, logic_time))
        self.__logger.debug("acquire mutex")
        self.__logger.log("acquire", logic_time, time(), self.__id)

    def __release(self):
        if self.__mutex is None or self.__mutex.closed:
            self.__logger.error("attempt to release already released mutex")
            return
        self.__logger.debug("release mutex")
        logic_time = self.api.current_time() + 1  # releasing will be the next event
        self.__mutex.write("{} {} release\n".format(self.__id, logic_time))
        self.__mutex.close()
        self.__mutex = None
        self.__logger.log("release", logic_time, time(), self.__id)
        self.__logger.debug("send broadcast release")
        self.api.release()

    def tear_down(self):
        """
        release socket
        """
        self.api.tear_down()
