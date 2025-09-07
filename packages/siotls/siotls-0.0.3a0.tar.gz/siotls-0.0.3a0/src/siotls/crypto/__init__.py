import importlib
import typing
from collections.abc import Collection
from os import getenv

from siotls.iana import CipherSuites, NamedGroup, SignatureScheme

if typing.TYPE_CHECKING or '/siotls/' in getenv('DOCUTILSCONFIG', ''):
    import _hashlib
    from collections.abc import Callable

    HashInstance: typing.TypeAlias = _hashlib.HASH
    HashFunction: typing.TypeAlias = Callable[..., _hashlib.HASH]
    """ A hash function from hashlib, e.g. ``hashlib.sha256``. """
else:
    HashFunction: typing.TypeAlias = typing.Any
    HashInstance: typing.TypeAlias = typing.Any

from .cipher_suites import TLSCipherSuite
from .key_exchanges import TLSKeyExchange
from .signature_schemes import SignatureKeyError, SignatureVerifyError, TLSSignatureScheme


def install(
    backend: str,
    iana_ids: Collection[CipherSuites | NamedGroup | SignatureScheme] | None = None,
    *,
    duplicate: typing.Literal['raise', 'skip', 'override'] = 'raise'
):
    """
    Install a crypto backend.

    :param backend: the name of the backend to install, it must be a
        package present in the ``siotls.crypto.backends`` namespace.
    :param iana_ids: a list of algorithms to install, to only install a
        subset of the algorithms available in the backend. Use ``None``
        to install them all.
    :param duplicate: may this function be called multiple times with
        various backends, what to do in case this installation attempt
        to install a algorithm that is installed already.

        ``"raise"`` (default):
            Raise a ``KeyError``

        ``"skip"``
            Keep the algorithm installed already.

        ``"override"``
            Replace the installed algorithm by he new one.
    """
    mod = importlib.import_module('.' + backend, 'siotls.crypto.backends')
    mod.install(iana_ids, duplicate=duplicate)
