''' Code related to user accounts '''

import base64
import random
import uuid

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import pymongo

import game.config as config
from game.monster import Monster

CONFIG = config.Config()
DB = pymongo.MongoClient('mongo', 27017).game.user

# Avoid accidental multiple occurrences, ie. if multiple creation
# attempts for same user in close occurrence. Overall, enforces
# unique 'name' field value, allowing us to use this as our unique
# identifier for the user.
DB.create_index([('name', pymongo.TEXT)], unique=True)

class BadAuthentication(Exception):
    ''' Bad authentication attempt '''

class User:
    ''' Represents a single user, and helpers for users '''

    @classmethod
    def get_user(cls, socket):
        ''' Communicates with client to verify user '''

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
            return User(user['name'], user['class'], user['key'],
                        user['hp'], user['str'])

        socket.send('Failed to complete challenge!')

        raise BadAuthentication('User did not fulfill challenge')

    @staticmethod
    def create_user(socket, name):
        ''' Communicates with client to create user '''

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

    # pylint: disable=too-many-arguments
    def __init__(self, name, cls, key, health=100, strength=10):
        self.cls = cls
        self.name = name
        self.key = key
        self.health = health
        self.strength = strength

    def lose(self, amount):
        ''' Subtracts an amount from health '''

        self.health = self.health - amount

    def hit(self):
        ''' Determines amount to hit '''

        return random.randrange(self.strength/2, self.strength)

    def save(self):
        ''' Saves current state of user to DB '''

        data = {
            'name': self.name,
            'class': self.cls,
            'key': self.key,
            'health': self.health,
            'strength': self.strength
        }

        DB.update({'name': self.name}, {'$set': data}, upsert=True)

    def battle(self, socket):
        ''' Carries out a battle against a monster

        Returns remaining user HP
        '''

        monster_config = random.choice(CONFIG.get('monster'))
        monster = Monster(monster_config['name'], monster_config['health'],
                          monster_config['strength'])

        while True:
            monster_dmg = monster.hit()
            self.lose(monster_dmg)
            self.save()
            socket.send_nl('{} inflicted {}, you have {} remaining'
                           .format(monster.name, monster_dmg, self.health))
            if self.health <= 0:
                break

            if socket.send_wait('Flee?').lower() == 'y':
                break

            dmg = self.hit()
            monster.lose(dmg)
            socket.send_nl('You inflicted {}, {} has {} remaining'
                           .format(dmg, monster.name, monster.health))
            if monster.health <= 0:
                break

            if socket.send_wait('Flee?').lower() == 'y':
                break

        return self.health
