from network import Connection
from threading import RLock
from time import time


class API:
    """
    class is not thread-safe. Can be used only in one thread.
    """
    # constants
    __REQUEST = 0
    __RELEASE = 1
    __CONFIRM = 2
    # variables
    __lock = RLock()
    # we use this lock to achieve consistency inside some functions
    # where we suppose logic time to be the same during the whole execution of function
    __clock = 0  # lamport clock
    __number_of_processes = 0  # exclude current
    __number_of_confirmations = 0
    __last_confirmation_time = 0

    def __on_response(self, response):
        message, sender, sender_time = response
        self.__lock.acquire()
        self.__clock = max(self.__clock, sender_time) + 1
        if message == self.__CONFIRM:
            self.__number_of_confirmations += 1
            self.__last_confirmation_time = self.__clock
            self.__lock.release()
            return
        self.__lock.release()
        if message == self.__REQUEST:
            self.on_request(sender, sender_time)
        elif message == self.__RELEASE:
            self.on_release(sender, sender_time)

    def __init__(self, id, port, ids, ports, on_request, on_release):
        """
        :param id: self id
        :param port: self port
        :param ids: ids of other processes
        :param ports: ports of other processes
        :param on_request: callback function
        :param on_release: callback function
        """
        self.__number_of_processes = len(ids)
        self.on_request = on_request
        self.on_release = on_release
        self.connection = Connection(id, port, ids, ports, self.__on_response)

    def current_time(self):
        """
        :return: current lamport clock time
        """
        return self.__clock

    def request(self, timeout: int) -> int:
        """
        send broadcast request with intention to enter critical section
        returns when all confirmations received or after timeout
        :param timeout: max await time in seconds
        :return: -1 if timeout, otherwise time of the last confirmation
        """
        self.__lock.acquire()
        self.__clock += 1
        self.__number_of_confirmations = 0
        self.__last_confirmation_time = 0
        self.connection.broadcast(self.__REQUEST, self.__clock)
        self.__lock.release()
        start = time()
        # await confirmations
        while self.__number_of_confirmations != self.__number_of_processes:
            if time() - start >= timeout:
                return -1
        return self.__last_confirmation_time

    def confirm(self, recipient_id):
        """
        send confirmation
        :param recipient_id: id of process which requires confirmation
        """
        self.__lock.acquire()
        self.__clock += 1
        self.connection.send(recipient_id, self.__CONFIRM, self.__clock)
        self.__lock.release()

    def release(self):
        """
        send broadcast request to notify exit from critical section
        :return logic time of event
        """
        self.__lock.acquire()
        try:
            self.__clock += 1
            self.connection.broadcast(self.__RELEASE, self.__clock)
            return self.__clock
        finally:
            self.__lock.release()

    def acquire(self):
        """
        actually it isn't RPC, but we call it to increment clock
        :return logic time of event
        """
        self.__lock.acquire()
        try:
            self.__clock += 1
            return self.__clock
        finally:
            self.__lock.release()

    def tear_down(self):
        """
        release socket
        """
        self.connection.tear_down()
