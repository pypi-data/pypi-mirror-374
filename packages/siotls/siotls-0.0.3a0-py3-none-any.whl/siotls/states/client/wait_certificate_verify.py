from siotls.contents import alerts
from siotls.crypto import SignatureKeyError, SignatureVerifyError, TLSSignatureScheme
from siotls.iana import ContentType, HandshakeType

from .. import State
from . import ClientWaitFinished

CERTIFICATE_VERIFY_SERVER = b"".join([
    b" " * 64,
    b"TLS 1.3, server CertificateVerify",
    b"\x00",
])


class ClientWaitCertificateVerify(State):
    can_send = True
    can_send_application_data = False

    def __init__(self, connection, must_authentify, certificate_transcript_hash):
        super().__init__(connection)
        self._must_authentify = must_authentify
        self._certificate_transcript_hash = certificate_transcript_hash

    def process(self, content):
        if (content.content_type != ContentType.HANDSHAKE
            or content.msg_type is not HandshakeType.CERTIFICATE_VERIFY):
            super().process(content)
            return

        if content.algorithm not in self.config.signature_algorithms:
            e =(f"the server's selected {content.algorithm} wasn't "
                f"offered in ClientHello: {self.config.signature_algorithms}")
            raise alerts.IllegalParameter(e)
        self.nconfig.peer_signature_algorithm = content.algorithm

        try:
            TLSSignatureScheme[content.algorithm](public_key=self.nconfig.peer_public_key).verify(
                content.signature,
                CERTIFICATE_VERIFY_SERVER + self._certificate_transcript_hash,
            )
        except (SignatureKeyError, SignatureVerifyError) as exc:
            raise alerts.BadCertificate from exc

        self._move_to_state(
            ClientWaitFinished,
            must_authentify=self._must_authentify,
            certificate_verify_transcript_hash=self._transcript.digest(),
        )
