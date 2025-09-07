from siotls.contents import alerts
from siotls.contents.handshakes import CertificateHandshake, CertificateVerify, Finished
from siotls.contents.handshakes.certificate import RawPublicKeyEntry, X509Entry
from siotls.iana import CertificateType, ContentType, HandshakeType

from .. import CERTIFICATE_VERIFY_CLIENT, Connected, State


class ClientWaitFinished(State):
    can_send = True
    can_send_application_data = False

    def __init__(self, connection, must_authentify, server_certificate_verify_th):
        super().__init__(connection)
        self._must_authentify = must_authentify
        self._server_certificate_verify_th = server_certificate_verify_th

    def process(self, content):
        if (content.content_type != ContentType.HANDSHAKE
            or content.msg_type is not HandshakeType.FINISHED):
            super().process(content)
            return

        try:
            self._cipher.verify_finish(
                self._server_certificate_verify_th,
                content.verify_data,
            )
        except ValueError as exc:
            raise alerts.DecryptError from exc
        server_finished_th = self._transcript.digest()

        if self._must_authentify:
            self._send_certificate()

        client_pre_finished_th = self._transcript.digest()
        self._send_content(Finished(self._cipher.sign_finish(client_pre_finished_th)))

        client_finished_th = self._transcript.digest()
        self._cipher.derive_master_secrets(server_finished_th, client_finished_th)

        self._move_to_state(Connected)

    def _send_certificate(self):
        certificate_list = []
        match self.nconfig.client_certificate_type:
            case CertificateType.RAW_PUBLIC_KEY:
                certificate_list.append(RawPublicKeyEntry(self.config.public_key, []))
            case CertificateType.X509:
                certificate_list.extend([
                    X509Entry(certificate, [])
                    for certificate
                    in self.config.certificate_chain
                ])
            case unknown:
                e = f"unknown client certificate type: {unknown!r}"
                raise NotImplementedError(e)

        self._send_content(CertificateHandshake(b'', certificate_list))
        self._send_content(CertificateVerify(
            self._signature.iana_id,
            self._signature.sign(CERTIFICATE_VERIFY_CLIENT + self._transcript.digest())
        ))
