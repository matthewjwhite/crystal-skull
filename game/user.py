''' Code related to user accounts '''

import base64
import copy
import random
import uuid

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import pymongo

from game.config import Config
from game.entity import Entity
from game.map import Location, Map
from game.constants import \
    DB_NAME, DB_STR, DB_KEY, DB_CLS, DB_HP, DB_LOC, \
    NAME, STR, KEY, CLS, HP, LOC

CONFIG = Config.load()
DB = pymongo.MongoClient('mongo', 27017).game.user

# Avoid accidental multiple occurrences, ie. if multiple creation
# attempts for same user in close occurrence. Overall, enforces
# unique 'name' field value, allowing us to use this as our unique
# identifier for the user.
DB.create_index([('name', pymongo.TEXT)], unique=True)

class BadAuthentication(Exception):
    ''' Bad authentication attempt '''

class BadMove(Exception):
    ''' Bad move when navigating '''

class User(Entity):
    ''' Represents a single user, and helpers for users '''

    # Starting location for all users.
    start_loc = Location(
        mp=Map.get('West Dungeon'), x=50, y=50)

    @staticmethod
    def from_db(**kwargs):
        ''' Converts database document to User object '''

        data = {
            NAME: kwargs[DB_NAME],
            CLS: kwargs[DB_CLS],
            KEY: kwargs[DB_KEY],
            HP: kwargs[DB_HP],
            STR: kwargs[DB_STR],
            LOC: Location.from_db(**kwargs[DB_LOC])
        }

        return User(**data)

    @classmethod
    def get_user(cls, socket):
        ''' Communicates with client to verify user '''

        name = socket.send_wait('Welcome! User?')
        if not DB.find({DB_NAME: name}).count():
            return cls.create_user(socket, name)

        # Instantiate RSA public key object.
        key = DB.find_one({DB_NAME: name})[DB_KEY].encode('utf-8')
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
            # DB field names match User constructor parameters.
            return User.from_db(**DB.find_one({DB_NAME: name}))

        socket.send('Failed to complete challenge!')

        raise BadAuthentication('User did not fulfill challenge')

    @classmethod
    def create_user(cls, socket, name):
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
        player_cls = socket.send_wait(msg)
        if player_cls not in classes:
            socket.send('Invalid class!')
            raise RuntimeError('Invalid class selected')

        user = User(name=name, cls=player_cls, key=key,
                    location=cls.start_loc)
        user.save()

        return user

    def __init__(self, cls, key, location, **kwargs):
        ''' Param names match constants.py '''

        self.cls = cls
        self.key = key
        self.location = location
        super().__init__(**kwargs)

    def to_db(self):
        ''' Translates object to DB document '''

        return {
            DB_NAME: self.name,
            DB_CLS: self.cls,
            DB_KEY: self.key,
            DB_HP: self.health,
            DB_STR: self.strength,
            DB_LOC: Location.to_db(self.location)
        }

    def save(self):
        ''' Saves current state of user to DB '''

        DB.update({DB_NAME: self.name}, {'$set': self.to_db()},
                  upsert=True)

    def battle(self, socket):
        ''' Carries out a battle against a monster

        Returns remaining user HP
        '''

        monster = copy.deepcopy(random.choice(self.location.map.monsters))

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

    def move(self, direction):
        ''' Moves user within current map or to another map '''
        curr_map = self.location.map
        next_x = self.location.x
        next_y = self.location.y
        direction = direction.lower()

        if direction == 'n':
            next_y += 1
        elif direction == 'e':
            next_x += 1
        elif direction == 's':
            next_y -= 1
        elif direction == 'w':
            next_x -= 1

        # Self location coordinates are relative with respect to the current
        # map, so they must be checked per the height/width as opposed to the
        # map's X and Y min/max, which indicate points in the overall grid.
        curr_map_width = curr_map.dim.x_max - curr_map.dim.x_min + 1
        curr_map_height = curr_map.dim.y_max - curr_map.dim.y_min + 1

        # -1 indicates going off the edge, left or downwards. If we hit the
        # width or height, we've gone off the edge right or upwards -
        # coordinates start at 0!
        if next_x in (-1, curr_map_width) or next_y in (-1, curr_map_height):
            # Next step will breach boundary. See if there is even anything
            # on the other side.
            match_map = Map.match(curr_map.dim.x_min + next_x, curr_map.dim.y_min + next_y)

            if match_map:
                new_rel_x = curr_map.dim.x_min + next_x - match_map.dim.x_min
                new_rel_y = curr_map.dim.y_min + next_y - match_map.dim.y_min

                self.location.map = match_map
                self.location.x = new_rel_x
                self.location.y = new_rel_y
            else:
                raise BadMove('At boundary with no neighboring map')
        else:
            # Still within boundary, so continue on within current map.
            self.location.x = next_x
            self.location.y = next_y
