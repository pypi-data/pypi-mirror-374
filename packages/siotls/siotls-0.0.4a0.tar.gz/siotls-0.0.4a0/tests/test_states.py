import dataclasses
import unittest

from siotls import TLSConnection
from siotls.contents import ApplicationData, alerts
from siotls.contents.handshakes import ClientHello, Finished, HelloRetryRequest
from siotls.contents.handshakes.extensions import (
    KeyShareRequest,
    KeyShareRetry,
    SignatureAlgorithms,
    SupportedGroups,
    SupportedVersionsRequest,
    SupportedVersionsResponse,
)
from siotls.crypto import TLSKeyExchange
from siotls.iana import (
    CertificateType,
    CipherSuites,
    MaxFragmentLengthOctets,
    NamedGroup,
    SignatureScheme,
    TLSVersion,
)
from siotls.utils import submap

from . import TAG_INTEGRATION, TestCase, tls_decode
from .config import client_config, server_config, server_domain


class TestStateServerWaitClientHello(TestCase):
    def test_state_server_wait_client_hello_bad_content_type(self):
        server_conn = TLSConnection(server_config)
        server_conn.initiate_connection()

        e = "cannot process ApplicationData in state ServerWaitClientHello"
        with self.assertRaises(alerts.UnexpectedMessage, error_msg=e):
            server_conn._state.process(ApplicationData(b""))

    def test_state_server_wait_client_hello_bad_msg_type(self):
        server_conn = TLSConnection(server_config)
        server_conn.initiate_connection()

        e = "cannot process Finished in state ServerWaitClientHello"
        with self.assertRaises(alerts.UnexpectedMessage, error_msg=e):
            server_conn._state.process(Finished(b""))

    def test_state_server_wait_client_hello_close_notify(self):
        server_conn = TLSConnection(server_config)
        server_conn.initiate_connection()

        with self.assertLogs('siotls.connection', 'WARNING') as capture:
            server_conn._state.process(alerts.CloseNotify())
        self.assertTrue(server_conn.is_post_handshake())
        self.assertFalse(server_conn.is_connected())
        self.assertEqual(capture.output, [
            'WARNING:siotls.connection:EOF or CloseNotify alert during handshake'
        ])

    def test_state_server_wait_client_hello_hrr(self):
        server_conn = TLSConnection(server_config)
        server_conn.initiate_connection()

        # first flight
        config = dataclasses.replace(client_config,
            cipher_suites=[client_config.cipher_suites[0]],
        )
        client_conn = TLSConnection(config, server_domain)
        client_conn._send_content(ClientHello(
            random=b'a' * 32,
            cipher_suites=[client_config.cipher_suites[0]],
            extensions=[
                SupportedVersionsRequest([TLSVersion.TLS_1_3]),
                SignatureAlgorithms(client_conn.config.signature_algorithms),
                SupportedGroups(client_conn.config.key_exchanges),
            ]
        ))
        client_hello_first_flight = client_conn.data_to_send()
        server_conn.receive_data(client_hello_first_flight)
        self.assertEqual(
            tls_decode(client_conn, server_conn.data_to_send()),
            [HelloRetryRequest(
                random=HelloRetryRequest.random,
                legacy_session_id_echo=b"",
                cipher_suite=client_config.cipher_suites[0],
                extensions=[
                    SupportedVersionsResponse(TLSVersion.TLS_1_3),
                    KeyShareRetry(server_config.key_exchanges[0]),
                ],
            )]
        )

        _, exchange = TLSKeyExchange[server_config.key_exchanges[0]].init()
        server_state = server_conn._state
        server_transcript = server_conn._transcript.copy()
        server_nconfig = server_conn.nconfig.copy()

        for subtest in (
            self._test_state_server_wait_client_hello_hrr_bad_cipher,
            self._test_state_server_wait_client_hello_hrr_bad_client_random,
            self._test_state_server_wait_client_hello_hrr_missing_key_share,
        ):
            name = subtest.__func__.__name__.split('_', 8)[-1]
            with self.subTest(subtest=name):
                server_conn._state = server_state
                server_conn._transcript = server_transcript.copy()
                server_conn.nconfig = server_nconfig
                subtest(server_conn, exchange)

    def _test_state_server_wait_client_hello_hrr_bad_cipher(self, server_conn, _exchange):  # noqa: E501
        if len(client_config.cipher_suites) < 2:  # noqa: PLR2004
            self.skipTest("incompatible crypto backend")
        config = dataclasses.replace(client_config,
            cipher_suites=[client_config.cipher_suites[1]],  # bad cipher
        )
        client_conn = TLSConnection(config, server_domain)
        client_conn._send_content(ClientHello(
            random=b'a' * 32,
            cipher_suites=[client_config.cipher_suites[1]],  # bad cipher
            extensions=[
                SupportedVersionsRequest([TLSVersion.TLS_1_3]),
                SignatureAlgorithms(client_conn.config.signature_algorithms),
                SupportedGroups(client_conn.config.key_exchanges),
            ]
        ))
        client_hello_second_flight = client_conn.data_to_send()

        e = "no common cipher suite found"
        with self.assertRaises(alerts.HandshakeFailure, error_msg=e):
            server_conn.receive_data(client_hello_second_flight)
        self.assertEqual(
            tls_decode(client_conn, server_conn.data_to_send()),
            [alerts.HandshakeFailure()]
        )

    def _test_state_server_wait_client_hello_hrr_bad_client_random(self, server_conn, exchange):  # noqa: E501
        client_conn = TLSConnection(client_config, server_domain)
        client_conn._send_content(ClientHello(
            random=b'b' * 32,  # bad client unique
            cipher_suites=client_conn.config.cipher_suites,
            extensions=[
                SupportedVersionsRequest([TLSVersion.TLS_1_3]),
                SignatureAlgorithms(client_conn.config.signature_algorithms),
                SupportedGroups([server_config.key_exchanges[0]]),
                KeyShareRequest({server_config.key_exchanges[0]: exchange}),
            ]
        ))
        client_hello_second_flight = client_conn.data_to_send()

        e = "client's random cannot change in between Hellos"
        with self.assertRaises(alerts.IllegalParameter, error_msg=e):
            server_conn.receive_data(client_hello_second_flight)
        self.assertEqual(
            tls_decode(client_conn, server_conn.data_to_send()),
            [alerts.IllegalParameter()]
        )

    def _test_state_server_wait_client_hello_hrr_missing_key_share(self, server_conn, _):  # noqa: E501
        client_conn = TLSConnection(client_config, server_domain)
        client_conn._send_content(ClientHello(
            random=b'a' * 32,
            cipher_suites=client_conn.config.cipher_suites,
            extensions=[
                SupportedVersionsRequest([TLSVersion.TLS_1_3]),
                SignatureAlgorithms(client_conn.config.signature_algorithms),
                SupportedGroups([server_config.key_exchanges[0]]),
            ]
        ))
        client_hello_second_flight = client_conn.data_to_send()

        e = "invalid KeyShare in second ClientHello"
        with self.assertRaises(alerts.HandshakeFailure, error_msg=e):
            server_conn.receive_data(client_hello_second_flight)
        self.assertEqual(
            tls_decode(client_conn, server_conn.data_to_send()),
            [alerts.HandshakeFailure()]
        )

    @unittest.skipUnless(TAG_INTEGRATION, "enable with SIOTLS_INTEGRATION=1")
    def test_state_server_wait_client_hello_good(self):
        server_conn = TLSConnection(server_config)
        server_conn.initiate_connection()

        client_conn = TLSConnection(client_config, server_domain)
        client_conn.initiate_connection()

        server_conn.receive_data(client_conn.data_to_send())
        self.assertEqual(
            second=(keys:={
                'alpn': None,
                'cipher_suite': CipherSuites.TLS_CHACHA20_POLY1305_SHA256,
                'client_certificate_type': None,
                'key_exchange': NamedGroup.x25519,
                'max_fragment_length': MaxFragmentLengthOctets.MAX_16384,
                'server_certificate_type': CertificateType.X509,
                'signature_algorithm': SignatureScheme.ecdsa_secp256r1_sha256
            }),
            first=submap(dataclasses.asdict(server_conn.nconfig), keys),
        )
