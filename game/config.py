''' Contains code related to game configuration '''

import yamale

class ConfigError(Exception):
    ''' Exception for configuration errors '''

class Config(): # pylint: disable=too-few-public-methods
    ''' In-memory representation of configuration on disk '''

    _single = None # Singleton instance.

    @classmethod
    def load(cls, loc='/game/config.yml', schema_loc='/game/schema.yml'):
        ''' Creates and returns singleton instance '''

        if Config._single is None:
            cls._single = Config(loc, schema_loc)

        return cls._single

    def __init__(self, loc, schema_loc):
        # Load configuration YAML and schema files.
        try:
            config = yamale.make_data(loc)
            schema = yamale.make_schema(schema_loc)
        except OSError as error:
            raise ConfigError('Unable to read file') from error

        # Validate structure of YAML file.
        try:
            yamale.validate(schema, config)
        except ValueError as error:
            raise ConfigError('Configuration deviates from schema') from error

        self._config = config[0][0]

        # Validate non-structural information.
        monster_names = [ monster['name'] for monster in self._config['monster'] ]
        for mp in self._config['map']: #pylint: disable=invalid-name
            if [ monster_name for monster_name in mp['monsters'] \
                     if monster_name not in monster_names ]:
                raise ConfigError('One or more map-referenced monsters not defined')

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
