from websocket import create_connection
from typing import List
from network.models import Process
from logger import Logger


class Sender(object):

    def __init__(self, id: int, others: List[Process]):
        self.id = id
        self.logger = Logger()
        self.ports = {}
        self.processes = {}
        for process in others:
            self.ports[process.id] = process.port
            try:
                self.processes[process.id] = create_connection("ws://localhost:{}/ws".format(process.port))
            except ConnectionRefusedError:
                self.processes[process.id] = None

    def send(self, recipient_id: int, message: str):
        recipient = self.processes.get(recipient_id)
        if recipient is None:
            recipient = self.__open_socket(recipient_id)
        if not recipient:
            return False
        try:
            recipient.send(message)
        except BrokenPipeError:
            recipient = self.__open_socket(recipient_id)
            if not recipient:
                return False
            recipient.send(message)
        return True

    def __open_socket(self, recipient_id):
        try:
            port = self.ports.get(recipient_id)
            if port is None:
                self.logger.error("recipient id doesn't exist")
                return False
            recipient = create_connection("ws://localhost:{}/ws".format(port))
        except ConnectionRefusedError:
            self.logger.error("can't connect to {}".format(recipient_id))
            return False
        self.processes[recipient_id] = recipient
        return recipient

    def broadcast(self, message: str):
        [self.send(recipient_id, message) for recipient_id in self.processes.keys()]
