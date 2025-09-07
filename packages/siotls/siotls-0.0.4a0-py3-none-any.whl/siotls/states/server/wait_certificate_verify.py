from siotls.contents import alerts
from siotls.crypto import SignatureKeyError, SignatureVerifyError, TLSSignatureScheme
from siotls.iana import ContentType, HandshakeType

from .. import CERTIFICATE_VERIFY_CLIENT, State
from . import ServerWaitFinished


class ServerWaitCertificateVerify(State):
    can_send = True
    can_send_application_data = True

    def __init__(
        self,
        connection,
        server_finished_th,
        client_certificate_th,
        *,
        fatal_alert=None,
    ):
        super().__init__(connection)
        self._server_finished_th = server_finished_th
        self._client_certificate_th = client_certificate_th
        self._fatal_alert = fatal_alert

    def process(self, content):
        if (content.content_type != ContentType.HANDSHAKE
            or content.msg_type is not HandshakeType.CERTIFICATE_VERIFY):
            super().process(content)
            return
        client_pre_finished_th = self._transcript.digest()

        if content.algorithm not in self.config.signature_algorithms:
            e =(f"the client's selected {content.algorithm} wasn't "
                f"offered in CertificateRequest: {self.config.signature_algorithms}")
            raise alerts.IllegalParameter(e)
        self.nconfig.peer_signature_algorithm = content.algorithm

        try:
            TLSSignatureScheme[content.algorithm](
                public_key=self.nconfig.peer_public_key
            ).verify(
                content.signature,
                CERTIFICATE_VERIFY_CLIENT + self._client_certificate_th,
            )
        except (SignatureKeyError, SignatureVerifyError) as exc:
            raise alerts.BadCertificate from exc

        self._move_to_state(
            ServerWaitFinished,
            self._server_finished_th,
            client_pre_finished_th,
            fatal_alert=self._fatal_alert,
        )
