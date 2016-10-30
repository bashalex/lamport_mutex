from network.models import Process
from network.receiver import Receiver
from network.sender import Sender
from network.serializator import serialize


class Connection:
    def __init__(self, id, port, other_ids, other_ports, cb, logger=None):
        """
        :param id: process id
        :param port: socket port
        :param other_ids: ids of other processes
        :param other_ports: ports of other processes
        :param cb: callback function for receiving messages
        """
        self.id = id
        self.port = port
        self.sender = Sender(id, [Process(_id, _port) for _id, _port in zip(other_ids, other_ports)],
                             logger)
        self.receiver = Receiver(id, port, cb, logger)

    def send(self, recipient_id, message, time, request_id=-1):
        """
        :param recipient_id: id of message recipient
        :param message: message to send
        :param time: local Lamport clock time
        :param request_id:
                1. if message is request that awaits answer
                           :param request_id contains unique id of this request
                2. if message is response (actually 'confirmation' in our case)
                           :param request_id contains id of incoming request.
        """
        self.sender.send(recipient_id, serialize(message, self.id, time, request_id))

    def tear_down(self):
        """
        release socket
        """
        self.receiver.tear_down()
