from siotls.contents import alerts
from siotls.iana import AlertDescription, ContentType, HandshakeType
from siotls.states.wait_certificate_mixin import WaitCertificateMixin

from .. import State
from . import ServerWaitCertificateVerify, ServerWaitFinished


class ServerWaitCertificate(WaitCertificateMixin, State):
    can_send = True
    can_send_application_data = True

    def __init__(self, connection, server_finished_th):
        super().__init__(connection)
        self._server_finished_th = server_finished_th

    def process(self, content):
        if (content.content_type != ContentType.HANDSHAKE
            or content.msg_type is not HandshakeType.CERTIFICATE):
            super().process(content)
            return

        client_certificate_th = self._transcript.digest()
        try:
            self._process(content, self.nconfig.client_certificate_type)
        except alerts.TLSFatalAlert as exc:
            # cannot send the alert immediatly, as the client is now
            # receiving messages using the Master key
            if exc.description == AlertDescription.CERTIFICATE_REQUIRED:
                next_state = ServerWaitFinished
            else:
                next_state = ServerWaitCertificateVerify
            self._move_to_state(
                next_state,
                self._server_finished_th,
                client_certificate_th,
                fatal_alert=exc,
            )
        else:
            self._move_to_state(
                ServerWaitCertificateVerify,
                self._server_finished_th,
                client_certificate_th,
            )
