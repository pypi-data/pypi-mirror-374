# Copyright (c) Julien Castiaux
#
# This software is made available under the terms of *either* of the
# licenses found in LICENSE.APACHE or LICENSE.BSD. Contributions to
# siotls are made under the terms of *both* these licenses.

"""
Sans-IO Python implementation of the TLS 1.3 (RFC 8446) protocol stack.
"""

import importlib.metadata
import logging

__all__ = [
    'USER_AGENT',
    'TLSConfiguration',
    'TLSConnection',
    'TLSError',
    'TLSErrorGroup',
    '__version__',
    'key_logger',
    'logger',
]

__version__ = importlib.metadata.version(__name__)

USER_AGENT = f'python-{__name__}/{__version__}'

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

key_logger = logger.getChild('keylog')
key_logger.propagate = False
key_logger.setLevel(logging.DEBUG)
key_logger.addHandler(logging.NullHandler())

class TLSError(Exception):
    """ Top-exception class for all exceptions defined by siotls. """

class TLSErrorGroup(ExceptionGroup, TLSError):  # noqa: N818
    """ Top-exception class for all exception groups defined by siotls. """

from .configuration import TLSConfiguration
from .connection import TLSConnection
