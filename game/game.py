''' Primary game module in game package, containing core game code '''

import random

from game.user import User, BadMove

class GameSession(): #pylint: disable=too-few-public-methods
    ''' Represents the game session for a single player '''

    def __init__(self, socket):
        self.socket = GameSocket(socket)
        self.user = None

    def run(self):
        ''' Kicked off when the Greenlet is created '''

        self.user = User.get_user(self.socket)
        self.socket.send_nl('Welcome, {}!'.format(self.user.name))

        while self.socket.send_wait('Continue?').lower() != 'n':
            if GameSession._battle():
                self.user.battle(self.socket)

            direction = self.socket.send_wait('Explore (N/E/S/W)?')
            if direction.lower() not in ['n', 'e', 's', 'w']:
                self.socket.send_nl('Very well, traveller!')

            try:
                self.user.move(direction)
            except BadMove:
                self.socket.send_nl('At boundary, choose another direction!')

    # Determines whether to enter a battle or not.
    @staticmethod
    def _battle():
        return random.randrange(100) % 3 == 0

class GameSocket():
    ''' Wrapper for the server socket, to communicate with client '''

    def __init__(self, socket):
        self._socket = socket

    def get(self):
        ''' Gets data in buffer from client '''

        # 10000 is arbitrary - general high number of bytes.
        return self._socket.recv(10000).decode('utf-8').strip()

    def send(self, data):
        ''' Sends data to client '''

        self._socket.sendall(data.encode('utf-8'))

    def send_nl(self, data):
        ''' Wrapper for send, attaches newline '''

        self.send('{}\r\n'.format(data))

    def send_wait(self, data):
        ''' Sends and waits for data '''

        # Add trailing space to further indicate requested output.
        self.send('{} '.format(data))
        return self.get()
