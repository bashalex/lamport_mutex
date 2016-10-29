from tornado import websocket, web, ioloop
from threading import Thread
from network.serializator import deserialize
from logger import Logger


class Receiver:

    class SocketHandler(websocket.WebSocketHandler):
        def initialize(self, cb):
            self.callback = cb

        def data_received(self, chunk):
            pass

        def open(self):
            pass

        def on_message(self, message):
            self.callback(deserialize(message))

        def on_close(self):
            pass

    def run_loop(self, app, port):
        try:
            app.listen(port)
            self.logger.debug("socket created on port: {}".format(port))
        except PermissionError:
            self.logger.error("wrong port number")
        ioloop.IOLoop.instance().start()

    def tear_down(self):
        self.thread.join(1)
        self.logger.debug("socket released")

    def __init__(self, id: int, port: int, cb):
        self.id = id
        self.logger = Logger()
        self.app = web.Application([
            (r'/ws', self.SocketHandler, dict(cb=cb))
        ])
        self.thread = Thread(target=self.run_loop, args=(self.app, port), daemon=True)
        self.thread.start()
