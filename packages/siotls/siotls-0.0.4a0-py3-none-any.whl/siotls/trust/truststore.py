import abc
from collections.abc import Sequence
from typing import TYPE_CHECKING

from siotls.contents.handshakes.certificate import X509Entry

if TYPE_CHECKING:
    from siotls import TLSConnection
    from siotls.contents import alerts  # noqa: F401


class TrustStore(metaclass=abc.ABCMeta):
    """ Abstract class that the trust backends implement. """

    @abc.abstractmethod
    def verify_chain(
        self,
        conn: 'TLSConnection',
        entry_chain: Sequence[X509Entry],
    ) -> None:
        """
        Verify that the ``entry_chain`` is composed of valid
        certificates that can be re-ordered to form a chain of trust
        anchored with a trusted certificate.

        In the case of a server certificate, also verify that the first
        certificate in the chain is a subject certificate whoose
        :abbr:`CN (Common Name)` or :abbr:`SAN (Subject Alternative
        Names)` match with ``conn.server_hostname`` (if set).

        :raises alerts.BadCertificate: When the verification failed,
            that it would be unsafe to continue using the connection.
        """
        raise NotImplementedError
