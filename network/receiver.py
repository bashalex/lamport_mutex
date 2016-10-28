from tornado import websocket, web, ioloop
from threading import Thread
import log


class Receiver:

    class SocketHandler(websocket.WebSocketHandler):
        def initialize(self, cb):
            self.callback = cb

        def data_received(self, chunk):
            pass

        def open(self):
            pass

        def on_message(self, message):
            self.callback(message)

        def on_close(self):
            pass

    @staticmethod
    def run_loop(app, port):
        try:
            app.listen(port)
            log.ok("socket created on port: {}".format(port))
        except PermissionError:
            log.error("wrong port number")
        ioloop.IOLoop.instance().start()

    def kill(self):
        self.thread.join(1)
        log.ok("socket released")

    def __init__(self, id: int, port: int, cb):
        self.id = id
        self.app = web.Application([
            (r'/ws', self.SocketHandler, dict(cb=cb))
        ])
        self.thread = Thread(target=self.run_loop, args=(self.app, port), daemon=True)
        self.thread.start()
