from siotls.contents import alerts
from siotls.iana import CertificateType


class WaitCertificateMixin:
    def _process(self, content, certificate_type):
        if self.config.require_peer_authentication:
            if not content.certificate_list:
                if self.config.other_side == 'server':
                    e = "empty server certificate"
                    raise alerts.DecodeError(e)
                e = "empty client certificate"
                raise alerts.CertificateRequired(e)
        self._check_certificate_types(content.certificate_list, certificate_type)
        match certificate_type:
            case CertificateType.X509:
                self._process_x509(content)
            case CertificateType.RAW_PUBLIC_KEY:
                self._process_raw_public_key(content)
            case _:
                raise NotImplementedError

    def _check_certificate_types(self, certificate_entries, certificate_type):
        bad_entries = (
            entry
            for entry in certificate_entries
            if entry.certificate_type != certificate_type
        )
        if bad_entry := next(bad_entries, None):
            e = f"expected {certificate_type} but found {bad_entry.certificate_type}"
            raise alerts.UnsupportedCertificate(e)

    def _process_x509(self, content):
        leaf = content.certificate_list[0]
        self.nconfig.peer_certificate = leaf.certificate
        self.nconfig.peer_public_key = leaf.asn1_certificate.public_key.dump()
        if not self.config.require_peer_authentication:
            return
        if self.nconfig.peer_public_key in self.config.trusted_public_keys:
            return
        if self.config.truststore:
            self.config.truststore.verify_chain(self, content.certificate_list)
            return
        e = "the peer's public key is not trusted"
        raise alerts.BadCertificate(e)

    def _process_raw_public_key(self, content):
        public_key = content.certificate_list[0].public_key
        self.nconfig.peer_public_key = public_key
        if (self.config.require_peer_authentication
            and public_key not in self.config.trusted_public_keys()
        ):
            e = "the peer's raw public key is not trusted"
            raise alerts.BadCertificate(e)
