import logging

from siotls.crypto.cipher_suites import CipherState, TLSCipherSuite
from siotls.iana import CipherSuites

from . import TestCase


class TestCrytoCipherSuite(TestCase):
    def _assertKeyLogEqual(self, output, client_unique, *pairs):  # noqa: N802
        self.assertEqual(output, [
            f"INFO:siotls.keylog:{secret} {client_unique.hex()} {value}"
            for secret, value in pairs
        ])

    def test_cipher_init(self):
        ChaPoly = TLSCipherSuite[CipherSuites.TLS_CHACHA20_POLY1305_SHA256]
        client_cipher = ChaPoly('client', b'', log_keys=False)
        self.assertEqual(client_cipher.state, CipherState.INIT)
        self.assertFalse(client_cipher.must_decrypt)
        self.assertFalse(client_cipher.must_encrypt)
        self.assertFalse(client_cipher.should_rekey)
        with self.assertRaises((TypeError, AssertionError)):
            client_cipher.encrypt(b'', b'')
        with self.assertRaises((TypeError, AssertionError)):
            client_cipher.decrypt(b'', b'')
        with self.assertRaises((AttributeError, AssertionError)):
            client_cipher.sign_finish(b'')
        with self.assertRaises((AttributeError, AssertionError)):
            client_cipher.verify_finish(b'', b'')

    def test_cipher_skip_early_secret(self):
        ChaPoly = TLSCipherSuite[CipherSuites.TLS_CHACHA20_POLY1305_SHA256]
        client_unique = b'client unique value of 32 bytes-'

        client_cipher = ChaPoly('client', client_unique, log_keys=True)
        with self.assertNoLogs('siotls.keylog', logging.INFO):
            client_cipher.skip_early_secrets()
        self.assertEqual(client_cipher.state, CipherState.EARLY)
        self.assertFalse(client_cipher.must_decrypt)
        self.assertFalse(client_cipher.must_encrypt)
        self.assertFalse(client_cipher.should_rekey)

        server_cipher = ChaPoly('server', client_unique, log_keys=True)
        with self.assertNoLogs('siotls.keylog', logging.INFO):
            server_cipher.skip_early_secrets()
        self.assertEqual(server_cipher.state, CipherState.EARLY)
        self.assertFalse(server_cipher.must_decrypt)
        self.assertFalse(server_cipher.must_encrypt)
        self.assertFalse(server_cipher.should_rekey)

    def test_cipher_early_secret(self):
        ChaPoly = TLSCipherSuite[CipherSuites.TLS_CHACHA20_POLY1305_SHA256]
        client_unique = b'client unique value of 32 bytes-'
        pre_shared_key = b'pre shared key value of 32 bytes'
        transcript_hash = ChaPoly.digestmod(b"client hello").digest()

        # client side
        client_cipher = ChaPoly('client', client_unique, log_keys=True)
        with self.assertLogs('siotls.keylog', logging.INFO) as capture:
            client_cipher.derive_early_secrets(
                pre_shared_key, 'external', transcript_hash)
            self._assertKeyLogEqual(capture.output, client_unique,
                ('CLIENT_EARLY_TRAFFIC_SECRET',
                 'fc3ab38713cde6d40f65f709e740339997f5fc5004ce46cf820a51ddcd81f8c8'),
            )
        self.assertEqual(client_cipher.state, CipherState.EARLY)
        self.assertFalse(
            client_cipher.must_decrypt,
            "the server is about to send unencrypted server hello")
        self.assertTrue(
            client_cipher.must_encrypt,
            "the client is about to send encrypted early data")
        self.assertFalse(client_cipher.should_rekey)

        # server side
        server_cipher = ChaPoly('server', client_unique, log_keys=True)
        with self.assertLogs('siotls.keylog', logging.INFO) as capture:
            server_cipher.derive_early_secrets(
                pre_shared_key, 'external', transcript_hash)
            self.assertEqual(capture.output, [
                f'INFO:siotls.keylog:CLIENT_EARLY_TRAFFIC_SECRET {client_unique.hex()} '
                    'fc3ab38713cde6d40f65f709e740339997f5fc5004ce46cf820a51ddcd81f8c8'
            ])

        self.assertEqual(server_cipher.state, CipherState.EARLY)
        self.assertTrue(
            server_cipher.must_decrypt,
            "client will send encrypted early data")
        self.assertFalse(
            server_cipher.must_encrypt,
            "server will send clear server hello")
        self.assertFalse(server_cipher.should_rekey)

        # exchange
        ciphertag = client_cipher.encrypt(b"hello server", b'')
        plain = server_cipher.decrypt(ciphertag, b'')
        self.assertEqual(plain, b"hello server")


    def test_cipher_handshake_after_init(self):
        ChaPoly = TLSCipherSuite[CipherSuites.TLS_CHACHA20_POLY1305_SHA256]
        client_unique = b'client unique value of 32 bytes-'
        shared_key = b'shared key value of 32 bytes----'
        transcript_hash = ChaPoly.digestmod(b'server hello').digest()

        # client side
        client_cipher = ChaPoly('client', client_unique, log_keys=True)
        client_cipher.skip_early_secrets()
        with self.assertLogs('siotls.keylog', logging.INFO) as capture:
            client_cipher.derive_handshake_secrets(shared_key, transcript_hash)
            self._assertKeyLogEqual(capture.output, client_unique,
                ('CLIENT_HANDSHAKE_TRAFFIC_SECRET',
                 'dbefec40bafcc3a522a2b3f5a654cb2968c3d455536d2580bb1f12c7222fa229'),
                ('SERVER_HANDSHAKE_TRAFFIC_SECRET',
                 '8d8d2873468ef0fce8e5b95f3ab55999e2354281804749c521641bd18dd5900e'))

        self.assertEqual(client_cipher.state, CipherState.HANDSHAKE)
        self.assertTrue(
            client_cipher.must_decrypt,
            "server will send encrypted extensions")
        self.assertTrue(
            client_cipher.must_encrypt,
            "client will send encrypted finished")
        self.assertFalse(client_cipher.should_rekey)

        # server side
        server_cipher = ChaPoly('server', client_unique, log_keys=True)
        server_cipher.skip_early_secrets()
        with self.assertLogs('siotls.keylog', logging.INFO) as capture:
            server_cipher.derive_handshake_secrets(shared_key, transcript_hash)
            self._assertKeyLogEqual(capture.output, client_unique,
                ('CLIENT_HANDSHAKE_TRAFFIC_SECRET',
                 'dbefec40bafcc3a522a2b3f5a654cb2968c3d455536d2580bb1f12c7222fa229'),
                ('SERVER_HANDSHAKE_TRAFFIC_SECRET',
                 '8d8d2873468ef0fce8e5b95f3ab55999e2354281804749c521641bd18dd5900e'))

        self.assertEqual(server_cipher.state, CipherState.HANDSHAKE)
        self.assertTrue(
            server_cipher.must_encrypt,
            "server will send encrypted extensions")
        self.assertTrue(
            server_cipher.must_decrypt,
            "client will send encrypted finished")
        self.assertFalse(server_cipher.should_rekey)

        # exchange
        ciphertag = client_cipher.encrypt(b"hello server", b'')
        plain = server_cipher.decrypt(ciphertag, b'')
        self.assertEqual(plain, b"hello server")

        ciphertag = server_cipher.encrypt(b"hello client", b'')
        plain = client_cipher.decrypt(ciphertag, b'')
        self.assertEqual(plain, b"hello client")

    def test_cipher_handshake_after_early(self):
        ChaPoly = TLSCipherSuite[CipherSuites.TLS_CHACHA20_POLY1305_SHA256]
        client_unique = b'client unique value of 32 bytes-'
        pre_shared_key = b'pre shared key value of 32 bytes'
        shared_key = b'shared key value of 32 bytes----'
        ch_transcript_hash = ChaPoly.digestmod(b"client hello").digest()
        sh_transcript_hash = ChaPoly.digestmod(b"server hello").digest()

        # client side
        client_cipher = ChaPoly('client', client_unique, log_keys=True)
        client_cipher.derive_early_secrets(
            pre_shared_key, 'external', ch_transcript_hash)
        with self.assertLogs('siotls.keylog', logging.INFO) as capture:
            client_cipher.derive_handshake_secrets(shared_key, sh_transcript_hash)
            self._assertKeyLogEqual(capture.output, client_unique,
                ('CLIENT_HANDSHAKE_TRAFFIC_SECRET',
                 '0cbf0651c12830f01658a6667a0e01a78017ab28de20b6db24c23bef23db8ec0'),
                ('SERVER_HANDSHAKE_TRAFFIC_SECRET',
                 '31c22e21f05830130ece72713c0a2783652c6f53cfcfa4242431ca2b1e6d55d0'))

        self.assertEqual(client_cipher.state, CipherState.HANDSHAKE)
        self.assertTrue(
            client_cipher.must_decrypt,
            "server will send encrypted extensions")
        self.assertTrue(
            client_cipher.must_encrypt,
            "client will send encrypted finished")
        self.assertFalse(client_cipher.should_rekey)

        # server side
        server_cipher = ChaPoly('server', client_unique, log_keys=True)
        server_cipher.derive_early_secrets(
            pre_shared_key, 'external', ch_transcript_hash)
        with self.assertLogs('siotls.keylog', logging.INFO) as capture:
            server_cipher.derive_handshake_secrets(shared_key, sh_transcript_hash)
            self._assertKeyLogEqual(capture.output, client_unique,
                ('CLIENT_HANDSHAKE_TRAFFIC_SECRET',
                 '0cbf0651c12830f01658a6667a0e01a78017ab28de20b6db24c23bef23db8ec0'),
                ('SERVER_HANDSHAKE_TRAFFIC_SECRET',
                 '31c22e21f05830130ece72713c0a2783652c6f53cfcfa4242431ca2b1e6d55d0'))

        self.assertEqual(server_cipher.state, CipherState.HANDSHAKE)
        self.assertTrue(
            server_cipher.must_encrypt,
            "server will send encrypted extensions")
        self.assertTrue(
            server_cipher.must_decrypt,
            "client will send encrypted finished")
        self.assertFalse(server_cipher.should_rekey)

        # exchange
        ciphertag = client_cipher.encrypt(b"hello server", b'')
        plain = server_cipher.decrypt(ciphertag, b'')
        self.assertEqual(plain, b"hello server")

        ciphertag = server_cipher.encrypt(b"hello client", b'')
        plain = client_cipher.decrypt(ciphertag, b'')
        self.assertEqual(plain, b"hello client")

    def test_cipher_application(self):
        ChaPoly = TLSCipherSuite[CipherSuites.TLS_CHACHA20_POLY1305_SHA256]
        client_unique = b'client unique value of 32 bytes-'
        shared_key = b'shared key value of 32 bytes----'
        sh_transcript_hash = ChaPoly.digestmod(b'server hello').digest()
        sf_transcript_hash = ChaPoly.digestmod(b'server finished').digest()
        cf_transcript_hash = ChaPoly.digestmod(b'client finished').digest()

        # client side
        client_cipher = ChaPoly('client', client_unique, log_keys=True)
        client_cipher.skip_early_secrets()
        client_cipher.derive_handshake_secrets(shared_key, sh_transcript_hash)
        with self.assertLogs('siotls.keylog', logging.INFO) as capture:
            client_cipher.derive_master_secrets(sf_transcript_hash, cf_transcript_hash)
            self._assertKeyLogEqual(capture.output, client_unique,
                ('CLIENT_TRAFFIC_SECRET_0',
                 'b3779f71acf1ed121518da01abaec9eed9fd48eb2f6dbccf1a29f0203e1c12eb'),
                ('SERVER_TRAFFIC_SECRET_0',
                 'f529b987cbe46f37e517d9ae8f92c1eeba82c051acff1a4557fddd3a229900e1'),
                ('EXPORTER_SECRET',
                 'b7bbad0f7b1ee9364f4098dba9008b70d0586c6315d5980676dec3a1b283348a'),
            )

        self.assertEqual(client_cipher.state, CipherState.APPLICATION)
        self.assertTrue(
            client_cipher.must_encrypt,
            "client to send encrypted application data")
        self.assertTrue(
            client_cipher.must_decrypt,
            "server to send encrypted application data")
        self.assertFalse(client_cipher.should_rekey)

        # server side
        server_cipher = ChaPoly('server', client_unique, log_keys=True)
        server_cipher.skip_early_secrets()
        server_cipher.derive_handshake_secrets(shared_key, sh_transcript_hash)
        with self.assertLogs('siotls.keylog', logging.INFO) as capture:
            server_cipher.derive_master_secrets(sf_transcript_hash, cf_transcript_hash)
            self._assertKeyLogEqual(capture.output, client_unique,
                ('CLIENT_TRAFFIC_SECRET_0',
                 'b3779f71acf1ed121518da01abaec9eed9fd48eb2f6dbccf1a29f0203e1c12eb'),
                ('SERVER_TRAFFIC_SECRET_0',
                 'f529b987cbe46f37e517d9ae8f92c1eeba82c051acff1a4557fddd3a229900e1'),
                ('EXPORTER_SECRET',
                 'b7bbad0f7b1ee9364f4098dba9008b70d0586c6315d5980676dec3a1b283348a'),
            )

        self.assertEqual(server_cipher.state, CipherState.APPLICATION)
        self.assertTrue(
            server_cipher.must_encrypt,
            "server to send encrypted application data")
        self.assertTrue(
            server_cipher.must_decrypt,
            "client to send encrypted application data")
        self.assertFalse(server_cipher.should_rekey)

        # exchange
        ciphertag = client_cipher.encrypt(b"hello server", b'')
        plain = server_cipher.decrypt(ciphertag, b'')
        self.assertEqual(plain, b"hello server")

        ciphertag = server_cipher.encrypt(b"hello client", b'')
        plain = client_cipher.decrypt(ciphertag, b'')
        self.assertEqual(plain, b"hello client")

    def test_cipher_sign_verify(self):
        ChaPoly = TLSCipherSuite[CipherSuites.TLS_CHACHA20_POLY1305_SHA256]
        client_unique = b'client unique value of 32 bytes-'
        shared_key = b'shared key value of 32 bytes----'
        sh_transcript_hash = ChaPoly.digestmod(b'server hello').digest()
        cf_transcript_hash = ChaPoly.digestmod(b'client finish').digest()
        sf_transcript_hash = ChaPoly.digestmod(b'server finish').digest()

        client_cipher = ChaPoly('client', client_unique, log_keys=False)
        client_cipher.skip_early_secrets()
        client_cipher.derive_handshake_secrets(shared_key, sh_transcript_hash)
        client_cf_signed = client_cipher.sign_finish(cf_transcript_hash)

        server_cipher = ChaPoly('server', client_unique, log_keys=False)
        server_cipher.skip_early_secrets()
        server_cipher.derive_handshake_secrets(shared_key, sh_transcript_hash)
        server_sf_signed = server_cipher.sign_finish(sf_transcript_hash)

        client_cipher.verify_finish(sf_transcript_hash, server_sf_signed)
        with self.assertRaises(ValueError):
            client_cipher.verify_finish(sf_transcript_hash, client_cf_signed)

        server_cipher.verify_finish(cf_transcript_hash, client_cf_signed)
        with self.assertRaises(ValueError):
            server_cipher.verify_finish(cf_transcript_hash, server_sf_signed)
