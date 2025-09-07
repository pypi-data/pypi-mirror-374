# copyright Julien Castiaux, Belgium, 2025, licensed under the EUPL
# https://interoperable-europe.ec.europa.eu/collection/eupl/eupl-text-eupl-12

import importlib.metadata
import logging

__version__ = importlib.metadata.version(__name__)

USER_AGENT = f'python-{__name__}/{__version__}'

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

key_logger = logger.getChild('keylog')
key_logger.propagate = False
key_logger.setLevel(logging.DEBUG)
key_logger.addHandler(logging.NullHandler())

class TLSError(Exception):
    pass

class TLSErrorGroup(ExceptionGroup, TLSError):  # noqa: N818
    pass

from .configuration import TLSConfiguration
from .connection import TLSConnection

# don't bloat dir(siotls) with useless stuff
del importlib.metadata
del logging
