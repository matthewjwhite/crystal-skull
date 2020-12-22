''' Contains code related to maps '''

from game.config import Config
from game.monster import Monster

#pylint: disable=too-few-public-methods
class Dim:
    ''' Represents map dimensions via X and Y min/max '''
    def __init__(self, x_min, x_max, y_min, y_max):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

    @staticmethod
    def from_cfg(**kwargs):
        ''' Convert configuration dimensions to Dim object '''

        data = {
            'x_min': kwargs['xMin'],
            'x_max': kwargs['xMax'],
            'y_min': kwargs['yMin'],
            'y_max': kwargs['yMax']
        }

        return Dim(**data)

    # pylint: disable=invalid-name
    def contains(self, x, y):
        ''' Tells us whether this map contains a certain point

        x and y should be grid (overall map) points, not relative
        '''

        return (self.x_min <= x <= self.x_max) and \
               (self.y_min <= y <= self.y_max)

class UnknownMap(Exception):
    ''' Unknown map, not in configuration '''

class Map:
    ''' Map '''

    def __init__(self, name, monsters, dim):
        self.name = name
        self.monsters = monsters
        self.dim = dim

    @staticmethod
    def from_cfg(**kwargs):
        ''' Converts configuration map to Map object '''

        data = {
            'name': kwargs['name'],
            'monsters': [ Monster.get(name)
                for name in kwargs['monsters'] ],
            'dim': Dim.from_cfg(**kwargs['dim'])
        }

        return Map(**data)

    @staticmethod
    def get(name):
        ''' Gets matching map '''

        try:
            return next(map for map in MAPS if map.name == name)
        except StopIteration:
            # Technically this should never happen, unless maps are removed from
            # the configuration. If it does happen, it should unwind all the way,
            # killing the Greenlet and closing the socket.
            raise UnknownMap('No map with name: {}'.format(name)) from None

    # pylint: disable=invalid-name
    @staticmethod
    def match(x, y):
        ''' Attempts to find a matching map given a set of coordinates

        x and y should be grid (overall map) points, not relative
        '''
        for curr in MAPS:
            if curr.dim.contains(x, y):
                return curr

        return None

# Maps loaded once and referenced from this to avoid unnecessary reloading.
MAPS = [ Map.from_cfg(**map) for map in Config.load().get('map') ]

class Location:
    ''' Represents location of user '''

    # pylint: disable=invalid-name
    def __init__(self, mp, x, y):
        ''' Location '''

        self.map = mp
        self.x = x
        self.y = y

    @staticmethod
    def from_db(**kwargs):
        ''' Converts database object to Location object '''

        data = {
            'mp': Map.get(kwargs['map']),
            'x': kwargs['x'],
            'y': kwargs['y']
        }

        return Location(**data)

    def to_db(self):
        ''' Converts Location object to database object '''

        data = {
            'map': self.map.name,
            'x': self.x,
            'y': self.y
        }

        return data
