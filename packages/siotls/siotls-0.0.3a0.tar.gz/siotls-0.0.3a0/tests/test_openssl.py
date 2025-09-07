import contextlib
import dataclasses
import ssl
import unittest
from os import environ, fspath
from pathlib import Path
from unittest.mock import patch

from parameterized import parameterized

from siotls import TLSConnection
from siotls.crypto import TLSCipherSuite, TLSKeyExchange
from siotls.iana import CipherSuites, NamedGroup

from . import TAG_INTEGRATION, TestCase, test_temp_dir
from .config import client_config, server_config, server_domain


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
