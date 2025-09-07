"""
The Transcript Hash is a running sha2 of the handshake messages
exchanged when establishing the secure connection. The digest is used
many times, at various stages of the exchange, by
:class:`~siotls.crypto.cipher_suites.TLSCipherSuite`. The digest,
together with the key exchanged via
:mod:`~siotls.contents.handshakes.extensions.key_share` or
:mod:`~siotls.contents.handshakes.extensions.pre_shared_key`, is used to
generate the many secrets key used by the AEAD algorithms to encrypt
exchanges.

There are shenanigans regarding
:class:`~siotls.contents.handshakes.client_hello.ClientHello` and
:class:`~siotls.contents.handshakes.server_hello.HelloRetryRequest` that
make the implementation unfortunately not trivial.

**About Client Hello**

The client can offer multiple cipher suites in its first
:class:`~siotls.contents.handshakes.client_hello.ClientHello`, the
different offered cipher suites can come with different hashing
algorithm, e.g. :attr:`~siotls.iana.CipherSuites.TLS_AES_128_GCM_SHA256`
vs :attr:`~siotls.iana.CipherSuites.TLS_AES_256_GCM_SHA384` (SHA256 vs
SHA386). The actual hashing algorithm to use for this connection will
only be known with the
:class:`~siotls.contents.handshakes.server_hello.ServerHello` /
:class:`~siotls.contents.handshakes.server_hello.HelloRetryRequest`
hanshake of the server.

This means that either (1) we have to keep the
:class:`~siotls.contents.handshakes.client_hello.ClientHello` message
around until we know what hash algorithm the server decides to use and
only then compute the transcript hash, either (2) we save multiple
hashes and then discard those we won't use. The current implementation
uses (2) as several passages of the TLS RFC hint at this choice and that
it seems to be the common method used by many TLS implementations.

In cases multiple differents hashing algorithms are offered, that until
receiving :class:`~siotls.contents.handshakes.server_hello.ServerHello`
/ :class:`~siotls.contents.handshakes.server_hello.HelloRetryRequest` we
do not know which one will be used, it is forbidden to request a digest
(via the :meth:`digest` and :meth:`hexdigest` methods) before calling
:meth:`post_init`.

This has an important implication regarding
:class:`~siotls.crypto.cipher_suites.TLSCipherSuite` and Early Data:
the transcript hash of
:class:`~siotls.contents.handshakes.client_hello.ClientHello` is used
when generating the "early exported master" and "client early traffic"
secrets. Those secrets are generated and used before receiving
:class:`~siotls.contents.handshakes.server_hello.ServerHello` /
:class:`~siotls.contents.handshakes.server_hello.HelloRetryRequest`. All
the pre-shared-keys all must share the same hashing algorithm othersise
it would be impossible to generate the secrets.

**About Hello Retry Request**

TLS 1.3 claims that it is possible to do a stateless
:class:`~siotls.contents.handshakes.server_hello.HelloRetryRequest`
using a clever (but not smart) hack. We still don't know how to do a
stateless
:class:`~siotls.contents.handshakes.server_hello.HelloRetryRequest` but
we still have to implement the hack otherwise the transcript wouldn't be
right.
"""

import hashlib
import typing

from siotls.contents import alerts
from siotls.iana import HandshakeType, HandshakeType_

if typing.TYPE_CHECKING:
    from collections.abc import Iterable

    import siotls.crypto

class HandshakeOrder(typing.NamedTuple):
    side: typing.Literal['client', 'server']
    handshake: HandshakeType | HandshakeType_
    is_skippable: bool = False

ORDER = [
    HandshakeOrder('client', HandshakeType.MESSAGE_HASH),
    HandshakeOrder('server', HandshakeType_.HELLO_RETRY_REQUEST),
    HandshakeOrder('client', HandshakeType.CLIENT_HELLO),
    HandshakeOrder('server', HandshakeType.SERVER_HELLO),
    HandshakeOrder('server', HandshakeType.ENCRYPTED_EXTENSIONS),
    HandshakeOrder('server', HandshakeType.CERTIFICATE_REQUEST, is_skippable=True),
    HandshakeOrder('server', HandshakeType.CERTIFICATE),
    HandshakeOrder('server', HandshakeType.CERTIFICATE_VERIFY),
    HandshakeOrder('server', HandshakeType.FINISHED),
    HandshakeOrder('client', HandshakeType.END_OF_EARLY_DATA, is_skippable=True),
    HandshakeOrder('client', HandshakeType.CERTIFICATE, is_skippable=True),
    HandshakeOrder('client', HandshakeType.CERTIFICATE_VERIFY, is_skippable=True),
    HandshakeOrder('client', HandshakeType.FINISHED),
]


class Transcript:
    """"""
    def __init__(self, digestmods: 'Iterable[siotls.crypto.HashFunction]'):
        """
        Prepare a new empty transcript for a new connection.

        :param digestmods: the list of hash function that are supported
            for this connection, usually SHA256, SHA384, or both.

        :raise ValueError: When ``digestmods`` is empty.
        """
        if not digestmods:
            e = "empty digestmods"
            raise ValueError(e)
        self._digestmod: None | siotls.crypto.HashInstance = None
        self._digestmods = [dm() for dm in digestmods]
        self._order_i = 2
        self._client_hello_transcripts: dict[str, bytes] = {}

    def post_init(self, digestmod: 'siotls.crypto.HashFunction') -> None:
        """
        Finilize the initialization with a definitive hash function.

        :param digestmod: The definite hash function.

        :raise ValueError: When ``digestmod`` is not one of the hash
            functions this transcript was initialized with.
        """
        name = digestmod().name
        self._digestmod = next((h for h in self._digestmods if h.name == name), None)
        if not self._digestmod:
            e = f"{digestmod} not found inside {self._digestmods}"
            raise ValueError(e)
        self._digestmods.clear()

    def do_hrr_dance(self):
        """
        Implemented as follow::

            Transcript-Hash(ClientHello1, HelloRetryRequest, ... Mn) =
                Hash(message_hash ||        /* Handshake type */
                     00 00 Hash.length  ||   /* Handshake message length (bytes) */
                     Hash(ClientHello1) ||  /* Hash of ClientHello1 */
                     HelloRetryRequest  || ... || Mn)
        """
        self._order_i = 0
        self._digestmod = hashlib.new(self._digestmod.name, b'')

        message_hash = b''.join((
            HandshakeType.MESSAGE_HASH.to_bytes(1, 'big'),
            b'\x00\x00',
            self._digestmod.digest_size.to_bytes(1, 'big'),
            self._client_hello_transcripts[self._digestmod.name],
        ))
        self.update(message_hash, 'client', HandshakeType.MESSAGE_HASH)

    def update(
        self,
        handshake_data: bytes,
        side: typing.Literal['client', 'server'],
        handshake_type: HandshakeType | HandshakeType_,
    ):
        """
        Update the underlying hash with new data.

        The side and handshake type are used as sanity check, and also
        to save the ClientHello's transcript digest for
        :meth:`do_hrr_dance`.

        :param handshake_data: The plain handshake, as extracted and
            decrypted from TLS record layer.
        :param side: The side of this connection.
        :param handshake_type: The type of the handshake.
        """
        # the transcript should only be updated during the initial handshake
        if self._order_i == len(ORDER):
            return

        # extra safety net, the states should validate the incomming
        # messages and by construction always send valid handshakes
        ho = ORDER[self._order_i]
        while ho.is_skippable and (side, handshake_type) != (ho.side, ho.handshake):
            self._order_i += 1
            ho = ORDER[self._order_i]
        if (side, handshake_type) != (ho.side, ho.handshake):
            e =(f"was expecting {(ho.side, ho.handshake)} "
                f"but found {(side, handshake_type)} instead")
            raise alerts.UnexpectedMessage(e)

        # update the transcript
        if self._digestmod:
            self._digestmod.update(handshake_data)
        for dm in self._digestmods:
            dm.update(handshake_data)

        # save the transcript after the first client hello, for the
        # hello retry request (hrr) dance
        if handshake_type == HandshakeType.CLIENT_HELLO:
            for dm in self._digestmods:
                self._client_hello_transcripts[dm.name] = dm.digest()
        elif handshake_type == HandshakeType.ENCRYPTED_EXTENSIONS:
            self._client_hello_transcripts.clear()

        self._order_i += 1

    def digest(self) -> bytes:
        """
        Digest the current transcript hash.

        :raise ValueError: When this method is called before
            :meth:`post_init` was called to finilize the initialization.
        """
        if self._digestmod is None:
            e = "must call post_init() prior of using this function"
            raise ValueError(e)
        return self._digestmod.digest()

    def hexdigest(self) -> str:
        """
        Digest and hexlify the current transcript hash.

        :raise ValueError: When this method is called before
            :meth:`post_init` was called to finilize the initialization.
        """
        if self._digestmod is None:
            e = "must call post_init() prior of using this function"
            raise ValueError(e)
        return self._digestmod.hexdigest()

    def copy(self):
        """ Create an independent copy of the current transcript hash. """
        dummy = bool
        copy = type(self)([dummy])
        if self._digestmods:
            copy._digestmods = [  # noqa: SLF001
                h.copy() for h in self._digestmods
            ]
            copy._digestmod = None  # noqa: SLF001
        else:
            copy._digestmods = []  # noqa: SLF001
            copy._digestmod = self._digestmod.copy()  # noqa: SLF001
        copy._order_i = self._order_i  # noqa: SLF001
        return copy
