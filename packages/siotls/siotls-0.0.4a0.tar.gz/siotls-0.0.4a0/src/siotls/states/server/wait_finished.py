from siotls.contents import alerts
from siotls.iana import ContentType, HandshakeType

from .. import Connected, State


class ServerWaitFinished(State):
    can_send = True
    can_send_application_data = True

    def __init__(
        self,
        connection,
        server_finished_th,
        client_pre_finished_th,
        *,
        fatal_alert=None,
    ):
        super().__init__(connection)
        self._server_finished_th = server_finished_th
        self._client_pre_finished_th = client_pre_finished_th
        self._fatal_alert = fatal_alert

    def process(self, finished):
        if (finished.content_type != ContentType.HANDSHAKE
            or finished.msg_type != HandshakeType.FINISHED):
            super().process(finished)
            return
        client_finished_th = self._transcript.digest()

        try:
            self._cipher.verify_finish(
                self._client_pre_finished_th,
                finished.verify_data,
            )
        except ValueError as exc:
            raise alerts.DecryptError from exc

        self._cipher.derive_master_secrets(
            self._server_finished_th,
            client_finished_th,
        )

        if self._fatal_alert:
            raise self._fatal_alert
        self._move_to_state(Connected)
