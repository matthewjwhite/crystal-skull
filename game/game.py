''' Primary game module in game package, containing core game code '''

import pymongo
import yaml
import game.config as config
import uuid
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64

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
                key = self.socket.send_wait('Paste your (base64-encoded) '
                                            'public key.')
                key = base64.b64decode(key).decode('utf-8')
                if not key:
                    self.socket.send('Bad key!')
                    raise RuntimeError('Invalid key specified')

                classes = CONFIG.get('player/class')
                msg = 'Available classes: {}'.format(classes)
                cls = self.socket.send_wait(msg)
                if cls not in classes:
                    self.socket.send('Invalid class!')
                    raise RuntimeError('Invalid class selected')

                self.user = {'name': name, 'class': cls,
                             'auth': {'publicKey': key}}
                self.db.user.insert_one(self.user)
        else:
            key = self.db.user.find_one({'name': name})['auth']['publicKey']
            key = key.encode('utf-8')
            key = RSA.importKey(key)
            cipher = PKCS1_v1_5.new(key)
            challenge = str(uuid.uuid4())
            challenge_bytes = challenge.encode('utf-8')
            challenge_bytes = cipher.encrypt(challenge_bytes)
            enc = base64.b64encode(challenge_bytes).decode()
            attempt = self.socket.send_wait(enc)
            print(challenge)
            print(attempt)
            if challenge == attempt:
                self.socket.send('woo!')

    def run(self):
        self._initialize()

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
