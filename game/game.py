''' Primary game module in game package, containing core game code '''

import pymongo
import yaml
import game.config as config

CONFIG = config.Config()

class GameSession():

    def __init__(self, socket):
        self.socket = GameSocket(socket)
        self.db = pymongo.MongoClient('mongo', 27017).game
        self.user = None

    def _initialize(self):
        name = self.socket.send_wait('Welcome! User?')
        if not self.db.user.find({'name': name}).count():
            msg = 'Does not exist! Create (Y/N)?'
            resp = self.socket.send_wait(msg)
            if resp.upper() == 'Y':
                classes = CONFIG.get('player/class')
                msg = 'Available classes: {}'.format(classes)
                cls = self.socket.send_wait(msg)
                if cls not in classes:
                    self.socket.send('Invalid class!')
                    raise RuntimeError('Invalid class selected')

                self.user = {'name': name, 'class': cls}
                self.db.user.insert_one(self.user)

    def run(self):
        self._initialize()

class GameSocket():
    def __init__(self, socket):
        self._socket = socket

    def get(self):
        return self._socket.recv(1024).decode('utf-8').strip()

    def send(self, data):
        self._socket.sendall(data.encode('utf-8'))

    def send_wait(self, data):
        # Add trailing space to further indicate requested output.
        self.send('{} '.format(data))
        return self.get()
