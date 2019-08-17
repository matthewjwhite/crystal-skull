''' Primary game module in game package, containing core game code '''

from game.user import User

class GameSession():

    def __init__(self, socket):
        self.socket = GameSocket(socket)
        self.user = None

    def run(self):
        self.user = User.get_user(self.socket)
        self.socket.send('Welcome, {}!'.format(self.user.name))

class GameSocket():
    def __init__(self, socket):
        self._socket = socket

    def get(self):
        # 10000 is arbitrary - general high number of bytes.
        return self._socket.recv(10000).decode('utf-8').strip()

    def send(self, data):
        self._socket.sendall(data.encode('utf-8'))

    def send_wait(self, data):
        # Add trailing space to further indicate requested output.
        self.send('{} '.format(data))
        return self.get()
