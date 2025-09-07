"""
Some types alias.

.. _asn1crypto.x509.Certificate: https://github.com/wbond/asn1crypto/blob/1.5.1/asn1crypto/x509.py#L2144>
.. _asn1crypto.keys.PublicKeyInfo: https://github.com/wbond/asn1crypto/blob/1.5.1/asn1crypto/keys.py#L1060>
.. _asn1crypto.keys.PrivateKeyInfo: https://github.com/wbond/asn1crypto/blob/1.5.1/asn1crypto/keys.py#L696>
"""

import typing

__all__ = (
    'DerCertificate',
    'DerPrivateKey',
    'DerPublicKey',
    'PemCertificate',
    'PemCertificateChain',
    'PemPrivateKey',
    'PemPublicKey',
)

if typing.TYPE_CHECKING:
    # for mypy
    DerCertificate: typing.TypeAlias = bytes
    PemCertificate: typing.TypeAlias = bytes
    PemCertificateChain: typing.TypeAlias = bytes
    DerPrivateKey: typing.TypeAlias = bytes
    PemPrivateKey: typing.TypeAlias = bytes
    DerPublicKey: typing.TypeAlias = bytes
    PemPublicKey: typing.TypeAlias = bytes

else:
    # for broken sphinx autodoc...

    DerCertificate = typing.NewType('DerCertificate', bytes)
    """ A single DER-encoded `asn1crypto.x509.Certificate`_. """

    PemCertificate = typing.NewType('PemCertificate', bytes)
    """ A single PEM-encoded `asn1crypto.x509.Certificate`_. """

    PemCertificateChain = typing.NewType('PemCertificateChain', bytes)
    """ Multiple concatenated PEM-encoded `asn1crypto.x509.Certificate`_. """

    DerPrivateKey = typing.NewType('DerPrivateKey', bytes)
    """ A DER-encoded `asn1crypto.keys.PrivateKeyInfo`_. """

    PemPrivateKey = typing.NewType('PemPrivateKey', bytes)
    """ A PEM-encoded `asn1crypto.keys.PrivateKeyInfo`_. """

    DerPublicKey = typing.NewType('DerPublicKey', bytes)
    """ A DER-encoded `asn1crypto.keys.PublicKeyInfo`_. """

    PemPublicKey = typing.NewType('PemPublicKey', bytes)
    """ A PEM-encoded `asn1crypto.keys.PublicKeyInfo`_. """
