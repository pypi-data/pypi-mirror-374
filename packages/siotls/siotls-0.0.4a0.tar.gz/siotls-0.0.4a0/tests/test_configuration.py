import dataclasses
from collections import defaultdict
from unittest.mock import patch

import asn1crypto.keys  # type: ignore[import-untyped]
import asn1crypto.x509  # type: ignore[import-untyped]

from siotls.configuration import TLSConfiguration, TLSNegotiatedConfiguration
from siotls.crypto import TLSSignatureScheme
from siotls.iana import CertificateType, CipherSuites, MaxFragmentLengthOctets
from siotls.utils import RegistryMeta

from . import TestCase
from .config import (
    ca_der_cert,
    client_der_cert,
    client_der_privkey,
    client_der_pubkey,
    default_cipher_suites,
    default_key_exchanges,
    default_signature_algorithms,
    server_der_cert,
    server_der_privkey,
    server_der_pubkey,
    test_trust_store,
)


class TestConfigurationCommon(TestCase):
    def test_config_no_crypto_backend(self):
        with (
            patch.object(RegistryMeta, '__bool__', lambda *_: False),
            self.assertRaises(RuntimeError) as capture_exc,
        ):
            TLSConfiguration('client')
        self.assertEqual(capture_exc.exception.args[0].splitlines()[0],
            "No cipher suite available, surely because no crypto "
            "backend is installed."
        )

    def test_config_no_algo(self):
        with self.assertRaises(ValueError) as capture_exc:
            TLSConfiguration('client', cipher_suites=[])
        self.assertEqual(capture_exc.exception.args[0].splitlines()[0],
            "at least one TLSConfiguration.cipher_suites must be provided"
        )

    def test_config_missing_algo_in_crypto_backend(self):
        with (
            patch.object(RegistryMeta, '__contains__', lambda *_: False),
            self.assertRaises(ValueError) as capture_exc,
        ):
            TLSConfiguration('client', cipher_suites=[
                CipherSuites.TLS_AES_128_GCM_SHA256,
            ])
        self.assertEqual(capture_exc.exception.args[0].splitlines()[0],
            "the following algorithms are not available with the "
            "installed crypto backend, and must be removed from the "
            "configuration:"
        )

    def test_config_certchain_no_privkey(self):
        with self.assertRaises(ValueError) as capture_exc:
            TLSConfiguration(
                'client',
                certificate_chain=[client_der_cert, ca_der_cert]
            )
        self.assertEqual(capture_exc.exception.args[0],
            "certificate chain provided but private key missing"
        )

    def test_config_pubkey_no_privkey(self):
        with self.assertRaises(ValueError) as capture_exc:
            TLSConfiguration(
                'client',
                public_key=client_der_pubkey,
            )
        self.assertEqual(capture_exc.exception.args[0],
            "public key provided but private key missing"
        )

    def test_config_certchain_privkey_mismatch(self):
        with self.assertRaises(ValueError) as capture_exc:
            TLSConfiguration(
                'client',
                private_key=client_der_privkey,
                certificate_chain=[server_der_cert, ca_der_cert]
            )
        self.assertEqual(capture_exc.exception.args[0],
            "the public key found in the first certificate is not the "
            "counter part of the private key"
        )

    def test_config_pubkey_privkey_mismatch(self):
        with self.assertRaises(ValueError) as capture_exc:
            TLSConfiguration(
                'client',
                private_key=client_der_privkey,
                public_key=server_der_pubkey,
            )
        self.assertEqual(capture_exc.exception.args[0],
            "the public key is not the counter part of the private key"
        )

    def test_config_certchain_no_algo(self):
        with (
            patch.object(
                TLSSignatureScheme,
                '_signature_pubkey_oid_registry',
                defaultdict(list)
            ),
            self.assertRaises(ValueError) as capture_exc
        ):
            TLSConfiguration(
                'client',
                private_key=client_der_privkey,
                certificate_chain=[client_der_cert, ca_der_cert]
            )
        self.assertEqual(capture_exc.exception.args[0],
            "the crypto backend doesn't support the private key"
        )

    def test_config_pubkey_no_algo(self):
        with (
            patch.object(
                TLSSignatureScheme,
                '_signature_pubkey_oid_registry',
                defaultdict(list)
            ),
            self.assertRaises(ValueError) as capture_exc
        ):
            TLSConfiguration(
                'client',
                private_key=client_der_privkey,
                public_key=client_der_pubkey,
            )
        self.assertEqual(capture_exc.exception.args[0],
            "the crypto backend doesn't support the private key"
        )


class TestConfigurationClient(TestCase):
    def test_config_client_default(self):
        with self.assertLogs('siotls.configuration', 'WARNING') as capture:
            client_config = TLSConfiguration('client')

        self.assertEqual(dataclasses.asdict(client_config), {
            'side': 'client',
            'cipher_suites': default_cipher_suites,
            'key_exchanges': default_key_exchanges,
            'signature_algorithms': default_signature_algorithms,
            'truststore': None,
            'trusted_public_keys': (),
            'private_key': None,
            'private_key_signature_algorithms':
                # there's 0 logic for this one, and it is tedious to
                # copy/paste.
                client_config.private_key_signature_algorithms,
            'public_key': None,
            'certificate_chain': (),
            'max_fragment_length': MaxFragmentLengthOctets.MAX_16384,
            'alpn': (),
            'log_keys': False,
        })
        self.assertIsNone(client_config.asn1_public_key)
        self.assertIsNone(client_config.asn1_private_key)
        self.assertEqual(client_config.asn1_certificate_chain, [])
        self.assertEqual(client_config.asn1_trusted_public_keys, [])
        self.assertFalse(client_config.require_peer_authentication)
        self.assertEqual(client_config.certificate_types, [])
        self.assertEqual(client_config.peer_certificate_types, [CertificateType.X509])
        self.assertEqual(client_config.other_side, 'server')
        self.assertEqual(capture.output, [
            "WARNING:siotls.configuration:missing trust store or list "
                "of trusted public keys, will not verify the peer's "
                "certificate",
        ])

class TestConfigurationServer(TestCase):
    def test_config_server_default(self):
        with self.assertNoLogs('siotls.configuration'):
            server_config = TLSConfiguration(
                'server',
                private_key=server_der_privkey,
                certificate_chain=[server_der_cert, ca_der_cert],
            )

        self.assertEqual(dataclasses.asdict(server_config), {
            'side': 'server',
            'cipher_suites': default_cipher_suites,
            'key_exchanges': default_key_exchanges,
            'signature_algorithms': default_signature_algorithms,
            'truststore': None,
            'trusted_public_keys': (),
            'private_key': server_der_privkey,
            'private_key_signature_algorithms':
                # there's 0 logic for this one, and it is tedious to
                # copy/paste.
                server_config.private_key_signature_algorithms,
            'public_key': None,
            'certificate_chain': [server_der_cert, ca_der_cert],
            'max_fragment_length': MaxFragmentLengthOctets.MAX_16384,
            'alpn': (),
            'log_keys': False,
        })
        self.assertIsInstance(
            server_config.asn1_public_key,
            asn1crypto.keys.PublicKeyInfo,
        )
        self.assertIsInstance(
            server_config.asn1_private_key,
            asn1crypto.keys.PrivateKeyInfo,
        )
        self.assertEqual(len(server_config.asn1_certificate_chain), 2)
        self.assertIsInstance(
            server_config.asn1_certificate_chain[0],
            asn1crypto.x509.Certificate,
        )
        self.assertEqual(server_config.asn1_trusted_public_keys, [])
        self.assertFalse(server_config.require_peer_authentication)
        self.assertEqual(server_config.certificate_types, [CertificateType.X509])
        self.assertEqual(server_config.peer_certificate_types, [])
        self.assertEqual(server_config.other_side, 'client')

    def test_config_server_missing_priv_key(self):
        with self.assertRaises(ValueError) as capture_exc:
            TLSConfiguration(
                'server',
                certificate_chain=[server_der_cert, ca_der_cert],
            )
        self.assertEqual(
            capture_exc.exception.args[0],
            "a private key is mandatory server side"
        )

    def test_config_server_missing_cert(self):
        with self.assertRaises(ValueError) as capture_exc:
            TLSConfiguration(
                'server',
                private_key=server_der_privkey,
            )
        self.assertEqual(
            capture_exc.exception.args[0],
            "a certificate chain or a public key is mandatory server side"
        )

    def test_config_server_cant_max_fragment_length(self):
        with self.assertRaises(ValueError) as capture_exc:
            TLSConfiguration(
                'server',
                private_key=server_der_privkey,
                public_key=server_der_pubkey,
                max_fragment_length=MaxFragmentLengthOctets.MAX_1024
            )
        self.assertEqual(capture_exc.exception.args[0],
            "max fragment length is only configurable client side")

    def test_config_server_mtls(self):
        with self.assertLogs('siotls.configuration') as capture:
            server_config = TLSConfiguration(
                'server',
                private_key=server_der_privkey,
                public_key=server_der_pubkey,
                truststore=test_trust_store,
                trusted_public_keys=[client_der_pubkey],
            )
        self.assertTrue(server_config.require_peer_authentication)
        self.assertEqual(server_config.certificate_types, [
            CertificateType.RAW_PUBLIC_KEY,
        ])
        self.assertEqual(server_config.peer_certificate_types, [
            CertificateType.X509,
            CertificateType.RAW_PUBLIC_KEY,
        ])
        self.assertEqual(capture.output, [
            "INFO:siotls.configuration:a trust store and/or a list of "
                "trusted public keys is provided, client certificates "
                "will be requested"
        ])

class TestNegotiatedConfiguration(TestCase):
    def test_nconfig_default(self):
        nconfig = TLSNegotiatedConfiguration()
        self.assertEqual(dataclasses.asdict(nconfig), {
            'cipher_suite': None,
            'key_exchange': None,
            'signature_algorithm': None,
            'alpn': ...,
            'max_fragment_length': None,
            'client_certificate_type': None,
            'server_certificate_type': None,
            'peer_signature_algorithm': None,
            'peer_certificate_chain': None,
            'peer_public_key': None,
        })
        self.assertIsNone(nconfig.peer_asn1_certificate_chain)
        self.assertIsNone(nconfig.peer_asn1_public_key)

    def test_nconfig_copy(self):
        nconfig1 = TLSNegotiatedConfiguration()
        nconfig2 = nconfig1.copy()
        self.assertEqual(nconfig1, nconfig2)
        self.assertIsNot(nconfig1, nconfig2)

    def test_nconfig_freeze(self):
        nconfig = TLSNegotiatedConfiguration()
        with self.assertRaises(TypeError):
            del nconfig.cipher_suite
        nconfig.freeze()
        with self.assertRaises(dataclasses.FrozenInstanceError):
            nconfig.cipher_suite = CipherSuites.TLS_AES_128_GCM_SHA256

    def test_nconfig_peer_cert(self):
        nconfig = TLSNegotiatedConfiguration()
        self.assertIsNone(nconfig.peer_asn1_certificate_chain)
        self.assertIsNone(nconfig.peer_asn1_public_key)

        nconfig.peer_certificate_chain = [server_der_cert, ca_der_cert]
        self.assertEqual(len(nconfig.peer_asn1_certificate_chain), 2)
        self.assertIsInstance(
            nconfig.peer_asn1_certificate_chain[0], asn1crypto.x509.Certificate)
        self.assertIsInstance(
            nconfig.peer_asn1_public_key, asn1crypto.keys.PublicKeyInfo)

        nconfig.peer_public_key = server_der_pubkey
        self.assertIsInstance(
            nconfig.peer_asn1_public_key, asn1crypto.keys.PublicKeyInfo)

        nconfig.freeze()
