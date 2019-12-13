''' Primary game module in game package, containing core game code '''

from game.user import User

class GameSession(): #pylint: disable=too-few-public-methods
    ''' Represents the game session for a single player '''

    def __init__(self, socket):
        self.socket = GameSocket(socket)
        self.user = None

    def run(self):
        ''' Kicked off when the Greenlet is created '''

        self.user = User.get_user(self.socket)
        self.socket.send('Welcome, {}!'.format(self.user.name))

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

    def send_wait(self, data):
        ''' Sends and waits for data '''

        # Add trailing space to further indicate requested output.
        self.send('{} '.format(data))
        return self.get()
