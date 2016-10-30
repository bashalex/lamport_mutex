from queue import PriorityQueue
from utils.logger import Logger
from time import time
from rpc import API
import fcntl


class LamportMutex:

    __queue = PriorityQueue()
    __mutex = None

    def __on_request(self, sender, sender_time, request_id):
        # self.__logger.log('I confirm', sender_time, time(), sender)
        self.__logger.debug('add {} request to the queue'.format((sender_time, sender)))
        self.__queue.put((sender_time, sender))
        self.__logger.debug('send confirmation to {}'.format(sender))
        self.api.confirm(sender, request_id)

    def __remove_request_from_queue(self, sender):
        """
        it isn't very efficient but who cares
        """
        with self.__queue.mutex:
            for x in self.__queue.queue:
                if x[1] == sender:
                    self.__queue.queue.remove(x)
                    return True
        return False

    def __on_release(self, sender, sender_time):
        if not self.__remove_request_from_queue(sender):
            self.__logger.error("release from {} but there is no request from it in the queue"
                                .format(sender))
            return
        self.__logger.log('release', sender_time, time(), sender)
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
        confirmation_time = self.api.request(timeout=1)  # request confirmation
        if confirmation_time == -1:
            self.__logger.error('timeout')
            self.__logger.debug("remove request from the queue")
            self.__queue.get()
            return False
        self.__logger.warn("all confirmations received")
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
        self.__logger.debug("__acquire mutex start")
        if self.__mutex is not None:
            self.__logger.error("attempt to acquire already acquired mutex")
            return
        # increment clock, because 'acquire mutex' it is event itself
        logic_time = self.api.increment_clock()
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
        # increment clock, because 'release mutex' it is event itself
        logic_time = self.api.increment_clock()
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
        if self.__mutex is not None and not self.__mutex.closed:
            self.__release()
        self.api.tear_down()
