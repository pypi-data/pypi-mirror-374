from logging import getLogger
from logging.config import dictConfig as configure_logging

from .. import __version__ as version
from ..logging_conf import logging_configuration

configure_logging(logging_configuration)

logger = getLogger(__name__)


def main() -> None:
    print(f"Hello from ci-starter version {version}!")
    logger.debug("Hello from log")
