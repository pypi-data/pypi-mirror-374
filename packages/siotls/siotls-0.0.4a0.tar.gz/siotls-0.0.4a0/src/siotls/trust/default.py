from threading import RLock

from siotls.asn1types import DerCertificate

from . import TrustStore, load_certifi_ca_certificates, load_system_ca_certificates

_lock = RLock()

_ca_certificates = None
def get_ca_certificates() -> list[DerCertificate]:
    """
    Load and save in cache a list of trusted root CA certificates.

    The loading order is as follow:

    #. :func:`~siotls.trust.load_system_ca_certificates`
    #. :func:`~siotls.trust.load_certifi_ca_certificates`

    It raises the error the last function rose when all functions
    failed.
    """
    global _ca_certificates  # noqa: PLW0603

    if _ca_certificates:
        return _ca_certificates
    with _lock:
        if not _ca_certificates:
            try:
                _ca_certificates = load_system_ca_certificates()
            except RuntimeError:
                _ca_certificates = load_certifi_ca_certificates()
    return _ca_certificates


_truststore = None
def get_truststore() -> TrustStore:
    """
    Instantiate and save in cache a concrete truststore.

    The loading order is as follow:

    #. :class:`~siotls.trust.backens.openssl.OpensslTrustStore`

    It raises the error the last function rose when all functions
    failed.
    """
    global _truststore  # noqa: PLW0603

    if not _truststore:
        with _lock:
            if not _truststore:
                from .backends.openssl import OpensslTrustStore  # noqa: PLC0415
                _truststore = OpensslTrustStore(get_ca_certificates())
    return _truststore
