import dataclasses
import textwrap
from collections.abc import Sequence

from siotls.contents import alerts
from siotls.contents.handshakes.extensions import Extension
from siotls.iana import ExtensionType, HandshakeType
from siotls.language import TLSIO, SerializableBody

from . import Handshake


@dataclasses.dataclass(init=False)
class CertificateRequest(Handshake, SerializableBody):
    """
    Certificate Request handshake as defined in :rfc:`8446#section-4.3.2`.
    Sent by the server when it want the user to authenticate.
    """

    msg_type = HandshakeType.CERTIFICATE_REQUEST
    _struct = textwrap.dedent("""
        struct {
            opaque certificate_request_context<0..2^8-1>;
            Extension extensions<0..2^16-1>;
        } CertificateRequest;
    """)

    certificate_request_context: bytes
    """
    Additional opaque data, for Post-Handshake Authentication
    (:rfc:`8446#section-4.6.2`).
    """

    extensions: dict[ExtensionType | int, Extension]
    """
    The list of extensions describing the certificate being requested,
    e.g.
    :class:`~siotls.contents.handshakes.extensions.signature_algorithms.SignatureAlgorithms`
    and
    :class:`~siotls.contents.handshakes.extensions.certificate_authorities.CertificateAuthorities`.
    """

    def __init__(self, certificate_request_context: bytes, extensions: Sequence[Extension]):
        self.certificate_request_context = certificate_request_context
        self.extensions = {ext.extension_type: ext for ext in extensions}
        if ExtensionType.SIGNATURE_ALGORITHMS not in self.extensions:
            e =(f"{ExtensionType.SIGNATURE_ALGORITHMS} is a mandatory "
                f"extension with {type(self)}")
            raise ValueError(e)

    @classmethod
    def parse_body(cls, stream, **kwargs):  # noqa: ARG003
        certificate_request_context = stream.read_var(1)

        extensions = []
        list_stream = TLSIO(stream.read_var(2))
        while not list_stream.is_eof():
            extension = Extension.parse(
                list_stream, handshake_type=HandshakeType.CERTIFICATE_REQUEST)
            extensions.append(extension)

        try:
            return cls(certificate_request_context, extensions)
        except ValueError as exc:
            raise alerts.IllegalParameter(*exc.args) from exc

    def serialize_body(self):
        extensions = b''.join(ext.serialize() for ext in self.extensions.values())

        return b''.join([
            len(self.certificate_request_context).to_bytes(1, 'big'),
            self.certificate_request_context,
            len(extensions).to_bytes(2, 'big'),
            extensions,
        ])
