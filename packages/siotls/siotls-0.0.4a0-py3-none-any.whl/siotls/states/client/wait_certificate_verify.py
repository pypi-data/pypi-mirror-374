from siotls.contents import alerts
from siotls.crypto import SignatureKeyError, SignatureVerifyError, TLSSignatureScheme
from siotls.iana import ContentType, HandshakeType

from .. import CERTIFICATE_VERIFY_SERVER, State
from . import ClientWaitFinished


class ClientWaitCertificateVerify(State):
    can_send = True
    can_send_application_data = False

    def __init__(self, connection, must_authentify, client_certificate_th):
        super().__init__(connection)
        self._must_authentify = must_authentify
        self._client_certificate_th = client_certificate_th

    def process(self, content):
        if (content.content_type != ContentType.HANDSHAKE
            or content.msg_type is not HandshakeType.CERTIFICATE_VERIFY):
            super().process(content)
            return
        server_certificate_verify_th = self._transcript.digest()

        if content.algorithm not in self.config.signature_algorithms:
            e =(f"the server's selected {content.algorithm} wasn't "
                f"offered in ClientHello: {self.config.signature_algorithms}")
            raise alerts.IllegalParameter(e)
        self.nconfig.peer_signature_algorithm = content.algorithm

        try:
            TLSSignatureScheme[content.algorithm](
                public_key=self.nconfig.peer_public_key
            ).verify(
                content.signature,
                CERTIFICATE_VERIFY_SERVER + self._client_certificate_th,
            )
        except (SignatureKeyError, SignatureVerifyError) as exc:
            raise alerts.BadCertificate from exc

        self._move_to_state(
            ClientWaitFinished,
            self._must_authentify,
            server_certificate_verify_th,
        )
