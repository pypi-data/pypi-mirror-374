from threading import RLock

_lock = RLock()

_store = None
def get_default_store():
    global _store  # noqa: PLW0603
    from . import castore

    if _store:
        return _store
    with _lock:
        if not _store:
            try:
                _store = castore.get_system_ca_certificates()
            except RuntimeError:
                _store = castore.get_certifi_store()
    return _store


_trust = None
def get_default_trust():
    global _trust  # noqa: PLW0603

    if not _trust:
        with _lock:
            if not _trust:
                from .backends.openssl import X509Verifier
                _trust = X509Verifier(get_default_store())
    return _trust
