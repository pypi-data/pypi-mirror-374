from ipaddress import ip_address

from siotls.contents.handshakes import ClientHello
from siotls.contents.handshakes.extensions import (
    ALPN,
    ClientCertificateTypeRequest,
    Cookie,
    HostName,
    KeyShareRequest,
    ServerCertificateTypeRequest,
    ServerNameListRequest,
    SignatureAlgorithms,
    SupportedGroups,
    SupportedVersionsRequest,
)
from siotls.crypto import TLSKeyExchange
from siotls.iana import CertificateType, TLSVersion

from .. import State
from . import ClientWaitServerHello


class ClientStart(State):
    can_send = True
    can_send_application_data = False

    def __init__(self, connection, cookie=None):
        super().__init__(connection)
        self._cookie = cookie
        self._key_shares = {}

    def initiate_connection(self):
        extensions = [
            SupportedVersionsRequest([TLSVersion.TLS_1_3]),
            SignatureAlgorithms(self.config.signature_algorithms),
            SupportedGroups(self.config.key_exchanges),
        ]
        if self.server_hostname:
            try:
                ip_address(self.server_hostname)
            except ValueError:
                # server_hostname is not an ip address
                extensions.append(ServerNameListRequest([
                    HostName(self.server_hostname)
                ]))
            else:
                # server_hostname is an ip address
                pass  # the ServerName extension doesn't support ip addresses
        if self.config.alpn:
            extensions.append(ALPN(self.config.alpn))

        if self.config.certificate_types:
            extensions.append(ClientCertificateTypeRequest(self.config.certificate_types))
        if self.config.peer_certificate_types not in ([], [CertificateType.X509]):
            # x509 assumed when extension missing
            extensions.append(ServerCertificateTypeRequest(self.config.peer_certificate_types))
        if self._cookie:
            extensions.append(Cookie(self._cookie))

        key_exchange = self.config.key_exchanges[0]
        private_key, my_key_share = TLSKeyExchange[key_exchange].init()
        self._key_shares[key_exchange] = private_key
        extensions.append(KeyShareRequest({key_exchange: my_key_share}))

        self._send_content(ClientHello(
            self._client_unique, self.config.cipher_suites, extensions,
        ))

        self._move_to_state(ClientWaitServerHello, key_shares=self._key_shares)

    def process(self, message):
        super().process(message)
