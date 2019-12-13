''' Contains game server code '''

import logging
import socket

from gevent import Greenlet

from game.game import GameSession

class TelnetServer():
    ''' Listener handling for Telnet server, creates session greenlets '''

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
        ''' Helper function for logging '''

        self._logger.debug(message)

    def run(self):
        ''' Listener loop '''

        while True:
            # Via listener socket, new server socket spawned to handle unique
            # connection with client, so it can continue listening.
            # Blocks thread  on 'accept' waiting for new connection attempts.
            conn, _ = self._listener.accept()
            TelnetServerHandler(conn)

class TelnetServerHandler(Greenlet):
    ''' Wrapper class for game session Greenlet '''

    def __init__(self, sock):
        self._socket = sock
        self._game = GameSession(sock)
        super().__init__(self.handle)
        self.start()

    def handle(self):
        ''' Main execution body for game session greenlet '''

        with self._socket: # Kill conn. if exception, finishes, etc.
            self._game.run()
