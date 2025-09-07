import dataclasses
import textwrap

from siotls.crypto import TLSCipherSuite
from siotls.iana import HandshakeType
from siotls.language import SerializableBody

from . import Handshake


@dataclasses.dataclass(init=False)
class Finished(Handshake, SerializableBody):
    """
    Finished handshake as defined in :rfc:`8446#section-4.4.4`. Contains
    a signed hash of the handshakes exchanged so far (which includes
    both ends ``random`` bytes) which, upon verification, gives the
    guarantee that this connection is secure.
    """

    msg_type = HandshakeType.FINISHED
    _struct = textwrap.dedent("""
        struct {
            opaque verify_data[Hash.length];
        } Finished;
    """).strip('\n')

    verify_data: bytes
    """ The result of the HMAC over the handshakes exchanged so far. """

    def __init__(self, verify_data):
        self.verify_data = verify_data

    @classmethod
    def parse_body(cls, stream, nconfig, **kwargs):  # noqa: ARG003
        cipher = TLSCipherSuite[nconfig.cipher_suite]
        return cls(stream.read_exactly(cipher.digestmod().digest_size))

    def serialize_body(self):
        return self.verify_data
