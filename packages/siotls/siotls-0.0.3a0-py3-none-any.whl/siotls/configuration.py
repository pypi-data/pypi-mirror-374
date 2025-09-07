import dataclasses
import functools
import logging
import secrets
import typing
from collections.abc import Collection, Sequence
from types import EllipsisType

import asn1crypto.keys  # type: ignore[import-untyped]
import asn1crypto.x509  # type: ignore[import-untyped]

from siotls.asn1types import DerCertificate, DerPrivateKey, DerPublicKey
from siotls.crypto import (
    SignatureVerifyError,
    TLSCipherSuite,
    TLSKeyExchange,
    TLSSignatureScheme,
)
from siotls.iana import (
    ALPNProtocol,
    CertificateType,
    CipherSuites,
    MaxFragmentLengthOctets as MLFOctets,
    NamedGroup,
    SignatureScheme,
)
from siotls.trust import X509Verifier

logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class TLSConfiguration:
    """
    The TLSConfiguration class provides a comprehensive set of options
    to configure the security parameters for TLS connections, applicable
    to both clients and servers.

    It allows control over the cryptographic elements involved in the
    TLS handshake, including the selection of ciphers, key exchange
    methods, and signature algorithms. It also allows control over
    various TLS extensions such as Server Name Indication (SNI),
    Application-Layer Protocol Negotiation (ALPN) and others.

    **Client** On the client-side, the :attr:`x509verifier` parameter is
    recommended. It is used to authenticate the remote server. Leaving
    the parameter out makes the connection insecure. See the
    :mod:`siotls.trust` module for available trust backends.

    >>> minimal_client_config = TLSConfiguration(
    >>>     'client',
    >>>     x509verifier=siotls.trust.get_default_trust(),
    >>> )

    **Server** On the server-side, the :attr:`private_key` and
    :attr:`certificate_chain` parameters are mandatory.

    >>> minimal_server_config = TLSConfiguration(
    >>>     'server',
    >>>     private_key=...,
    >>>     certificate_chain=...,
    >>> )

    **Mutual TLS** Server authentication is mandatory by TLS. Client
    authentication (mutual TLS) is optional. Set the
    :attr:`x509verifier` server-side to request client authentication.
    Set the :attr:`private_key` and :attr:`certificate_chain` pair
    client-side to comply.

    **Raw Public Keys** The :attr:`x509verifier` and
    :attr:`certificate_chain` parameters are used for certificate
    authentication. It is possible to authenticate using raw public keys
    in addition to / instead of certificates. Set the :attr:`public_key`
    parameter server-side. Set the :attr:`trusted_public_keys` parameter
    client-side. Set the other parameter on the other side for mutual
    TLS using raw public keys.

    **Certificate Revocation** siotls doesn't perform any IO on its own,
    this poses a problem when validating certificates, as it must check
    with the CA that the peer's certificate has not been revoked. siotls
    delegates the communication with the CA to the user, via the
    :attr:`service`: a user provided class that is used to download
    certificates, certificate revocation lists and OCSP. An alternative
    is to make sure that the remote peer provide an OCSP stapling for
    all the certificates in its chain.
    """

    side: typing.Literal['client', 'server']
    """
    Tell whether this configuration will be used for client connections
    or server ones.
    """

    _: dataclasses.KW_ONLY

    cipher_suites: Sequence[CipherSuites] = (
        CipherSuites.TLS_CHACHA20_POLY1305_SHA256,
        CipherSuites.TLS_AES_256_GCM_SHA384,
        CipherSuites.TLS_AES_128_GCM_SHA256,
    )
    """
    List the cipher suites that can be used to encrypt data transmitted
    on the wire.

    If the peers cannot agree on a same cipher suite, the connection
    fails with a :class:`siotls.alerts.HandshakeFailure` fatal alert.

    The list should be ordered server-side in decreasing preference
    order, i.e. the prefered cipher should be first in the list. The
    order doesn't matter client-side.

    The default list follows the recommendations of Cryptographic Right
    Answers (Latacora 2018). It is further stripped down to only include
    the algorithms supported by the crypto backend.

    The negotiated cipher is available at
    :attr:`TLSNegotiatedConfiguration.cipher_suite`.
    """

    key_exchanges: Sequence[NamedGroup] = (
        NamedGroup.x25519,
        NamedGroup.secp256r1,
    )
    """
    List the allowed key exchange algorithms that can be used to share
    a secret and bootstrap encryption.

    If the peers cannot agree on a same key exchange algorithm, the
    connection fails with a :class:`siotls.alerts.HandshakeFailure`
    fatal alert.

    The list should be ordered server-side in decreasing preference
    order, i.e. the prefered algorithm should be first in the list. The
    order doesn't matter client-side.

    The default list follows the recommendations of Cryptographic Right
    Answers (Latacora 2018), with the addition of ``P-256`` because of
    its widespread usage. It is further stripped down to only include
    the algorithms supported by the crypto backend.

    The negotiated algorithm is available at
    :attr:`TLSConnection.nconfig.key_exchange`.
    """

    signature_algorithms: Sequence[SignatureScheme] = (
        SignatureScheme.ed25519,
        SignatureScheme.ecdsa_secp256r1_sha256,
        SignatureScheme.ecdsa_secp384r1_sha384,
        SignatureScheme.ecdsa_secp521r1_sha512,
        SignatureScheme.rsa_pss_rsae_sha256,
        SignatureScheme.rsa_pss_rsae_sha384,
        SignatureScheme.rsa_pss_rsae_sha512,
    )
    """
    List the signature algorithms the peer is allowed to use to
    authenticate itself. Mandatory client side, as the server
    always authenticates itself. Optional server side, required only for
    mutual TLS.

    The default list follows the recommendation of Cryptographic Right
    Answers (Latacora 2018), with the addition of the algorithms allowed
    by the TLS Baseline Requirements (CA/Browser Forum 2.1.5). It is
    further stripped down to only include the algorithms supported by
    the crypto backend.

    The negotiated algorithm are available at
    :attr:`TLSConnection.nconfig.peer_signature_algorithm` and
    :attr:`TLSConnection.nconfig.signature_algorithm`.
    """

    x509verifier: X509Verifier | None = None
    """
    Make peer authentication mandatory. Allow the peer to authenticate
    using x509 certificates.

    The service used to verify a x509 certificate chain. See the
    :mod:`siotls.trust` module for more details.
    """

    trusted_public_keys: Collection[DerPublicKey] = ()
    """
    Negotiate :rfc:`7250#` (Raw Public Keys).

    Make peer authentication mandatory. Allow the peer to authenticate
    using raw public keys.

    When used in addition to :attr:`x509verifier`, it allows the peer to
    authenticate with either x509 (preferred) or raw public keys. When
    used instead of :attr:`x509verifier`, it only allows raw public keys
    and will reject x509 certificates with an
    :class:`~siotls.contents.alerts.UnsupportedCertificate` error.
    """

    private_key: DerPrivateKey | None = None
    """
    The private key counter part of :attr:`public_key` and the public
    key found inside the first :attr:`certificate_chain`. Mandatory
    server side, optional client-side (but a server might require for
    mutual TLS).
    """

    public_key: DerPublicKey | None = None
    """
    Negotiate :rfc:`7250#` (Raw Public Keys).

    The public key counter part of :attr:`private_key`. Allow this side
    to authenticate using raw public keys.

    When used in addition to :attr:`certificate_chain`, it will send
    either the certificate chain, either the public key, depending on
    the peer's negotiated preference. When used instead of
    :attr:`certificate_chain`, it will either send the public key,
    either fail with an
    :class:`~siotls.contents.alerts.UnsupportedCertificate` error,
    depending on the peer's support for raw public keys.
    """

    certificate_chain: Sequence[DerCertificate] = ()
    """
    The list of certificates that together form a chain of trust between
    the host certificate and a trusted root certificate. Make this side
    authenticate using x509 certificates.

    The first certificate in the list must be the certificate of the
    current host. The following certificates each should sign the one
    preceding. The last certificate should be signed by a trusted root
    certificate, or be a trusted root certificate directly.
    """

    # extensions
    max_fragment_length: MLFOctets = MLFOctets.MAX_16384
    """
    Negociate :rfc:`6066#section-4` (Maximum Fragment Length)

    Limit the length of data encapsuled by TLS, fragmenting the data
    over multiple records when necessary. The limit only accounts for
    the fragment length and does not account for the additional 5 bytes
    record header.

    This doesn't limit the size of the internal buffers used by siotls
    which can grow up to 24 MiB during handshake after defragmentation.

    The negotiated length is available at
    :attr:`TLSNegotiatedConfiguration.max_fragment_length`.
    """

    alpn: Sequence[ALPNProtocol | bytes] = ()
    """
    Negociate :rfc:`7301#` (Application-Layer Protocol Negociation/ALPN).

    List the protocols that this application is willing to use once the
    connection is secured.

    The list should be ordered server-side in decreasing preference
    order, i.e. the prefered protocol should be first in the list.

    The negotiated protocol is available at
    :attr:`TLSNegotiatedConfiguration.alpn`.
    """

    # extra
    log_keys: bool = False
    """
    Enable key logging for netword analysis tools such as wireshark.

    Setting this value ``True`` is not enough to enable key logging, the
    ``siotls.keylog`` logger must be configured too.
    """

    @functools.cached_property
    def asn1_public_key(self) -> asn1crypto.keys.PublicKeyInfo:
        """
        The public key loaded from :attr:`public_key` or
        :attr:`certificate_chain` as a asn1crypto object, or ``None`` if
        neither attribute is set.
        """
        if self.public_key:
            return asn1crypto.keys.PublicKeyInfo.load(self.public_key)
        if self.certificate_chain:
            return self.asn1_certificate_chain[0].public_key
        return None

    @functools.cached_property
    def asn1_private_key(self) -> asn1crypto.keys.PrivateKeyInfo:
        """
        The :attr:`private_key` loaded as a asn1crypto object, or
        ``None`` if there is not private key.
        """
        if self.private_key is None:
            return None
        return asn1crypto.keys.PrivateKeyInfo.load(self.private_key)

    @functools.cached_property
    def asn1_certificate_chain(self) -> Sequence[asn1crypto.x509.Certificate]:
        """
        The :attr:`certificate_chain` loaded as a list of asn1crypto
        objects, the list is empty when there are no certificates.
        """
        return [
            asn1crypto.x509.Certificate.load(der_cert)
            for der_cert in self.certificate_chain
        ]

    @functools.cached_property
    def asn1_trusted_public_keys(self) -> Collection[asn1crypto.keys.PublicKeyInfo]:
        """
        The :attr:`trusted_public_keys` loaded as a list of asn1crypto
        objects, the list is empty when there are no trusted public
        keys.
        """
        return [
            asn1crypto.keys.PublicKeyInfo.load(public_key)
            for public_key in self.trusted_public_keys
        ]

    @property
    def require_peer_authentication(self) -> bool:
        """
        Whether to verify the peer's authenticity, via a certificate
        and/or a raw public key. Determined on both :attr:`x509verifier`
        and :attr:`trusted_public_keys`.

        Client-side this property dictates if we should process or
        ignore the certificate or raw public key sent by the server.

        Server-side this property dictates if the server will request
        and process a client certificate or raw public key.
        """
        # TODO: maybe adapt this docstring for Post Handshake Auth
        return bool(self.x509verifier or self.trusted_public_keys)

    @functools.cached_property
    def certificate_types(self) -> Sequence[CertificateType]:
        """
        The certificate types this side of the connection can offer:

        * ``X509`` when :attr:`certificate_chain` is set.
        * ``RAW_PUBLIC_KEY`` when :attr:`public_key` is set.
        """
        types = []  # order is important, x509 must be first
        if self.certificate_chain:
            types.append(CertificateType.X509)
        if self.public_key:
            types.append(CertificateType.RAW_PUBLIC_KEY)
        return types

    @functools.cached_property
    def peer_certificate_types(self) -> Sequence[CertificateType]:
        """
        The certificate types this side of the connection can process if
        offered by the peer:

        * ``X509`` when :attr:`x509verifier` is set.
        * ``RAW_PUBLIC_KEY`` when :attr:`trusted_public_keys` is set.
        """
        types = []  # order is important, x509 must be first
        if self.x509verifier:
            types.append(CertificateType.X509)
        if self.trusted_public_keys:
            types.append(CertificateType.RAW_PUBLIC_KEY)
        return types

    @property
    def other_side(self) -> typing.Literal['client', 'server']:
        """ The side of the peer. """
        return 'server' if self.side == 'client' else 'client'

    def __post_init__(self):
        self._check_mandatory_settings()
        if self.side == 'server':
            self._check_server_settings()
        else:
            self._check_client_settings()

        self._load_asn1_objects()
        if self.certificate_chain:
            self._check_certificate_chain()
        if self.public_key:
            self._check_public_key()

    def _check_mandatory_settings(self):
        e_empty_registry = "No %s available, surely because no crypto backend is installed."
        e_empty_registry_note = (
            "Install a backend using pip and then configure siotls to use it:\n"
            "$ pip install siotls[openssl]\n"
            ">>> siotls.crypto.install('openssl')"
        )
        e_no_algorithm = f"at least one {type(self).__name__}.%s must be provided"
        e_algo_unavailable = (
            "the following algorithms are not available with the "
            "installed crypto backend, and must be removed from the "
            "configuration:\n  "
        )

        for attr, registry in (
            ('cipher_suites', TLSCipherSuite),
            ('key_exchanges', TLSKeyExchange),
            ('signature_algorithms', TLSSignatureScheme),
        ):
            name = attr.replace('_', ' ').removesuffix('s')
            if not registry:
                exc = RuntimeError(e_empty_registry % name)
                exc.add_note(e_empty_registry_note)
                raise exc
            algos = getattr(self, attr)
            if not algos:
                raise ValueError(e_no_algorithm % attr)
            elif algos is getattr(type(self), attr):
                # filter the default algorithms to only keep those that
                # are available in the crypto backed
                object.__setattr__(self, attr, tuple(
                    a for a in algos if a in registry
                ))
            elif unavailable := [a for a in algos if a not in registry]:
                raise ValueError(e_algo_unavailable + '\n  '.join(map(repr, unavailable)))

    def _check_server_settings(self):
        if self.max_fragment_length != MLFOctets.MAX_16384:
            e = "max fragment length is only configurable client side"
            raise ValueError(e)
        if not self.private_key:
            e = "a private key is mandatory server side"
            raise ValueError(e)
        if not (self.certificate_chain or self.public_key):
            e = "a certificate chain or a public key is mandatory server side"
            raise ValueError(e)
        if self.require_peer_authentication:
            m =("a x509verifier and/or a list of trusted public keys "
                "is provided, client certificates will be requested")
            logger.info(m)

    def _check_client_settings(self):
        if not self.require_peer_authentication:
            w =("missing x509verifier or list of trusted public keys, "
                "will not verify the peer's certificate")
            logger.warning(w)

    def _check_certificate_chain(self):
        if not self.private_key:
            e = "certificate chain provided but private key missing"
            raise ValueError(e)

        pubkey_algo = self.asn1_public_key['algorithm']
        suites = TLSSignatureScheme.for_key_algo(pubkey_algo)
        if not suites:
            e =("the crypto backend doesn't support the public key "
                "extracted from the first certificate")
            raise ValueError(e)

        token = secrets.token_bytes()
        suite = suites[0](
            public_key=self.asn1_public_key.dump(),
            private_key=self.private_key,
        )
        try:
            suite.verify(suite.sign(token), token)
        except SignatureVerifyError as exc:
            e =("the public key found in the first certificate is not "
                "the counter part of the private key")
            raise ValueError(e) from exc

    def _check_public_key(self):
        if not self.private_key:
            e = "public key provided but private key missing"
            raise ValueError(e)

        pubkey_algo = self.asn1_public_key['algorithm']
        suites = TLSSignatureScheme.for_key_algo(pubkey_algo)
        if not suites:
            e =("the crypto backend doesn't support the public key")
            raise ValueError(e)

        token = secrets.token_bytes()
        suite = suites[0](public_key=self.public_key, private_key=self.private_key)
        try:
            suite.verify(suite.sign(token), token)
        except SignatureVerifyError:
            e = "the public key is not the counter part of the private key"
            raise ValueError(e) from None

    def _load_asn1_objects(self):
        # ruff: noqa: B018
        self.asn1_certificate_chain
        self.asn1_private_key
        self.asn1_public_key
        self.asn1_trusted_public_keys


@dataclasses.dataclass(init=False)
class TLSNegotiatedConfiguration:
    """ The values agreed by both peers on a specific connection. """

    # All those attributes are manually documented inside configurat.rst
    cipher_suite: CipherSuites | None
    key_exchange: NamedGroup | None
    signature_algorithm: SignatureScheme | None
    alpn: ALPNProtocol | None | EllipsisType
    max_fragment_length: MLFOctets | None
    client_certificate_type: CertificateType | None
    server_certificate_type: CertificateType | None
    peer_signature_algorithm: SignatureScheme | None
    peer_certificate_chain: Sequence[DerCertificate] | None
    peer_public_key: DerPublicKey | None

    def __init__(self):
        object.__setattr__(self, '_frozen', False)
        self.cipher_suite = None
        self.key_exchange = None
        self.signature_algorithm = None
        self.alpn = ...  # None is part of the domain, using Ellipsis as "not set" value
        self.max_fragment_length = None
        self.client_certificate_type = None
        self.server_certificate_type = None
        self.peer_signature_algorithm = None
        self.peer_certificate_chain = None
        self.peer_public_key = None

    @property
    def peer_asn1_certificate_chain(self) -> Sequence[asn1crypto.x509.Certificate] | None:
        """
        The :attr:`peer_certificate_chain` loaded as a list of
        asn1crypto objects, the list is empty when there are no
        certificates.
        """
        if self.peer_certificate_chain is None:
            return None
        return [
            asn1crypto.x509.Certificate.load(cert_der)
            for cert_der in self.peer_certificate_chain
        ]

    @property
    def peer_asn1_public_key(self) -> asn1crypto.keys.PublicKeyInfo | None:
        """
        The public key loaded from :attr:`peer_public_key` or
        :attr:`peer_certificate_chain` as a asn1crypto object, or
        ``None`` if neither attribute is set.
        """
        if self.peer_public_key:
            return asn1crypto.keys.PublicKeyInfo.load(self.peer_public_key)
        if self.peer_certificate_chain:
            return self.peer_asn1_certificate_chain[0].public_key  # type: ignore[index]
        return None

    def freeze(self):
        if self.peer_certificate_chain is not None:
            self.peer_certificate_chain = tuple(self.peer_certificate_chain)
        self._frozen = True

    def __setattr__(self, attr, value):
        if self._frozen:
            e = f"cannot assign attribute {attr!r}: frozen instance"
            raise dataclasses.FrozenInstanceError(e)
        super().__setattr__(attr, value)

    def __delattr__(self, attr):
        e = f"cannot delete attribute of type {type(self).__name__!r}"
        raise TypeError(e)

    def copy(self):
        copy = type(self)()
        copy.cipher_suite = self.cipher_suite
        copy.key_exchange = self.key_exchange
        copy.signature_algorithm = self.signature_algorithm
        copy.alpn = self.alpn
        copy.max_fragment_length = self.max_fragment_length
        copy.client_certificate_type = self.client_certificate_type
        copy.server_certificate_type = self.server_certificate_type
        copy.peer_signature_algorithm = self.peer_signature_algorithm
        copy.peer_certificate_chain = self.peer_certificate_chain
        copy.peer_public_key = self.peer_public_key
        return copy
