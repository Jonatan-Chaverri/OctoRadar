"""
OctoRadarDaemon module runnable entry point.
"""

from sys import exit
from logging import (
    ERROR, WARNING, DEBUG, INFO,
    StreamHandler, getLogger, Formatter, basicConfig,
)

from setproctitle import setproctitle
from colorlog import ColoredFormatter

from .config import load
from .daemon import Daemon


log = getLogger(__name__)


COLOR_FORMAT = (
    '  {thin_white}{asctime}{reset} | '
    '{log_color}{levelname:8}{reset} | '
    '{thin_white}{name}{reset} | '
    '{log_color}{message}{reset}'
)
SIMPLE_FORMAT = (
    '  {asctime} | '
    '{levelname:8} | '
    '{name} | '
    '{message}'
)
LEVELS = {
    'error': ERROR,
    'warning': WARNING,
    'info': INFO,
    'debug': DEBUG,
}


def setup_logger(level, colorize):
    """
    Sets up the logger with the specified level and format.

    This function configures the logging module with a basic configuration.
    The log level and whether the output should be colorized can be customized.

    :param str level: The log level. This is a string that should be one of
     the keys in the LEVELS dictionary. If the level is not in the LEVELS
     dictionary, the log level is set to DEBUG.
    :param bool colorize: If True, the output will be colorized. If False,
     the output will not be colorized.

    :returns: None
    """
    level = LEVELS.get(level.lower(), DEBUG)

    if not colorize:
        formatter = Formatter(
            fmt=SIMPLE_FORMAT, style='{'
        )
    else:
        formatter = ColoredFormatter(
            fmt=COLOR_FORMAT, style='{'
        )

    handler = StreamHandler()
    handler.setFormatter(formatter)

    basicConfig(
        handlers=[handler],
        level=level,
    )


def main():
    """
    Package main function.

    :return: Exit code.
    :rtype: int
    """
    config = load()
    setup_logger(config.log.level, config.log.colorize)

    setproctitle('octoRadarDaemon')

    daemon = Daemon(config)
    daemon.run()

    return 0


if __name__ == '__main__':
    exit(main())


__all__ = [
    'main',
]
