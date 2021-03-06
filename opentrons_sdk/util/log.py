import logging
from logging.config import dictConfig
import os

import opentrons_sdk


logging_config = dict(
    version=1,
    formatters={
        'basic': {
            'format': '%(asctime)s %(name)s %(levelname)-8s %(message)s'}
    },
    handlers={
        'debug': {'class': 'logging.StreamHandler',
                  'formatter': 'basic',
                  'level': logging.DEBUG},
        'testing': {'class': 'logging.StreamHandler',
                    'formatter': 'basic',
                    'level': logging.WARNING},
        },
    root={
        'handlers': ['testing'],
        'level': logging.ERROR,
        },
    )
dictConfig(logging_config)


def set_log_file(filename):
    """
    Convenience method to set a log file along with default parameters
    provided by this module.

    logging.basicConfig can always be used on its own to specify any logging
    conditions desired.
    """
    pass


def debug(system, message):
    logging.debug("[{}] {}".format(system, message))


def info(system, message):
    logging.info("[{}] {}".format(system, message))


def error(system, message):
    logging.error("[{}] {}".format(system, message))


def warn(system, message):
    logging.warning("[{}] {}".format(system, message))


log_path = os.path.join(
    os.path.dirname(opentrons_sdk.__file__),
    '..',
    'logs'
)

if os.path.isdir(log_path):
    set_log_file(os.path.join(log_path, 'opentrons.log'))
