from threading import Thread

from tornado import websocket, web, ioloop

from network.serializator import deserialize
from utils.logger import Logger


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
            app.listen(port, no_keep_alive=True)
            self.logger.debug("socket created on port: {}".format(port))
        except PermissionError:
            self.logger.error("wrong port number")
        except OSError:
            self.logger.error("port already in use")
        self.logger.debug("run loop: IOLoop: {}".format(ioloop.IOLoop.current()))
        # init and make thread IOLoop 'current' to be able to stop it from the main thread
        ioloop.IOLoop.instance().make_current()
        # start loop in this thread (2)
        ioloop.IOLoop.current().start()

    def tear_down(self):
        self.logger.debug("tear down: IOLoop: {}".format(ioloop.IOLoop.current()))
        ioloop.IOLoop.current().stop()
        self.thread.join(1)
        self.logger.debug("socket released")

    def __init__(self, id: int, port: int, cb, logger=None):
        self.id = id
        self.logger = logger if logger is not None else Logger()
        self.app = web.Application([
            (r'/ws', self.SocketHandler, dict(cb=cb))
        ])
        self.thread = Thread(target=self.run_loop, args=(self.app, port))
        self.thread.start()
