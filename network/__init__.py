from network.models import Process
from network.receiver import Receiver
from network.sender import Sender
from network.serializator import serialize


class Connection:
    def __init__(self, id, port, other_ids, other_ports, cb):
        """
        :param id: process id
        :param port: socket port
        :param other_ids: ids of other processes
        :param other_ports: ports of other processes
        :param cb: callback function for receiving messages
        """
        self.id = id
        self.port = port
        self.sender = Sender(id, [Process(_id, _port) for _id, _port in zip(other_ids, other_ports)])
        self.receiver = Receiver(id, port, cb)

    def send(self, recipient_id, message, time):
        """
        :param recipient_id: id of message recipient
        :param message: message to send
        :param time: local Lamport clock time
        """
        self.sender.send(recipient_id, serialize(message, self.id, time))

    def broadcast(self, message, time):
        """
        :param message: message to send to every other process
        :param time: local Lamport clock time
        """
        self.sender.broadcast(serialize(message, self.id, time))

    def tear_down(self):
        """
        release socket
        """
        self.receiver.tear_down()
