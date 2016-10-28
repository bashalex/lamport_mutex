from websocket import create_connection
from typing import List
from network.models import Process
import log


class Sender(object):

    def __init__(self, id: int, others: List[Process]):
        self.id = id
        self.processes = {}
        for process in others:
            try:
                self.processes[process.id] = create_connection("ws://localhost:{}/ws".format(process.port))
            except ConnectionRefusedError:
                self.processes[process.id] = process.port
        log.ok("sender {} created".format(id))

    def send(self, recipient_id: int, message: str):
        recipient = self.processes.get(recipient_id)
        if recipient is None:
            log.error("recipient doesn't exist")
            return False
        if type(recipient) is int:
            try:
                recipient = create_connection("ws://localhost:{}/ws".format(recipient))
            except ConnectionRefusedError:
                log.error("can't connect to {}".format(recipient))
                return False
            self.processes[recipient_id] = recipient
        log.ok("message sent")
        return recipient.send(message)

    def broadcast(self, message: str):
        [self.send(recipient_id, message) for recipient_id in self.processes.keys()]
