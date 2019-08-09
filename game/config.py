''' Contains code related to game configuration '''

import yaml

class ConfigError(Exception):
    pass

class Config():
    def __init__(self, loc='/game/config.yml'):
        with open(loc, 'r') as fil:
            self._config = yaml.load(fil, Loader=yaml.SafeLoader)

    def get(self, path):
        data = self._config
        try:
            parts = path.split('/')
            for part in parts:
                data = data[part]
        except (KeyError, TypeError) as error:
            raise ConfigError('Failed to get path: {}'.format(path))

        return data
