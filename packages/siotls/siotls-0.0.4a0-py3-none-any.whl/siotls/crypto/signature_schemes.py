import abc
from collections import defaultdict
from collections.abc import Collection
from typing import ClassVar

import asn1crypto.algos  # type: ignore[import-untyped]
import asn1crypto.keys  # type: ignore[import-untyped]

from siotls import TLSError
from siotls.asn1types import DerPrivateKey, DerPublicKey
from siotls.iana import SignatureScheme
from siotls.oid import (
    EllipticCurveOID,
    HashOID,
    PublicKeyAlgorithmOID,
    SignatureAlgorithmOID,
)
from siotls.utils import RegistryMeta


class SignatureKeyError(TLSError):
    """ A private key or public key is invalid. """


class SignatureSignError(TLSError):
    """ There was a problem signing a message. """


class SignatureVerifyError(TLSError):
    """ The signature doesn't match. """


class ISign(metaclass=abc.ABCMeta):
    """
    Interface that must be implemented by every concrete signature
    scheme.
    """

    @abc.abstractmethod
    def __init__(
        self,
        *,
        public_key: DerPublicKey | None = None,
        private_key: DerPrivateKey | None = None,
    ):
        """
        Initialize a new scheme with either a public key, a private key
        or both.

        :param public_key: a DER-encoded SubjectPublicKeyInfo_ ASN.1
            type, or ``None``. Usually the public key of the peer.
        :param private_key: a DER-encoded PrivateKeyInfo_ ASN.1 type, or
            ``None``. Usually our private key.

        :raise SignatureKeyError: When any of the key is invalid.

        .. _SubjectPublicKeyInfo: https://datatracker.ietf.org/doc/html/rfc5280#section-4.1.2.7
        .. _PrivateKeyInfo: https://datatracker.ietf.org/doc/html/rfc5208#section-5
        """
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def sign(self, message: bytes) -> bytes:
        """
        Sign a message using the private key.

        :param message: The message to sign.
        :return: A signature. Each algorithm has its own way of
            serializing it. RSA and EdDSA generate a single value. ECDSA
            generates two values that are stored in a DER-encoded
            Dss-Sig-Value_ ASN.1 type.
        :raise SignatureSignError: When is was not possible to produce
            a signature.

        .. _Dss-Sig-Value: https://datatracker.ietf.org/doc/html/rfc3279#section-2.2
        """
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def verify(self, signature: bytes, message: bytes) -> None:
        """
        Verify a signature using the public key.

        :param signature: The signature of the message.
        :param message: The message that is signed.
        :raise SignatureVerifyError: When the signature doesn't match.
        """
        raise NotImplementedError  # pragma: no cover


class TLSSignatureScheme(ISign, metaclass=RegistryMeta):
    """
    Abstract base class and registry for :class:`siotls.iana.SignatureScheme`.
    """
    _registry_key = '_signature_iana_registry'
    _signature_iana_registry: ClassVar = {}
    _signature_sign_oid_registry: ClassVar = defaultdict(list)
    _signature_pubkey_oid_registry: ClassVar = defaultdict(list)

    @classmethod
    def install(cls, *, duplicate='raise'):  # pragma: no cover
        """
        Install this signature scheme in the registry.

        Called by :func:`siotls.crypto.install` which is the preferred
        way of installing signature schemes.
        """
        other_cls = cls._signature_iana_registry.get(cls.iana_id)
        if other_cls:
            match duplicate:
                case 'skip':
                    return
                case 'override':
                    cls._signature_sign_oid_registry[cls.sign_oid].remove(other_cls)
                    cls._signature_pubkey_oid_registry[cls.pubkey_oid].remove(other_cls)
                case 'raise':
                    exc = KeyError(cls.iana_id)
                    exc.add_note(f"cannot install {cls} as {other_cls} "
                                 f"is installed already")
                    raise exc
                case _:
                    e = f"not one of 'raise', 'skip', or 'override': {duplicate}"
                    raise ValueError(e)
        cls._signature_iana_registry[cls.iana_id] = cls
        cls._signature_sign_oid_registry[cls.sign_oid].append(cls)
        cls._signature_pubkey_oid_registry[cls.pubkey_oid].append(cls)

    iana_id: SignatureScheme
    sign_oid: SignatureAlgorithmOID
    pubkey_id: PublicKeyAlgorithmOID

    @classmethod
    def for_signature_algo(
        cls,
        asn1_signature_algo: asn1crypto.algos.SignedDigestAlgorithm
    ):
        """
        Find the :class:`TLSSignatureScheme` that can verify a
        certificate.

        :param asn1_signature_algo: the ``signatureAlgorithm`` field of
            a certificate.
        :rtype: A concrete :class:`TLSSignatureScheme`.
        """
        sign_oid = SignatureAlgorithmOID(asn1_signature_algo['algorithm'].dotted)
        Suites = cls._signature_sign_oid_registry[sign_oid]
        if sign_oid == SignatureAlgorithmOID.RSASSA_PSS:
            hash_algo = asn1_signature_algo['parameters']['hash_algorithm']
            hash_oid = HashOID(hash_algo['algorithm'].dotted)
            Suites = [Suite for Suite in Suites if Suite.hash_oid == hash_oid]
        if len(Suites) == 1:
            return Suites[0]
        if not Suites:
            exc = KeyError(sign_oid)
            exc.add_note(f"no tls suite installed for {sign_oid!r}")
            raise exc
        exc = KeyError(sign_oid)
        exc.add_note(f"too many tls suite installed for {sign_oid!r}: {Suites}")
        raise exc

    @classmethod
    def for_key_algo(
        cls,
        asn1_key_algo: asn1crypto.keys.PrivateKeyAlgorithm
                     | asn1crypto.keys.PublicKeyAlgorithm
    ) -> Collection:
        """
        Find the (potentialyl many) :class:`TLSSignatureScheme` that
        correspond to the given public or private key algorithm.

        The list can me empty if no signature scheme is installed for
        the given key algorithm.

        The list can holds multiple values, shall a single key algorithm
        be compatible with many signature schemes (usually the case for
        RSA).

        :param asn1_key_algo: The ``algorithm`` field of a public or
            private key.
        :rtype: A list of concrete :class:`TLSSignatureScheme`.
        """
        # asn1_certificate.public_key['algorithm']
        pubkey_oid = PublicKeyAlgorithmOID(asn1_key_algo['algorithm'].dotted)
        Suites = cls._signature_pubkey_oid_registry[pubkey_oid]
        if pubkey_oid == PublicKeyAlgorithmOID.EC_PUBLIC_KEY:
            curve_oid = EllipticCurveOID(asn1_key_algo['parameters'].chosen.dotted)
            Suites = [Suite for Suite in Suites if Suite.curve_oid == curve_oid]
        return Suites


class RsaPkcs1Sha256Mixin:
    """
    Mixin for RSASSA PKCS1 v1.5 with a SHA256 digest.

    This mixin can be inherited by crypto backends to feed all the
    attributes required by :class:`TLSSignatureScheme` that are specific
    to :attr:`~siotls.iana.SignatureScheme.rsa_pkcs1_sha256`.

    Specifically, this mixin has values for:
    :attr:`~TLSKeyExchange.iana_id`,
    :attr:`~TLSKeyExchange.sign_oid`, and
    :attr:`~TLSKeyExchange.pubkey_oid`.
    """
    iana_id = SignatureScheme.rsa_pkcs1_sha256
    sign_oid = SignatureAlgorithmOID.RSA_WITH_SHA256
    pubkey_oid = PublicKeyAlgorithmOID.RSAES_PKCS1_v1_5

class RsaPkcs1Sha384Mixin:
    """
    Mixin for RSASSA PKCS1 v1.5 with a SHA384 digest.

    This mixin can be inherited by crypto backends to feed all the
    attributes required by :class:`TLSSignatureScheme` that are specific
    to :attr:`~siotls.iana.SignatureScheme.rsa_pkcs1_sha384`.

    Specifically, this mixin has values for:
    :attr:`~TLSKeyExchange.iana_id`,
    :attr:`~TLSKeyExchange.sign_oid`, and
    :attr:`~TLSKeyExchange.pubkey_oid`.
    """
    iana_id = SignatureScheme.rsa_pkcs1_sha384
    sign_oid = SignatureAlgorithmOID.RSA_WITH_SHA384
    pubkey_oid = PublicKeyAlgorithmOID.RSAES_PKCS1_v1_5

class RsaPkcs1Sha512Mixin:
    """
    Mixin for RSASSA PKCS1 v1.5 with a SHA512 digest.

    This mixin can be inherited by crypto backends to feed all the
    attributes required by :class:`TLSSignatureScheme` that are specific
    to :attr:`~siotls.iana.SignatureScheme.rsa_pkcs1_sha512`.

    Specifically, this mixin has values for:
    :attr:`~TLSKeyExchange.iana_id`,
    :attr:`~TLSKeyExchange.sign_oid`, and
    :attr:`~TLSKeyExchange.pubkey_oid`.
    """
    iana_id = SignatureScheme.rsa_pkcs1_sha512
    sign_oid = SignatureAlgorithmOID.RSA_WITH_SHA512
    pubkey_oid = PublicKeyAlgorithmOID.RSAES_PKCS1_v1_5

class RsaPssRsaeSha256Mixin:
    """
    Mixin for RSASSA PSS with a ``rsaEncryption`` public key OID and a
    SHA256 digest.

    This mixin can be inherited by crypto backends to feed all the
    attributes required by :class:`TLSSignatureScheme` that are specific
    to :attr:`~siotls.iana.SignatureScheme.rsa_pss_rsae_sha256`.

    Specifically, this mixin has values for:
    :attr:`~TLSKeyExchange.iana_id`,
    :attr:`~TLSKeyExchange.sign_oid`, and
    :attr:`~TLSKeyExchange.pubkey_oid`.
    """
    iana_id = SignatureScheme.rsa_pss_rsae_sha256
    sign_oid = SignatureAlgorithmOID.RSASSA_PSS
    pubkey_oid = PublicKeyAlgorithmOID.RSAES_PKCS1_v1_5

class RsaPssRsaeSha384Mixin:
    """
    Mixin for RSASSA PSS with a ``rsaEncryption`` public key OID and a
    SHA384 digest.

    This mixin can be inherited by crypto backends to feed all the
    attributes required by :class:`TLSSignatureScheme` that are specific
    to :attr:`~siotls.iana.SignatureScheme.rsa_pss_rsae_sha384`.

    Specifically, this mixin has values for:
    :attr:`~TLSKeyExchange.iana_id`,
    :attr:`~TLSKeyExchange.sign_oid`, and
    :attr:`~TLSKeyExchange.pubkey_oid`.
    """
    iana_id = SignatureScheme.rsa_pss_rsae_sha384
    sign_oid = SignatureAlgorithmOID.RSASSA_PSS
    pubkey_oid = PublicKeyAlgorithmOID.RSAES_PKCS1_v1_5

class RsaPssRsaeSha512Mixin:
    """
    Mixin for RSASSA PSS with a ``rsaEncryption`` public key OID and a
    SHA512 digest.

    This mixin can be inherited by crypto backends to feed all the
    attributes required by :class:`TLSSignatureScheme` that are specific
    to :attr:`~siotls.iana.SignatureScheme.rsa_pss_rsae_sha512`.

    Specifically, this mixin has values for:
    :attr:`~TLSKeyExchange.iana_id`,
    :attr:`~TLSKeyExchange.sign_oid`, and
    :attr:`~TLSKeyExchange.pubkey_oid`.
    """
    iana_id = SignatureScheme.rsa_pss_rsae_sha512
    sign_oid = SignatureAlgorithmOID.RSASSA_PSS
    pubkey_oid = PublicKeyAlgorithmOID.RSAES_PKCS1_v1_5

class RsaPssPssSha256Mixin:
    """
    Mixin for RSASSA PSS with a ``RSASSA-PSS`` public key OID and a
    SHA256 digest.

    This mixin can be inherited by crypto backends to feed all the
    attributes required by :class:`TLSSignatureScheme` that are specific
    to :attr:`~siotls.iana.SignatureScheme.rsa_pss_rsae_sha256`.

    Specifically, this mixin has values for:
    :attr:`~TLSKeyExchange.iana_id`,
    :attr:`~TLSKeyExchange.sign_oid`, and
    :attr:`~TLSKeyExchange.pubkey_oid`.
    """
    iana_id = SignatureScheme.rsa_pss_pss_sha256
    sign_oid = SignatureAlgorithmOID.RSASSA_PSS
    pubkey_oid = PublicKeyAlgorithmOID.RSASSA_PSS
    hash_oid = HashOID.sha256

class RsaPssPssSha384Mixin:
    """
    Mixin for RSASSA PSS with a ``RSASSA-PSS`` public key OID and a
    SHA384 digest.

    This mixin can be inherited by crypto backends to feed all the
    attributes required by :class:`TLSSignatureScheme` that are specific
    to :attr:`~siotls.iana.SignatureScheme.rsa_pss_rsae_sha384`.

    Specifically, this mixin has values for:
    :attr:`~TLSKeyExchange.iana_id`,
    :attr:`~TLSKeyExchange.sign_oid`, and
    :attr:`~TLSKeyExchange.pubkey_oid`.
    """
    iana_id = SignatureScheme.rsa_pss_pss_sha384
    sign_oid = SignatureAlgorithmOID.RSASSA_PSS
    pubkey_oid = PublicKeyAlgorithmOID.RSASSA_PSS
    hash_oid = HashOID.sha384

class RsaPssPssSha512Mixin:
    """
    Mixin for RSASSA PSS with a ``RSASSA-PSS`` public key OID and a
    SHA512 digest.

    This mixin can be inherited by crypto backends to feed all the
    attributes required by :class:`TLSSignatureScheme` that are specific
    to :attr:`~siotls.iana.SignatureScheme.rsa_pss_rsae_sha512`.

    Specifically, this mixin has values for:
    :attr:`~TLSKeyExchange.iana_id`,
    :attr:`~TLSKeyExchange.sign_oid`, and
    :attr:`~TLSKeyExchange.pubkey_oid`.
    """
    iana_id = SignatureScheme.rsa_pss_pss_sha512
    sign_oid = SignatureAlgorithmOID.RSASSA_PSS
    pubkey_oid = PublicKeyAlgorithmOID.RSASSA_PSS
    hash_oid = HashOID.sha512


class EcdsaSecp256r1Sha256Mixin:
    """
    Mixin for ECDSA SEC P-256 R1 with a SHA256 digest.

    This mixin can be inherited by crypto backends to feed all the
    attributes required by :class:`TLSSignatureScheme` that are specific
    to :attr:`~siotls.iana.SignatureScheme.ecdsa_secp256r1_sha256`.

    Specifically, this mixin has values for:
    :attr:`~TLSKeyExchange.iana_id`,
    :attr:`~TLSKeyExchange.sign_oid`,
    :attr:`~TLSKeyExchange.pubkey_oid`, and
    :attr:`~TLSKeyExchange.curve_oid`.
    """
    iana_id = SignatureScheme.ecdsa_secp256r1_sha256
    sign_oid = SignatureAlgorithmOID.ECDSA_WITH_SHA256
    pubkey_oid = PublicKeyAlgorithmOID.EC_PUBLIC_KEY
    curve_oid = EllipticCurveOID.secp256r1

class EcdsaSecp384r1Sha384Mixin:
    """
    Mixin for ECDSA SEC P-384 R1 with a SHA384 digest.

    This mixin can be inherited by crypto backends to feed all the
    attributes required by :class:`TLSSignatureScheme` that are specific
    to :attr:`~siotls.iana.SignatureScheme.ecdsa_secp384r1_sha384`.

    Specifically, this mixin has values for:
    :attr:`~TLSKeyExchange.iana_id`,
    :attr:`~TLSKeyExchange.sign_oid`,
    :attr:`~TLSKeyExchange.pubkey_oid`, and
    :attr:`~TLSKeyExchange.curve_oid`.
    """
    iana_id = SignatureScheme.ecdsa_secp384r1_sha384
    sign_oid = SignatureAlgorithmOID.ECDSA_WITH_SHA384
    pubkey_oid = PublicKeyAlgorithmOID.EC_PUBLIC_KEY
    curve_oid = EllipticCurveOID.secp384r1

class EcdsaSecp521r1Sha512Mixin:
    """
    Mixin for ECDSA SEC P-521 R1 with a SHA512 digest.

    This mixin can be inherited by crypto backends to feed all the
    attributes required by :class:`TLSSignatureScheme` that are specific
    to :attr:`~siotls.iana.SignatureScheme.ecdsa_secp521r1_sha512`.

    Specifically, this mixin has values for:
    :attr:`~TLSKeyExchange.iana_id`,
    :attr:`~TLSKeyExchange.sign_oid`,
    :attr:`~TLSKeyExchange.pubkey_oid`, and
    :attr:`~TLSKeyExchange.curve_oid`.
    """
    iana_id = SignatureScheme.ecdsa_secp521r1_sha512
    sign_oid = SignatureAlgorithmOID.ECDSA_WITH_SHA512
    pubkey_oid = PublicKeyAlgorithmOID.EC_PUBLIC_KEY
    curve_oid = EllipticCurveOID.secp521r1


class Ed25519Mixin:
    """
    Mixin for Ed25519.

    This mixin can be inherited by crypto backends to feed all the
    attributes required by :class:`TLSSignatureScheme` that are specific
    to :attr:`~siotls.iana.SignatureScheme.ed25519`.

    Specifically, this mixin has values for:
    :attr:`~TLSKeyExchange.iana_id`,
    :attr:`~TLSKeyExchange.sign_oid`, and
    :attr:`~TLSKeyExchange.pubkey_oid`.
    """
    iana_id = SignatureScheme.ed25519
    sign_oid = SignatureAlgorithmOID.ED25519
    pubkey_oid = PublicKeyAlgorithmOID.ED25519

class Ed448Mixin:
    """
    Mixin for Ed448.

    This mixin can be inherited by crypto backends to feed all the
    attributes required by :class:`TLSSignatureScheme` that are specific
    to :attr:`~siotls.iana.SignatureScheme.ed448`.

    Specifically, this mixin has values for:
    :attr:`~TLSKeyExchange.iana_id`,
    :attr:`~TLSKeyExchange.sign_oid`, and
    :attr:`~TLSKeyExchange.pubkey_oid`.
    """
    iana_id = SignatureScheme.ed448
    sign_oid = SignatureAlgorithmOID.ED448
    pubkey_oid = PublicKeyAlgorithmOID.ED448
