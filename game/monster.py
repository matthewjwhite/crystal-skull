''' Contains code related to monsters '''

from game.constants import \
    DB_NAME, DB_STR, DB_HP, NAME, STR, HP
from game.entity import Entity
from game.config import Config

class UnknownMonster(Exception):
    ''' Unknown monster, not in configuration '''

class Monster(Entity):
    ''' Monster '''

    @staticmethod
    def from_cfg(**kwargs):
        ''' Converts configuration monster to Monster object '''

        data = {
            NAME: kwargs[DB_NAME],
            STR: kwargs[DB_STR],
            HP: kwargs[DB_HP]
        }

        return Monster(**data)

    @staticmethod
    def get(name):
        ''' Gets matching monster '''

        try:
            return next(monster for monster in MONSTERS if monster.name == name)
        except StopIteration:
            # Technically this should never happen, unless monsters are removed from
            # the configuration. If it does happen, it should unwind all the way, killing
            # the Greenlet and closing the socket.
            raise UnknownMonster('No monster with name: {}'.format(name)) from None

MONSTERS = [ Monster.from_cfg(**monster) for monster in Config.load().get('monster') ]
