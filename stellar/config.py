import os
import logging
import yaml
from schema import Use, Schema, SchemaError, Optional
from os.path import expanduser

class InvalidConfig(Exception):
    pass


class MissingConfig(Exception):
    pass


default_config = {
    'logging': 30,
    'migrate_from_0_3_2': True
}
schema = Schema({
    'stellar_url': Use(str),
    'url': Use(str),
    'project_name': Use(str),
    'tracked_databases': [Use(str)],
    Optional('logging'): int,
    Optional('migrate_from_0_3_2'): bool
})


def get_config_path():
    home_directory = expanduser("~/")
    while True:
        try:
            with open(
                os.path.join(home_directory, '.stellar.yaml'),
                'rb'
            ) as fp:
                return os.path.join(home_directory, '.stellar.yaml')
        except IOError:
            pass

        home_directory = os.path.abspath(
            os.path.join(home_directory, '..')
        )
        if home_directory == '/':
            return None


def load_config():
    config = {}
    home_directory = expanduser("~/")
    while True:
        try:
            with open(
                os.path.join(home_directory, '.stellar.yaml'),
                'rb'
            ) as fp:
                config = yaml.safe_load(fp)
                break
        except IOError:
            pass
        home_directory = os.path.abspath(
            os.path.join(home_directory, '..')
        )

        if home_directory == '/':
            break

    if not config:
        raise MissingConfig()

    for k, v in default_config.items():
        if k not in config:
            config[k] = v

    try:
        return schema.validate(config)
    except SchemaError as e:
        raise InvalidConfig(e)


def save_config(config):
    logging.getLogger(__name__).debug('save_config()')
    with open(get_config_path(), "w") as fp:
        yaml.dump(config, fp)
