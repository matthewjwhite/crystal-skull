''' Contains code related to monsters '''

from game.constants import \
    DB_NAME, DB_STR, DB_HP, NAME, STR, HP
from game.entity import Entity

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
