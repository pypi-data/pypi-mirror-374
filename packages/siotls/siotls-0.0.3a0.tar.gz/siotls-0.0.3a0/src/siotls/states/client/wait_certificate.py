import logging

from siotls.contents import alerts
from siotls.iana import CertificateType, ContentType, HandshakeType

from .. import State
from . import ClientWaitCertificateVerify

logger = logging.getLogger(__name__)


class ClientWaitCertificate(State):
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

        if self.config.require_peer_authentication:
            if not content.certificate_list:
                e = "missing certificate"
                raise alerts.BadCertificate(e)
        self._check_certificate_types(content.certificate_list)
        match self.nconfig.server_certificate_type:
            case CertificateType.X509:
                self._process_x509(content)
            case CertificateType.RAW_PUBLIC_KEY:
                self._process_raw_public_key(content)
            case _:
                raise NotImplementedError

        self._move_to_state(
            ClientWaitCertificateVerify,
            must_authentify=self._must_authentify,
            certificate_transcript_hash=self._transcript.digest(),
        )

    def _check_certificate_types(self, certificate_entries):
        bad_entries = (
            entry
            for entry in certificate_entries
            if entry.certificate_type != self.nconfig.server_certificate_type
        )
        if bad_entry := next(bad_entries, None):
            e =(f"expected {self.nconfig.server_certificate_type} "
                f"but found {bad_entry.certificate_type}")
            raise alerts.UnsupportedCertificate(e)

    def _process_x509(self, content):
        leaf = content.certificate_list[0]
        self.nconfig.peer_certificate = leaf.certificate
        self.nconfig.peer_public_key = leaf.asn1_certificate.public_key.dump()
        if not self.config.require_peer_authentication:
            return
        if self.nconfig.peer_public_key in self.config.trusted_public_keys:
            return
        self.config.x509verifier.verify_chain(self, content.certificate_list)

    def _process_raw_public_key(self, content):
        public_key = content.certificate_list[0].public_key
        self.nconfig.peer_public_key = public_key
        if (self.config.require_peer_authentication
            and public_key not in self.config.trusted_public_keys()
        ):
            e = "untrusted raw public key"
            raise alerts.BadCertificate(e)
