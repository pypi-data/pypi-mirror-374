import contextlib
import dataclasses
import ipaddress
import shutil
import ssl
import unittest
from os import environ, fspath
from pathlib import Path
from textwrap import dedent
from unittest.mock import patch

from parameterized import parameterized  # type: ignore[import-untyped]

from siotls import TLSConnection
from siotls.contents import alerts
from siotls.crypto import TLSCipherSuite, TLSKeyExchange
from siotls.iana import CipherSuites, NamedGroup, SignatureScheme

from . import TAG_INTEGRATION, NetworkMixin, TestCase, test_temp_dir
from .config import (
    client_config,
    empty_trust_store,
    server_config,
    server_domain,
    server_rsa_config,
    test_trust_store,
)

OPENSSL_PATH = shutil.which('openssl')


@unittest.skipUnless(TAG_INTEGRATION, "enable with SIOTLS_INTEGRATION=1")
class TestOpenSSL(TestCase):
    def _test_openssl_client(self, cipher, key_exchange):
        context = ssl.create_default_context(
            cafile=fspath(test_temp_dir.joinpath('ca-cert.pem'))
        )
        openssl_in = siotls_out = ssl.MemoryBIO()
        openssl_out = siotls_in = ssl.MemoryBIO()
        openssl_sock = context.wrap_bio(openssl_in, openssl_out)

        config = dataclasses.replace(
            server_config,
            cipher_suites=[cipher],
            key_exchanges=[key_exchange],
        )
        conn = TLSConnection(config)
        conn.initiate_connection()

        # ClientHello
        with contextlib.suppress(ssl.SSLWantReadError):
            openssl_sock.do_handshake()
        conn.receive_data(siotls_in.read())
        siotls_out.write(conn.data_to_send())

        if key_exchange != NamedGroup.x25519:
            # ClientHello again after HelloRetryRequest
            with contextlib.suppress(ssl.SSLWantReadError):
                openssl_sock.do_handshake()
            conn.receive_data(siotls_in.read())
            siotls_out.write(conn.data_to_send())

        # Finished after ServerHello/Cert/CertVerify/Finished
        openssl_sock.do_handshake()
        conn.receive_data(siotls_in.read())
        siotls_out.write(conn.data_to_send())

        # Connection established, exchange a ping pong
        self.assertTrue(conn.is_post_handshake())
        openssl_sock.write(b"ping!\n")
        conn.receive_data(siotls_in.read())
        self.assertEqual(conn.data_to_read(), b"ping!\n")
        conn.send_data(b"pong!\n")
        siotls_out.write(conn.data_to_send())
        self.assertEqual(openssl_sock.read(), b"pong!\n")

    @parameterized.expand([
        (cipher.name[4:], cipher)
        for cipher in [
            CipherSuites.TLS_AES_128_GCM_SHA256,
            CipherSuites.TLS_AES_256_GCM_SHA384,
            CipherSuites.TLS_CHACHA20_POLY1305_SHA256,
        ]
        if cipher in TLSCipherSuite
    ])
    def test_openssl_client_cipher(self, _, cipher):
        group = server_config.key_exchanges[0]
        self._test_openssl_client(cipher, group)

    @parameterized.expand([
        (group.name, group)
        for group in NamedGroup
        if group in TLSKeyExchange
    ])
    def test_openssl_client_group(self, _, group):
        cipher = server_config.cipher_suites[0]
        self._test_openssl_client(cipher, group)


    def _test_openssl_server(self, cipher, key_exchange):
        context = ssl.create_default_context(
            purpose=ssl.Purpose.CLIENT_AUTH,
            cafile=fspath(test_temp_dir.joinpath('ca-cert.pem'))
        )
        context.load_cert_chain(
            fspath(test_temp_dir.joinpath('server-cert.pem')),
            fspath(test_temp_dir.joinpath('server-privkey.pem')),
        )
        openssl_in = siotls_out = ssl.MemoryBIO()
        openssl_out = siotls_in = ssl.MemoryBIO()
        openssl_sock = context.wrap_bio(openssl_in, openssl_out, server_side=True)

        config = dataclasses.replace(
            client_config,
            cipher_suites=[cipher],
            key_exchanges=[key_exchange],
        )
        conn = TLSConnection(config, server_domain)

        # ClientHello
        conn.initiate_connection()
        siotls_out.write(conn.data_to_send())

        with contextlib.suppress(ssl.SSLWantReadError):
            openssl_sock.do_handshake()
        conn.receive_data(siotls_in.read())
        siotls_out.write(conn.data_to_send())

        # Finished after ServerHello/Cert/CertVerify/Finished
        openssl_sock.do_handshake()

        # Connection established, exchange a ping pong
        self.assertTrue(conn.is_post_handshake())
        openssl_sock.write(b"ping!\n")
        conn.receive_data(siotls_in.read())
        self.assertEqual(conn.data_to_read(), b"ping!\n")
        conn.send_data(b"pong!\n")
        siotls_out.write(conn.data_to_send())
        self.assertEqual(openssl_sock.read(), b"pong!\n")

    @parameterized.expand([
        (cipher.name[4:], cipher)
        for cipher in [
            CipherSuites.TLS_AES_128_GCM_SHA256,
            CipherSuites.TLS_AES_256_GCM_SHA384,
            CipherSuites.TLS_CHACHA20_POLY1305_SHA256,
        ]
        if cipher in TLSCipherSuite
    ])
    def test_openssl_server_cipher(self, _, cipher):
        group = client_config.key_exchanges[0]
        self._test_openssl_server(cipher, group)

    @parameterized.expand([
        (group.name, group)
        for group in NamedGroup
        if group in TLSKeyExchange
    ])
    def test_openssl_server_group(self, _, group):
        cipher = client_config.cipher_suites[0]
        self._test_openssl_server(cipher, group)


    @patch.dict(environ, {'SSLKEYLOGFILE': fspath(Path.home()/'.sslkeylogfile')})
    def test_openssl_client_hello_retry_request(self):
        if NamedGroup.secp384r1 not in TLSKeyExchange:
            self.skipTest("incompatible crypto backend")

        context = ssl.create_default_context(
            cafile=fspath(test_temp_dir.joinpath('ca-cert.pem'))
        )
        openssl_in = siotls_out = ssl.MemoryBIO()
        openssl_out = siotls_in = ssl.MemoryBIO()
        openssl_sock = context.wrap_bio(openssl_in, openssl_out)

        config = dataclasses.replace(
            server_config,
            key_exchanges=[NamedGroup.secp384r1],
            log_keys=True,
        )
        conn = TLSConnection(config)
        conn.initiate_connection()

        # ClientHello
        with contextlib.suppress(ssl.SSLWantReadError):
            openssl_sock.do_handshake()
        conn.receive_data(siotls_in.read())
        siotls_out.write(conn.data_to_send())

        # ClientHello again after HelloRetryRequest
        with contextlib.suppress(ssl.SSLWantReadError):
            openssl_sock.do_handshake()
        conn.receive_data(siotls_in.read())
        siotls_out.write(conn.data_to_send())

        # Finished after ServerHello/Cert/CertVerify/Finished
        openssl_sock.do_handshake()
        conn.receive_data(siotls_in.read())
        siotls_out.write(conn.data_to_send())

        # Connection established, exchange a ping pong
        self.assertTrue(conn.is_post_handshake())
        openssl_sock.write(b"ping!\n")
        conn.receive_data(siotls_in.read())
        self.assertEqual(conn.data_to_read(), b"ping!\n")
        conn.send_data(b"pong!\n")
        siotls_out.write(conn.data_to_send())
        self.assertEqual(openssl_sock.read(), b"pong!\n")



@unittest.skipUnless(TAG_INTEGRATION, "enable with SIOTLS_INTEGRATION=1")
@unittest.skipUnless(OPENSSL_PATH, "openssl not found in path")
class TestOpenSslCli(NetworkMixin, TestCase):
    def openssl_sclient(self, *args, **popen_kwargs):
        try:
            ipaddress.IPv6Address(self.host)
        except ValueError:
            addr = f'{self.host}:{self.port}'
        else:
            addr = f'[{self.host}]:{self.port}'

        proc = self.popen([
            OPENSSL_PATH,
            's_client',
            '-brief',
            '-noservername',
            '-verifyCAfile', str(test_temp_dir/'ca-cert.pem'),
            '-verify_return_error',
            '-connect', addr,
            *args,
        ], **popen_kwargs)

        client, client_info = self.socket.accept()
        self.addCleanup(client.close)

        return proc, client

    def test_openssl_sclient(self):
        proc, client = self.openssl_sclient()
        conn = TLSConnection(server_rsa_config)
        with conn.wrap(client) as sclient:
            proc.stdin.write(b"Hello\n")
            proc.stdin.flush()
            self.assertEqual(sclient.read(), b"Hello\n")

        self.assertEqual(proc.wait(timeout=1), 0)
        self.assertEqual(proc.stdout.read(), b"")
        self.assertEqual(proc.stderr.read().decode(), dedent("""\
            CONNECTION ESTABLISHED
            Protocol version: TLSv1.3
            Ciphersuite: TLS_CHACHA20_POLY1305_SHA256
            Peer certificate: CN = siotls test server (rsa)
            Hash used: SHA256
            Signature type: RSA-PSS
            Verification: OK
            Server Temp Key: X25519, 253 bits
        """))

    def test_openssl_sclient_rsa_pkcs1(self):
        # openssl sends a single ClientHello that is compatible with
        # both TLS 1.2 and TLS 1.3, with a "supported_version" extension
        # to advertise it supports both.
        # But it includes the union of supported algorithms for both 1.2
        # and 1.3, and then strip its list down when it knows via the
        # ServerHello if it is really 1.2 or 1.3.
        # So it advertises it supports rsa pkcs1 in its ClientHello, but
        # actually only support it in 1.2, and not in 1.3. Hence if the
        # server (rightfully) picks rsa pkcs1, openssl is gonna reject
        # the connection nonetheless.
        # This test is about testing this weird condition.
        proc, client = self.openssl_sclient()
        conn = TLSConnection(dataclasses.replace(server_rsa_config,
            private_key_signature_algorithms=(SignatureScheme.rsa_pkcs1_sha256,))
        )
        conn.initiate_connection()
        conn.receive_data(client.recv(16384))
        self.assertEqual(
            conn.nconfig.signature_algorithm,
            SignatureScheme.rsa_pkcs1_sha256,
        )
        client.send(conn.data_to_send())

        with self.assertRaises(alerts.IllegalParameter):
            conn.receive_data(client.recv(16384))
        self.assertEqual(conn._state.name(), 'Failed')
        client.close()

        self.assertNotEqual(proc.wait(timeout=1), 0)
        self.assertEqual(proc.stdout.read(), b"")
        self.assertIn(b"wrong signature type", proc.stderr.read())

    def test_openssl_sclient_mtls_missing_client_cert(self):
        proc, client = self.openssl_sclient()
        conn = TLSConnection(dataclasses.replace(server_config,
            truststore=test_trust_store,
        ))
        conn.initiate_connection()
        conn.receive_data(client.recv(16384))
        client.send(conn.data_to_send())
        with self.assertRaises(alerts.CertificateRequired):
            conn.receive_data(client.recv(16384))
        client.send(conn.data_to_send())
        client.close()
        self.assertNotEqual(proc.wait(timeout=1), 0)
        self.assertEqual(proc.stdout.read(), b"")
        self.assertIn(b"alert certificate required", proc.stderr.read())

    def test_openssl_sclient_mtls_bad_client_cert(self):
        proc, client = self.openssl_sclient(
            '-key', fspath(test_temp_dir/'client-privkey.der'),
            '-keyform', 'DER',
            '-cert', fspath(test_temp_dir/'client-cert.der'),
            '-certform', 'DER',
            '-cert_chain', fspath(test_temp_dir/'ca-cert.der'),
            '-build_chain',
        )
        conn = TLSConnection(dataclasses.replace(server_config,
            truststore=empty_trust_store,
        ))
        conn.initiate_connection()
        conn.receive_data(client.recv(16384))
        client.send(conn.data_to_send())
        with self.assertRaises(alerts.BadCertificate):
            conn.receive_data(client.recv(16384))
        client.send(conn.data_to_send())
        client.close()
        self.assertNotEqual(proc.wait(timeout=1), 0)
        self.assertEqual(proc.stdout.read(), b"")
        self.assertIn(b"alert bad certificate", proc.stderr.read())

    def test_openssl_sclient_mtls_with_client_cert(self):
        proc, client = self.openssl_sclient(
            '-key', fspath(test_temp_dir/'client-privkey.der'),
            '-keyform', 'DER',
            '-cert', fspath(test_temp_dir/'client-cert.der'),
            '-certform', 'DER',
            '-cert_chain', fspath(test_temp_dir/'ca-cert.der'),
            '-build_chain',
        )
        conn = TLSConnection(server_config)

        with conn.wrap(client) as sclient:
            proc.stdin.write(b"Hello\n")
            proc.stdin.flush()
            self.assertEqual(sclient.read(), b"Hello\n")

        self.assertEqual(proc.wait(timeout=1), 0)
        self.assertEqual(proc.stdout.read(), b"")
        self.assertEqual(proc.stderr.read().decode(), dedent("""\
            CONNECTION ESTABLISHED
            Protocol version: TLSv1.3
            Ciphersuite: TLS_CHACHA20_POLY1305_SHA256
            Peer certificate: CN = siotls test server
            Hash used: SHA256
            Signature type: ECDSA
            Verification: OK
            Server Temp Key: X25519, 253 bits
        """))
