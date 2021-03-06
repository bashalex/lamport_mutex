from network import Connection
from threading import RLock
from time import time


class API:
    """
    Actually it is not pure RPC class.
    At least normally RPC layer doesn't suppose incoming messages
    that aren't answers for our outgoing requests.
    It means that in our case we must have some callback for them anyway (or maybe futures).
    Moreover some of our requests don't suppose answer (e.g. 'release').
    Therefore I guess it would be strange to await every confirmation
    before sending next request during broadcast messaging.
    (Can consider current implementation of 'request' method as asynchronous remote calls :))

    Anyway from the outside calls of the functions from this class looks exactly like RPC
    because they return only after receiving response (if it's supposed to be there).
    """
    # constants
    __REQUEST = 0
    __RELEASE = 1
    __CONFIRM = 2
    __PING = 3
    # variables
    __lock = RLock()
    # we use this lock to achieve consistency inside some functions
    # where we suppose logic time to be the same during the whole execution of function
    clock = 0  # lamport clock
    __number_of_processes = 0  # exclude current
    __number_of_confirmations = 0
    __last_request_id = 0
    __last_confirmation_time = 0

    def on_response(self, response):
        message, sender, sender_time, request_id = response
        self.__lock.acquire()
        self.clock = max(self.clock, sender_time) + 1
        if message == self.__CONFIRM:
            if request_id != self.__last_request_id:
                # probably it's delayed confirmation for previous PING request
                # that finished with timeout
                # ignore it
                return
            self.__number_of_confirmations += 1
            self.__last_confirmation_time = self.clock
            self.__lock.release()
            return
        self.__lock.release()
        if message == self.__REQUEST:
            self.on_request(sender, sender_time, request_id)
        elif message == self.__RELEASE:
            self.on_release(sender, sender_time)
        elif message == self.__PING:
            self.confirm(sender, request_id)

    def __init__(self, id, port, ids, ports, on_request, on_release, logger=None):
        """
        :param id: self id
        :param port: self port
        :param ids: ids of other processes
        :param ports: ports of other processes
        :param on_request: callback function
        :param on_release: callback function
        """
        self.__number_of_processes = len(ids)
        self.ids = ids
        self.on_request = on_request
        self.on_release = on_release
        self.logger = logger
        self.connection = Connection(id, port, ids, ports, self.on_response, logger)

    def current_time(self):
        """
        :return: current lamport clock time
        """
        return self.clock

    def request(self) -> int:
        """
        send broadcast request with intention to acquire mutex
        returns when all confirmations received or after timeout
        :return: -1 if timeout, otherwise time of the last confirmation
        """
        self.__lock.acquire()
        self.__number_of_confirmations = 0
        self.__last_confirmation_time = 0
        self.__last_request_id += 1
        for _id in self.ids:
            self.clock += 1
            self.connection.send(_id, self.__REQUEST, self.clock, self.__last_request_id)
        self.__lock.release()
        start = time()
        # await confirmations
        timeout = False
        while self.__number_of_confirmations != self.__number_of_processes:
            if time() - start >= 10 and not timeout:
                self.logger.error('await for confirmations more than 10s...')
                timeout = True
        return self.__last_confirmation_time

    def confirm(self, recipient_id, request_id):
        """
        send confirmation
        :param recipient_id: id of process which requires confirmation
        """
        self.__lock.acquire()
        self.clock += 1
        # self.logger.warn("pong to {} with id: {}".format(recipient_id, request_id))
        self.connection.send(recipient_id, self.__CONFIRM, self.clock, request_id)
        self.__lock.release()

    def release(self):
        """
        send broadcast request to notify release of mutex
        :return logic time of event
        """
        self.__lock.acquire()
        try:
            for _id in self.ids:
                self.clock += 1
                self.connection.send(_id, self.__RELEASE, self.clock)
            return self.clock
        finally:
            self.__lock.release()

    def increment_clock(self):
        """
        actually it isn't remote call, just increment local clock
        :return logic time of event
        """
        self.__lock.acquire()
        try:
            self.clock += 1
            return self.clock
        finally:
            self.__lock.release()

    def ping_all(self, timeout=1):
        self.__number_of_confirmations = 0
        self.__last_confirmation_time = 0
        self.__last_request_id += 1
        for _id in self.ids:
            self.connection.send(_id, self.__PING, self.clock, self.__last_request_id)
        start = time()
        # await confirmations
        while self.__number_of_confirmations != self.__number_of_processes:
            if time() - start >= timeout:
                return False
        return True

    def tear_down(self):
        """
        release socket
        """
        self.connection.tear_down()
