''' Contains code related to game configuration '''

import yaml

class ConfigError(Exception):
    ''' Exception for configuration errors '''

class Config(): # pylint: disable=too-few-public-methods
    ''' In-memory representation of configuration on disk '''

    _single = None # Singleton instance.

    @classmethod
    def load(cls, loc='/game/config.yml'):
        ''' Creates and returns singleton instance '''

        if Config._single is None:
            cls._single = Config(loc)

        return cls._single

    def __init__(self, loc):
        with open(loc, 'r') as fil:
            self._config = yaml.load(fil, Loader=yaml.SafeLoader)

    def get(self, path):
        ''' Used to query for config element '''

        data = self._config
        try:
            parts = path.split('/')
            for part in parts:
                data = data[part]
        except (KeyError, TypeError):
            raise ConfigError('Failed to get path: {}'.format(path)) from None

        return data
