from siotls.iana import ContentType, HandshakeType
from siotls.states.wait_certificate_mixin import WaitCertificateMixin

from .. import State
from . import ClientWaitCertificateVerify


class ClientWaitCertificate(WaitCertificateMixin, State):
    can_send = True
    can_send_application_data = False

    def __init__(self, connection, must_authentify):
        super().__init__(connection)
        self._must_authentify = must_authentify

    def process(self, content):
        if (content.content_type != ContentType.HANDSHAKE
            or content.msg_type is not HandshakeType.CERTIFICATE):
            super().process(content)
            return

        server_certificate_th = self._transcript.digest()
        self._process(content, self.nconfig.server_certificate_type)

        self._move_to_state(
            ClientWaitCertificateVerify,
            self._must_authentify,
            server_certificate_th,
        )
