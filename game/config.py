''' Contains code related to game configuration '''

import yaml

class ConfigError(Exception):
    ''' Exception for configuration errors '''

class Config(): # pylint: disable=too-few-public-methods
    ''' In-memory representation of configuration on disk '''

    def __init__(self, loc='/game/config.yml'):
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
