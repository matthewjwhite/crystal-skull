''' Contains game server code '''

import logging
import socket

from gevent import Greenlet
from gevent import monkey
monkey.patch_all()

from game.game import GameSession

class TelnetServer():

    def __init__(self, host='', port=5555):
        # IPv4 socket (socket.AF_INET), TCP (socket.SOCK_STREAM).
        self._listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        logging.basicConfig()
        self._logger = logging.getLogger('server')
        self._logger.setLevel(logging.DEBUG)

        # https://docs.python.org/3/library/socket.html#example
        # Explicitly assign host and port to this socket ('bind' required
        # when explicitly specifying port).
        self._listener.bind((host, port))

        # Start listening.
        self._listener.listen()

    def log(self, message):
        self._logger.debug(message)

    def run(self):
        while True:
            # Via listener socket, new server socket spawned to handle unique
            # connection with client, so it can continue listening.
            # Blocks thread  on 'accept' waiting for new connection attempts.
            conn, addr = self._listener.accept()
            TelnetServerHandler(conn)

class TelnetServerHandler(Greenlet):
    def __init__(self, socket):
        self._socket = socket
        self._game = GameSession(socket)
        super().__init__(self.handle)
        self.start()

    def handle(self):
        with self._socket: # Kill conn. if exception, finishes, etc.
            self._game.run()