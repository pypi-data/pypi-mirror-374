import dataclasses
import logging
import textwrap

from siotls.iana import ExtensionType, HandshakeType
from siotls.language import TLSIO, SerializableBody

from . import Handshake
from .extensions import Extension

logger = logging.getLogger(__name__)


@dataclasses.dataclass(init=False)
class EncryptedExtensions(Handshake, SerializableBody):
    """
    Encrypted Extensions handshake as defined in :rfc:`8446#section-4.3.1`.
    Follows :class:`~siotls.contents.handshakes.server_hello.ServerHello`
    with the list of negotiated features that are not needed to setup
    encryption.
    """
    msg_type = HandshakeType.ENCRYPTED_EXTENSIONS

    _struct = textwrap.dedent("""
        struct {
            Extension extensions<0..2^16-1>;
        } EncryptedExtensions;
    """).strip('\n')

    extensions: dict[ExtensionType | int, Extension]
    """
    The extensions, indexed by :class:`siotls.iana.ExtensionType`, used
    to negotiate cryptographic settings and additionnal features for
    this connection.
    """

    def __init__(self, extensions: list[Extension]):
        self.extensions = {ext.extension_type: ext for ext in extensions}

    @classmethod
    def parse_body(cls, stream, **kwargs):
        extensions = []
        list_stream = TLSIO(stream.read_var(2))
        while not list_stream.is_eof():
            extension = Extension.parse(list_stream, handshake_type=cls.msg_type, **kwargs)
            extensions.append(extension)

        return cls(extensions)

    def serialize_body(self):
        extensions = b''.join(ext.serialize() for ext in self.extensions.values())
        return b''.join([
            len(extensions).to_bytes(2, 'big'),
            extensions,
        ])
