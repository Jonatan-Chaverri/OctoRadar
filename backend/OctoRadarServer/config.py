"""
Configuration loading module.
"""

from logging import getLogger

from pprintpp import pformat
from cerberus import Validator

from types import SimpleNamespace


log = getLogger(__name__)


SCHEMA_CONFIG = {
    "octoRadarServer": {
        "type": "dict",
        "schema": {
            "server": {
                "type": "dict",
                "schema": {
                    "host": {"type": "string"},
                    "port": {"type": "integer", "min": 1, "max": 65535},
                },
            },
            "databases": {
                "type": "dict",
                "schema": {
                    "mongodb": {
                        "type": "dict",
                        "schema": {
                            "host": {"type": "string"},
                            "port": {
                                "type": "integer", "min": 1, "max": 65535
                            },
                            "database": {"type": "string"},
                            "collections": {
                                "type": "dict",
                                "schema": {
                                    "organizations": {"type": "string"},
                                    "repositories": {"type": "string"},
                                },
                            },
                        },
                    },
                },
            },
            "log": {
                "type": "dict",
                "schema": {
                    "level": {
                        "type": "string", 
                        "allowed": [
                            "debug", "info", "warning", "error", "critical"
                        ]
                    },
                    "colorize": {"type": "boolean"},
                },
            },
        },
    },
}


def validate_definition(config):
    """
    Validate configuration against the schema.

    :param dict config: The configuration data structure to validate.

    :return: a dictionary with validated and coersed data.
    :rtype: dict

    :raises SyntaxError: If configuration fails to validate against the schema.
    """

    validator = Validator(SCHEMA_CONFIG)
    validated = validator.validated(config)

    if validated is None:
        log.critical(
            'Invalid configuration:\n{}'.format(
                pformat(validator.errors)
            )
        )
        raise SyntaxError('Invalid configuration')

    return validated


def recursive_dict_to_namespace(dict_obj):
    """
    Recursively converts a dictionary and all its nested dictionaries to
    SimpleNamespace objects.

    This function iterates over all items in the input dictionary. If an
    item's value is a dictionary, it recursively converts that dictionary
    to a SimpleNamespace object. Finally, it converts the input dictionary
    itself to a SimpleNamespace object.

    :param dict dict_obj: The dictionary to convert. This dictionary can
     contain other dictionaries, which will also be converted.

    :returns: The converted SimpleNamespace object.
    """
    for key, value in dict_obj.items():
        if isinstance(value, dict):
            dict_obj[key] = recursive_dict_to_namespace(value)
    return SimpleNamespace(**dict_obj)


def load():
    """
    Load package-wide configuration defaults from package and return it.

    :return: Package configuration defaults.
    :rtype: types.SimpleNamespace
    """
    from pkg_resources import resource_string
    from toml import loads

    content = resource_string(__name__, 'data/config.toml')
    definition = loads(content.decode('utf-8'))

    validated = validate_definition(definition)
    return recursive_dict_to_namespace(validated['octoRadarServer'])


__all__ = [
    'load',
]
