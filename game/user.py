import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import pymongo
import uuid

import game.config as config

CONFIG = config.Config()
DB = pymongo.MongoClient('mongo', 27017).game.user

# Avoid accidental multiple occurrences, ie. if multiple creation
# attempts for same user in close occurrence. Overall, enforces
# unique 'name' field value, allowing us to use this as our unique
# identifier for the user.
DB.create_index([('name', pymongo.TEXT)], unique=True)

class User:
    @classmethod
    def get_user(cls, socket):
        print(cls)
        print(socket)
        name = socket.send_wait('Welcome! User?')
        if not DB.find({'name': name}).count():
            return cls.create_user(socket, name)

        # Instantiate RSA public key object.
        key = DB.find_one({'name': name})['key'].encode('utf-8')
        key = RSA.importKey(key)

        # Encrypt random challenge for user to decrypt w/ priv. key.
        cipher = PKCS1_v1_5.new(key)
        challenge = str(uuid.uuid4())
        challenge_bytes = challenge.encode('utf-8')
        challenge_bytes = cipher.encrypt(challenge_bytes)
        enc = base64.b64encode(challenge_bytes).decode()

        # Get attempt, and compare.
        attempt = socket.send_wait('Decrypted {}?'.format(enc))
        if challenge == attempt:
            user = DB.find_one({'name': name})
            return User(user['name'], user['class'], user['key'])

    @staticmethod
    def create_user(socket, name):
        msg = 'Does not exist! Create (Y/N)?'
        resp = socket.send_wait(msg)
        if resp.upper() != 'Y':
            raise RuntimeError('User does not want to create user')

        # Get public key, to be used for further auth.
        key = socket.send_wait('Paste your (base64-encoded) '
                               'public key.')
        key = base64.b64decode(key).decode('utf-8')

        # Confirm selected class.
        classes = CONFIG.get('player/class')
        msg = 'Available classes: {}'.format(classes)
        cls = socket.send_wait(msg)
        if cls not in classes:
            socket.send('Invalid class!')
            raise RuntimeError('Invalid class selected')

        user = User(name, cls, key)
        user.save()

        return user

    def __init__(self, name, cls, key):
        self.cls = cls
        self.name = name
        self.key = key

    def save(self):
        data = {
            'name': self.name,
            'class': self.cls,
            'key': self.key
        }

        DB.update({'name': self.name}, {'$set': data}, upsert=True)
