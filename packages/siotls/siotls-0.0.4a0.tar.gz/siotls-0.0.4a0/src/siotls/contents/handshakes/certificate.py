import dataclasses
import functools
import textwrap
import typing
from collections.abc import Sequence

import asn1crypto.keys  # type: ignore[import-untyped]
import asn1crypto.x509  # type: ignore[import-untyped]

from siotls.asn1types import DerCertificate, DerPublicKey
from siotls.contents import alerts
from siotls.iana import CertificateType, ExtensionType, HandshakeType
from siotls.language import TLSIO, Serializable, SerializableBody
from siotls.utils import RegistryMeta

from . import Handshake
from .extensions import Extension


@dataclasses.dataclass(init=False)
class CertificateEntry(Serializable, metaclass=RegistryMeta):
    """ Abstract base class and registry for :class:`siotls.iana.CertificateType`. """
    _registry_key = '_certificate_entry_registry'
    _certificate_entry_registry: typing.ClassVar = {}

    _struct = textwrap.dedent("""
        enum {
            X509(0),
            RawPublicKey(2),
            (255)
        } CertificateType;

        struct {
            select (certificate_type) {
                case RawPublicKey:
                    /* From RFC 7250 ASN.1_subjectPublicKeyInfo */
                    opaque ASN1_subjectPublicKeyInfo<1..2^24-1>;

                case X509:
                    opaque cert_data<1..2^24-1>;
            };
            Extension extensions<0..2^16-1>;
        } CertificateEntry;
    """)

    certificate_type: CertificateType
    """ The unique numeric identifier of the certificate type. """

    extensions: dict[ExtensionType | int, Extension]
    """
    The extensions applied to this entry, indexed by
    :class:`siotls.iana.ExtensionType`.
    """

    def __init_subclass__(cls, *, register=True, **kwargs):
        super().__init_subclass__(**kwargs)
        if register and CertificateEntry in cls.__bases__:
            cls._certificate_entry_registry[cls.certificate_type] = cls

    @classmethod
    def parse(cls, stream, **kwargs):
        certificate = stream.read_var(3)

        extensions = []
        list_stream = TLSIO(stream.read_var(2))
        while not list_stream.is_eof():
            extension = Extension.parse(
                list_stream,
                handshake_type=HandshakeType.CERTIFICATE,
                **kwargs
            )
            extensions.append(extension)

        return cls(certificate, extensions)


class X509Entry(CertificateEntry):
    """ An entry for a X509 certificate. """

    certificate_type = CertificateType.X509  #:

    certificate: DerCertificate
    """ The der-encoded x509 certificate stored in this entry. """

    def __init__(self, certificate: DerCertificate, extensions: Sequence[Extension]):
        self.certificate = certificate
        self.extensions = {ext.extension_type: ext for ext in extensions}

    @functools.cached_property
    def asn1_certificate(self) -> asn1crypto.x509.Certificate:
        """ The certificate as a asn1crypto object. """
        return asn1crypto.x509.Certificate.load(self.certificate)

    def serialize(self):
        extensions = b''.join(ext.serialize() for ext in self.extensions.values())

        return b''.join([
            len(self.certificate).to_bytes(3, 'big'),
            self.certificate,
            len(extensions).to_bytes(2, 'big'),
            extensions,
        ])


class RawPublicKeyEntry(CertificateEntry):
    """ An entry for a Raw Public Key (:rfc:`7250#`). """

    certificate_type = CertificateType.RAW_PUBLIC_KEY  #:

    public_key: DerPublicKey
    """ The der-encoded public key stored in this entry. """

    def __init__(self, public_key: DerPublicKey, extensions: Sequence[Extension]):
        self.public_key = public_key
        self.extensions = {ext.extension_type: ext for ext in extensions}


    @functools.cached_property
    def asn1_public_key(self) -> asn1crypto.keys.PublicKeyInfo:
        """ The public key as a asn1crypto object. """
        return asn1crypto.keys.PublicKeyInfo.load(self.public_key)

    def serialize(self):
        extensions = b''.join(ext.serialize() for ext in self.extensions.values())

        return b''.join([
            len(self.public_key).to_bytes(3, 'big'),
            self.public_key,
            len(extensions).to_bytes(2, 'big'),
            extensions,
        ])


@dataclasses.dataclass(init=False)
class CertificateHandshake(Handshake, SerializableBody):
    """
    Certificate handshake as defined in :rfc:`8446#section-4.4.2`.
    Conveys the certificate chain or raw public key of one of the peers.
    """

    msg_type = HandshakeType.CERTIFICATE
    _struct = textwrap.dedent("""
        struct {
            opaque certificate_request_context<0..2^8-1>;
            CertificateEntry certificate_list<0..2^24-1>;
        } Certificate;
    """).strip('\n')

    certificate_request_context: bytes
    """
    Additional opaque data, for Post-Handshake Authentication
    (:rfc:`8446#section-4.6.2`).
    """

    certificate_list: Sequence[CertificateEntry]
    """
    The sequence (chain) of CertificateEntry structures, each containing
    a single certificate, or raw public key, with set of extensions.

    Quoting :rfc:`8446#section-4.4.2` (TLS 1.3 - Certificate):

       Note: Prior to TLS 1.3, "certificate_list" ordering required each
       certificate to certify the one immediately preceding it; however,
       some implementations allowed some flexibility.  Servers sometimes
       send both a current and deprecated intermediate for transitional
       purposes, and others are simply configured incorrectly, but these
       cases can nonetheless be validated properly.  For maximum
       compatibility, all implementations SHOULD be prepared to handle
       potentially extraneous certificates and arbitrary orderings from
       any TLS version, with the exception of the end-entity certificate
       wich MUST be first.
    """

    def __init__(
        self,
        certificate_request_context: bytes,
        certificate_list: Sequence[CertificateEntry]
    ):
        self.certificate_request_context = certificate_request_context
        self.certificate_list = certificate_list

    @classmethod
    def parse_body(cls, stream, *, config, nconfig, **kwargs):
        certificate_request_context = stream.read_var(1)

        certificate_list = []
        with stream.limit(stream.read_int(3)) as limit:
            while stream.tell() < limit:
                certificate = CertificateEntry[
                    nconfig.client_certificate_type
                    if config.other_side == 'client' else
                    nconfig.server_certificate_type
                ].parse(stream, **kwargs)
                certificate_list.append(certificate)

        try:
            return cls(certificate_request_context, certificate_list)
        except ValueError as exc:
            raise alerts.IllegalParameter(*exc.args) from exc

    def serialize_body(self):
        certificates = b''.join(cert.serialize() for cert in self.certificate_list)

        return b''.join([
            len(self.certificate_request_context).to_bytes(1, 'big'),
            self.certificate_request_context,
            len(certificates).to_bytes(3, 'big'),
            certificates
        ])
