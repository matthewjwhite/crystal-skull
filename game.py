class GameSession():

    def __init__(self, socket):
        self.socket = GameSocket(socket)

    def run(self):
        response = self.socket.send_wait('Welcome! User?')
        self.socket.send('Hello, {}!'.format(response))

class GameSocket():
    def __init__(self, socket):
        self._socket = socket

    def get(self):
        return self._socket.recv(1024).decode('utf-8').strip()

    def send(self, data):
        self._socket.sendall(data.encode('utf-8'))

    def send_wait(self, data):
        self.send(data)
        return self.get()
