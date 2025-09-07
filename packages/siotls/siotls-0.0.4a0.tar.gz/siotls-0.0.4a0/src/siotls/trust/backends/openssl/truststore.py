import typing
from collections import namedtuple
from collections.abc import Collection, Sequence
from datetime import UTC, datetime
from ipaddress import ip_address

from cryptography.x509 import DNSName, IPAddress, load_der_x509_certificate
from cryptography.x509.verification import (
    ClientVerifier,
    PolicyBuilder,
    ServerVerifier,
    Store,
    VerificationError,
)

import siotls.trust
from siotls.asn1types import DerCertificate
from siotls.connection import TLSConnection
from siotls.contents import alerts
from siotls.contents.handshakes.certificate import X509Entry

Entry = namedtuple('Entry', ('cryptocert', 'certificate', 'extensions'))


class OpensslTrustStore(siotls.trust.TrustStore):
    def __init__(
        self,
        der_ca_certificates: Collection[DerCertificate],
    ):
        self._store = Store([
            load_der_x509_certificate(der_cert)
            for der_cert in der_ca_certificates
        ])
        self._policy_builder = PolicyBuilder().store(self._store)

    def verify_chain(self, conn: TLSConnection, entry_chain: Sequence[X509Entry]):
        cert_chain = [
            load_der_x509_certificate(entry.certificate)
            for entry in entry_chain
        ]

        verifier: ClientVerifier | ServerVerifier
        if conn.config.other_side == 'client':
            verifier = self._build_client_verifier()
        else:
            conn.server_hostname = typing.cast('str', conn.server_hostname)
            subject: DNSName | IPAddress
            try:
                server_ip = ip_address(conn.server_hostname)
            except ValueError:
                subject = DNSName(conn.server_hostname)
            else:
                subject = IPAddress(server_ip)
            verifier = self._build_server_verifier(subject)

        try:
            verifier.verify(cert_chain[0], cert_chain[1:])
        except VerificationError as exc:
            raise alerts.BadCertificate from exc

    def _build_client_verifier(self) -> ClientVerifier:
        # override me if you want another policy
        return self._policy_builder \
            .time(datetime.now(UTC)) \
            .build_client_verifier()

    def _build_server_verifier(self, subject) -> ServerVerifier:
        # override me if you want another policy
        return self._policy_builder \
            .time(datetime.now(UTC)) \
            .build_server_verifier(subject)

    def _reorder(self, entry_chain, cert_chain, ordered_cert_chain):
        pairs = [
            (entry, cert)
            for (entry, cert)
            in zip(entry_chain, cert_chain, strict=True)
            if cert in ordered_cert_chain
        ]
        pairs.sort(key=lambda pair: ordered_cert_chain.index(pair[1]))
        return [entry for entry, _ in pairs]
