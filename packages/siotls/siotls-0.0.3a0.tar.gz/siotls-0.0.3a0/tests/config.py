import ipaddress
from datetime import UTC, datetime, timedelta

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)
from cryptography.x509.oid import NameOID

from siotls import TLSConfiguration as TLSConfig
from siotls.iana import CipherSuites, NamedGroup, SignatureScheme
from siotls.trust.backends.openssl import X509Verifier

from . import CRYPTO_BACKEND, test_temp_dir

now = datetime.now(UTC)
VALIDITY = timedelta(minutes=10)

key_usage_ca = x509.KeyUsage(  # cert and crl sign
    digital_signature=True, content_commitment=False, key_encipherment=False,
    data_encipherment=False, key_agreement=False, key_cert_sign=True,
    crl_sign=True, encipher_only=False, decipher_only=False,
)
key_usage_tls = x509.KeyUsage(  # digital signature
    digital_signature=True, content_commitment=False, key_encipherment=False,
    data_encipherment=False, key_agreement=False, key_cert_sign=False,
    crl_sign=False, encipher_only=False, decipher_only=False,
)
x_key_usage_ca = x509.ExtendedKeyUsage([
    x509.oid.ExtendedKeyUsageOID.OCSP_SIGNING,
    x509.oid.ExtendedKeyUsageOID.TIME_STAMPING,
])
x_key_usage_client = x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH])
x_key_usage_server = x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.SERVER_AUTH])
constraint_ca_ko = x509.BasicConstraints(ca=False, path_length=None)

#
# CA
#
ca_domain = 'ca.siotls.localhost'
ca_subject = x509.Name([
    x509.NameAttribute(NameOID.COMMON_NAME, "siotls test CA"),
])
ca_privkey = ec.generate_private_key(ec.SECP256R1())
ca_pubkey = ca_privkey.public_key()
ca_der_pubkey = ca_pubkey.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
ca_ski = x509.SubjectKeyIdentifier.from_public_key(ca_pubkey)
ca_cert = (
    x509.CertificateBuilder()
    .subject_name(ca_subject)
    .issuer_name(ca_subject)
    .public_key(ca_pubkey)
    .serial_number(x509.random_serial_number())
    .not_valid_before(now)
    .not_valid_after(now + VALIDITY)
    .add_extension(x509.BasicConstraints(ca=True, path_length=1), critical=True)
    .add_extension(key_usage_ca, critical=True)
#    .add_extension(x_key_usage_ca, critical=False)
    .add_extension(
        x509.SubjectAlternativeName([x509.DNSName(ca_domain)]),
        critical=False)
    .add_extension(ca_ski, critical=False)
    .sign(ca_privkey, hashes.SHA256())
)
ca_der_cert = ca_cert.public_bytes(Encoding.DER)
ca_aki = x509.AuthorityKeyIdentifier(
    ca_ski.digest, [x509.DNSName(ca_domain)], ca_cert.serial_number
)
(test_temp_dir/'ca-pubkey.der').write_bytes(ca_der_pubkey)
(test_temp_dir/'ca-pubkey.pem').write_bytes(ca_pubkey.public_bytes(
    Encoding.PEM, PublicFormat.SubjectPublicKeyInfo))
(test_temp_dir/'ca-cert.der').write_bytes(ca_der_cert)
(test_temp_dir/'ca-cert.pem').write_bytes(ca_cert.public_bytes(Encoding.PEM))

#
# Server
#
server_domain = 'server.siotls.localhost'
server_privkey = ec.generate_private_key(ec.SECP256R1())
server_der_privkey = server_privkey.private_bytes(
    Encoding.DER, PrivateFormat.PKCS8, NoEncryption())
server_pubkey = server_privkey.public_key()
server_der_pubkey = server_pubkey.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
server_cert = (
    x509.CertificateBuilder()
    .subject_name(x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "siotls test server"),
    ]))
    .issuer_name(ca_subject)
    .public_key(server_pubkey)
    .serial_number(x509.random_serial_number())
    .not_valid_before(now)
    .not_valid_after(now + VALIDITY)
    .add_extension(constraint_ca_ko, critical=True)
    .add_extension(key_usage_tls, critical=True)
    .add_extension(x_key_usage_server, critical=False)
    .add_extension(
         x509.SubjectAlternativeName([
            x509.DNSName(server_domain),
            x509.IPAddress(ipaddress.IPv4Address('127.0.0.2')),
        ]),
        critical=False)
    .add_extension(ca_aki, critical=False)
    .add_extension(
        x509.SubjectKeyIdentifier.from_public_key(server_pubkey),
        critical=False)
    .sign(ca_privkey, hashes.SHA256())
)
server_der_cert = server_cert.public_bytes(Encoding.DER)
(test_temp_dir/'server-privkey.der').write_bytes(server_der_privkey)
(test_temp_dir/'server-privkey.pem').write_bytes(server_privkey.private_bytes(
    Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()))
(test_temp_dir/'server-pubkey.der').write_bytes(server_der_pubkey)
(test_temp_dir/'server-pubkey.pem').write_bytes(server_pubkey.public_bytes(
    Encoding.PEM, PublicFormat.SubjectPublicKeyInfo))
(test_temp_dir/'server-cert.der').write_bytes(server_der_cert)
(test_temp_dir/'server-cert.pem').write_bytes(server_cert.public_bytes(Encoding.PEM))

#
# Client
#
client_privkey = ec.generate_private_key(ec.SECP256R1())
client_der_privkey = client_privkey.private_bytes(
    Encoding.DER, PrivateFormat.PKCS8, NoEncryption())
client_pubkey = client_privkey.public_key()
client_der_pubkey = client_pubkey.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
client_cert = (
    x509.CertificateBuilder()
    .subject_name(x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "siotls test client"),
    ]))
    .issuer_name(ca_subject)
    .public_key(client_pubkey)
    .serial_number(x509.random_serial_number())
    .not_valid_before(now)
    .not_valid_after(now + VALIDITY)
    .add_extension(constraint_ca_ko, critical=True)
    .add_extension(key_usage_tls, critical=True)
    .add_extension(x_key_usage_client, critical=False)
    .add_extension(ca_aki, critical=False)
    .add_extension(
        x509.SubjectKeyIdentifier.from_public_key(server_pubkey),
        critical=False)
    .sign(ca_privkey, hashes.SHA256())
)
client_der_cert = client_cert.public_bytes(Encoding.DER)
(test_temp_dir/'client-privkey.der').write_bytes(client_der_privkey)
(test_temp_dir/'client-privkey.pem').write_bytes(client_privkey.private_bytes(
    Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()))
(test_temp_dir/'client-pubkey.der').write_bytes(client_der_pubkey)
(test_temp_dir/'client-pubkey.pem').write_bytes(client_pubkey.public_bytes(
    Encoding.PEM, PublicFormat.SubjectPublicKeyInfo))
(test_temp_dir/'client-cert.der').write_bytes(client_der_cert)
(test_temp_dir/'client-cert.pem').write_bytes(client_cert.public_bytes(Encoding.PEM))

test_x509verifier = X509Verifier([ca_der_cert])
test_trusted_public_keys = [client_der_pubkey, server_der_pubkey]

#
# Configurations
#
server_config = TLSConfig(
    'server',
    private_key=server_der_privkey,
    certificate_chain=[server_der_cert, ca_der_cert],
)
client_config = TLSConfig(
    'client',
    x509verifier=test_x509verifier,
)

#
# Per-crypto-backend default algorithms
#
openssl_cipher_suites = (
    CipherSuites.TLS_CHACHA20_POLY1305_SHA256,
    CipherSuites.TLS_AES_256_GCM_SHA384,
    CipherSuites.TLS_AES_128_GCM_SHA256,
)
openssl_key_exchanges = (
    NamedGroup.x25519,
    NamedGroup.secp256r1,
)
openssl_signature_algorithms = (
    SignatureScheme.ed25519,
    SignatureScheme.ecdsa_secp256r1_sha256,
    SignatureScheme.ecdsa_secp384r1_sha384,
    SignatureScheme.ecdsa_secp521r1_sha512,
    SignatureScheme.rsa_pss_rsae_sha256,
    SignatureScheme.rsa_pss_rsae_sha384,
    SignatureScheme.rsa_pss_rsae_sha512,
)

hacl_cipher_suites = (
    CipherSuites.TLS_CHACHA20_POLY1305_SHA256,
)
hacl_key_exchanges = (
    NamedGroup.x25519,
)
hacl_signature_algorithms = (
    SignatureScheme.ed25519,
    SignatureScheme.ecdsa_secp256r1_sha256,
)

default_cipher_suites, default_key_exchanges, default_signature_algorithms = {
    'openssl': (openssl_cipher_suites, openssl_key_exchanges, openssl_signature_algorithms),
    'hacl': (hacl_cipher_suites, hacl_key_exchanges, hacl_signature_algorithms),
}[CRYPTO_BACKEND]

assert tuple(server_config.cipher_suites) == default_cipher_suites  # noqa: S101
assert tuple(server_config.key_exchanges) == default_key_exchanges  # noqa: S101
assert tuple(server_config.signature_algorithms) == default_signature_algorithms  # noqa: S101
