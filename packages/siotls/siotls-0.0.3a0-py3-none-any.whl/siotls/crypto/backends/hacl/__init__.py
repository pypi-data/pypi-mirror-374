import pyhacl  # type: ignore[import-untyped]

from .cipher_suites import *
from .key_exchanges import *
from .signature_schemes import *


def install(iana_ids=None, *, duplicate='raise'):
    for algo in globals().values():
        if (
            hasattr(algo, 'iana_id')
            if iana_ids is None
            else getattr(algo, 'iana_id', None) in iana_ids
        ):
            algo.install(duplicate=duplicate)
