import abc
import enum
import hashlib
import hmac
from typing import ClassVar, Literal

import siotls.crypto
from siotls import key_logger
from siotls.crypto.hkdf import hkdf_expand_label, hkdf_extract
from siotls.iana import CipherSuites
from siotls.utils import RegistryMeta, peekable

NONCE_MAX = 1 << 64
REKEY_THRESHOLD = 10 << 20  # 10MiB, arbitrary
SHA256_EMPTY = hashlib.sha256(b'').digest()
SHA256_ZEROS = b'\x00' * hashlib.sha256().digest_size
SHA384_EMPTY = hashlib.sha384(b'').digest()
SHA384_ZEROS = b'\x00' * hashlib.sha384().digest_size


class CipherState(enum.IntEnum):
    """ The state of the cipher. """

    INIT = 0
    """
    No encryption.

    Used during the initial
    :class:`~siotls.contents.handshakes.client_hello.ClientHello` and
    :class:`~siotls.contents.handshakes.server_hello.ServerHello`
    exchange.
    """

    EARLY = 1
    """
    Encryption using the early secret, a :abbr:`PSK (pre shared secret)`
    shared by both the client and server (obtained either externally or
    via a previous handshake).

    Allows the client to send encrypted data on the same flight as its
    (plain) :class:`~siotls.contents.handshakes.client_hello.ClientHello`.
    """

    HANDSHAKE = 2
    """
    Encryption using the handshake secret, a new secret that is unique
    to this connection and that was shared via
    :class:`~siotls.crypto.TLSKeyExchange` during the initial
    ClientHello/ServerHello exchange.

    Used by all other :mod:`~siotls.contents.handshakes`, except
    :class:`~siotls.contents.handshakes.key_update.KeyUpdate` and
    :class:`~siotls.contents.handshakes.new_session_ticket.NewSessionTicket`
    which are sent in the :attr:`APPLICATION` state.
    """

    APPLICATION = 3
    """
    Encryption using the main secret, a new secret unique to this
    connection that is derived from the handshake secret.

    Used for all messages, including handshakes, exchanged once the
    secure connection is established.
    """


class ICipher(metaclass=abc.ABCMeta):
    """ Interface that must be implemented by every concrete cipher suite. """

    @abc.abstractmethod
    def _ciphermod(self, key: bytes) -> None:
        """
        Instantiate a new cipher, with a new secret key.

        :param key: A secret key of :attr:`~TLSCipherSuite.key_length`
            bytes.
        """
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def _encrypt(self, nonce: bytes, data: bytes, associated_data: bytes) -> bytes:
        """
        Encrypt the data and compute a tag over the associated data.

        :param nonce: A unique value of
            :attr:`~TLSCipherSuite.nonce_length` bytes.
        :param data: The plain TLS content to encrypt.
        :param associated_data: The 5 bytes of the TLS record header.
        :return: The ciphertext of ``len(data)`` bytes and the tag of
            :attr:`~TLSCipherSuite.tag_length` bytes, concatenated.
        """
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def _decrypt(self, nonce: bytes, data: bytes, associated_data: bytes) -> bytes:
        """
        Decrypt the data and verify that the tag match the associated
        data.

        :param nonce: A unique value of
            :attr:`~TLSCipherSuite.nonce_length` bytes.
        :param data: The encrypted TLS content to decrypt.
        :param associated_data: The 5 bytes of the TLS record header.
        :return: The plaintext of ``len(data) - tag_length`` bytes.
        """
        raise NotImplementedError  # pragma: no cover


class _TLSSecrets:
    def __init__(self, digestmod, hashempty, hashzeros):
        self.state = CipherState.INIT
        self._digestmod = digestmod
        self._hashempty = hashempty
        self._hashzeros = hashzeros
        self._salt = self._hashzeros

    def _make_deriver(self, ikm, transcript_hash, *, update_salt):
        self.state = CipherState(self.state + 1)
        secret = hkdf_extract(self._digestmod, self._salt, ikm)
        if update_salt:
            self._salt = hkdf_expand_label(
                self._digestmod,
                secret,
                b'derived',
                self._hashempty,
                self._digestmod().digest_size,
            )
        return lambda label, *, transcript_hash=transcript_hash: (
            hkdf_expand_label(
                self._digestmod,
                secret,
                label,
                transcript_hash,
                self._digestmod().digest_size,
            )
        )

    def skip_early_secrets(self):
        assert self.state is CipherState.INIT  # noqa: S101
        psk = self._hashzeros
        self._make_deriver(psk, transcript_hash=None, update_salt=True)

    def derive_early_secrets(self, psk, psk_mode, client_hello_th):
        assert self.state is CipherState.INIT  # noqa: S101
        assert psk_mode in ('external', 'resume')  # noqa: S101
        psk_label = f'{psk_mode[:3]} binder'.encode()
        derive_early_secret = self._make_deriver(
            psk, client_hello_th, update_salt=True)

        binder_key = derive_early_secret(psk_label, transcript_hash=self._hashempty)
        early_exporter_master = derive_early_secret(b'e exp master')
        client_early_traffic = derive_early_secret(b'c e traffic')

        return (
            binder_key,
            early_exporter_master,
            client_early_traffic,
        )

    def derive_handshake_secrets(self, shared_key, server_hello_th):
        assert self.state is CipherState.EARLY  # noqa: S101
        derive_handshake_secret = self._make_deriver(
            shared_key, server_hello_th, update_salt=True)

        client_handshake_traffic = derive_handshake_secret(b'c hs traffic')
        server_handshake_traffic = derive_handshake_secret(b's hs traffic')
        return (
            client_handshake_traffic,
            server_handshake_traffic,
        )

    def derive_master_secrets(
        self, server_finished_th, client_finished_th
    ):
        assert self.state is CipherState.HANDSHAKE  # noqa: S101
        derive_master_secret = self._make_deriver(
            self._hashzeros, server_finished_th, update_salt=False)

        client_application_traffic = derive_master_secret(b'c ap traffic')
        server_application_traffic = derive_master_secret(b's ap traffic')
        exporter_master = derive_master_secret(b'exp master')
        resumption_master = derive_master_secret(
            b'res master', transcript_hash=client_finished_th)
        return (
            client_application_traffic,
            server_application_traffic,
            exporter_master,
            resumption_master,
        )


class TLSCipherSuite(ICipher, metaclass=RegistryMeta):
    """
    Abstract base class and registry for :class:`siotls.iana.CipherSuites`.
    """
    _registry_key = '_cipher_registry'
    _cipher_registry: ClassVar = {}

    @classmethod
    def install(cls, *, duplicate='raise'):  # pragma: no cover
        """
        Install this cipher suite in the registry.

        Called by :func:`siotls.crypto.install` which is the preferred
        way of installing cipher suites.
        """
        if other_cls := cls._cipher_registry.get(cls.iana_id):
            match duplicate:
                case 'skip':
                    return
                case 'override':
                    pass
                case 'raise':
                    exc = KeyError(cls.iana_id)
                    exc.add_note(f"cannot install {cls} as {other_cls} "
                                 f"is installed already")
                    raise exc
                case _:
                    e = f"not one of 'raise', 'skip', or 'override': {duplicate}"
                    raise ValueError(e)
        cls._cipher_registry[cls.iana_id] = cls

    iana_id: CipherSuites
    """ The unique numeric identifier of the cipher suite. """

    @property
    def state(self) -> CipherState:
        """ The current state of the cipher. """
        return self._secrets.state

    digestmod: 'siotls.crypto.HashFunction'
    """
    The hash algorithm associated to this cipher, from :mod:`hashlib`,
    e.g. ``hashlib.sha256``.
    """

    block_size: int
    """ The block size (in bytes) of the underlying AEAD algorithm. """

    key_length: int
    """ The secret key size (in bytes) of the underlying AEAD algorithm. """

    tag_length: int
    """
    The length (in bytes) of the authenticated tag produced in addition
    to the cipher text.
    """

    nonce_length: int
    """
    The length (in bytes) of the nonce, as required by the underlying
    AEAD algorithm.
    """

    hashempty: bytes
    """
    >>> digestmod(b"").digest()
    """

    hashzeros: bytes
    """
    >>> b"\0" * digestmod().digest_size
    """

    def __init__(
        self,
        side: Literal['client', 'server'],
        client_unique: bytes,
        *,
        log_keys: bool
    ):
        """
        :param side: This side of the connection.
        :param client_unique: The unique client identifier, coming from
            :attr:`~siotls.contents.handshakes.client_hello.ClientHello.random`.
            Ignored unless ``log_keys`` is ``True``.
        :param log_keys: Whether to log the TLS secrets on the
            ``siotls.keylog`` logger. For network analysing tools such
            as wireshark.
        """
        self._secrets = _TLSSecrets(self.digestmod, self.hashempty, self.hashzeros)
        self._side = side
        self._client_unique_hex = client_unique.hex() if log_keys else ''
        self._read_cipher = self._read_iv = self._read_seq = None
        self._write_cipher = self._write_iv = self._write_seq = None
        self._encrypted_blocks_count = 0

    # ------------------------------------------------------------------
    # AEAD Encryption and Decryption
    # ------------------------------------------------------------------

    @property
    def must_decrypt(self) -> bool:
        """ Whether it is necessary to decrypt the next received TLS record. """
        return bool(self._read_cipher)

    @property
    def must_encrypt(self) -> bool:
        """ Whether it is necessary to encryt the next TLS record. """
        return bool(self._write_cipher)

    @property
    def should_rekey(self) -> bool:
        """
        Whether it would be wise to exchange new keying materials with
        the peer.
        """
        raise NotImplementedError("abstract method")  # noqa: EM101

    def decrypt(self, data: bytes, associated_data: bytes) -> bytes:
        """
        Decrypt the cipher data and tag concatenated, verify the cipher
        and return the plaintext.

        :param nonce: :attr:`nonce_length` bytes, generated by TLS.
        :param data: The encrypted TLS content to decrypt.
        :param associated_data: The 5 bytes of the TLS record header.
        :return: The plaintext of ``len(data) - self.tag_length`` bytes.
        """
        return self._decrypt(self._next_read_nonce(), data, associated_data)

    def _next_read_nonce(self) -> bytes:
        assert self._read_seq is not None  # noqa: S101
        nonce = self._read_iv ^ next(self._read_seq)
        return nonce.to_bytes(self.nonce_length, 'big')

    def encrypt(self, data, associated_data):
        """
        Encrypt the plain data, return the ciphertext and tag
        concatenated.

        :param data: The plain TLS content to encrypt.
        :param associated_data: The 5 bytes of the TLS record header.
        :return: The ciphertext of ``len(data)`` size and tag of
            :attr:`tag_length` concatenated.
        """
        div, mod = divmod(len(data), self.block_size)
        self._encrypted_blocks_count += div + bool(mod)  # math.ceil
        return self._encrypt(self._next_write_nonce(), data, associated_data)

    def _next_write_nonce(self):
        assert self._write_seq is not None  # noqa: S101
        nonce = self._write_iv ^ next(self._write_seq)
        return nonce.to_bytes(self.nonce_length, 'big')

    # ------------------------------------------------------------------
    # Finished integrity
    # ------------------------------------------------------------------

    def sign_finish(self, transcript_hash: bytes) -> bytes:
        """
        Compute a HMAC over the the transcript digest, for the
        :attr:`~siotls.contents.handshakes.finished.Finished` handshake.
        """
        assert self.state is CipherState.HANDSHAKE  # noqa: S101
        key = (
            self._client_finished_key
            if self._side == 'client' else
            self._server_finished_key
        )
        return hmac.digest(key, transcript_hash, self.digestmod)

    def verify_finish(self, transcript_hash: bytes, other_verify_data: bytes) -> None:
        """
        Compute a HMAC over the transcript digest, and compare it
        against the :attr:`~siotls.contents.handshakes.finished.Finished`
        handshake sent by the peer.

        :raise ValueError: When the HMACs don't match.
        """
        assert self.state is CipherState.HANDSHAKE  # noqa: S101
        other_key = (
            self._server_finished_key
            if self._side == 'client' else
            self._client_finished_key
        )
        verify_data = hmac.digest(other_key, transcript_hash, self.digestmod)
        if not hmac.compare_digest(verify_data, other_verify_data):
            e = "invalid signature"
            raise ValueError(e)


    # ------------------------------------------------------------------
    # Key Derivation
    # ------------------------------------------------------------------

    @property
    def iv_length(self):
        # return max(8, self.nonce_length_min)
        return self.nonce_length

    def _derive_key_and_iv(self, secret):
        dm = self.digestmod
        return (
            hkdf_expand_label(dm, secret, b'key', b'', self.key_length),
            hkdf_expand_label(dm, secret, b'iv', b'', self.iv_length),
        )

    def skip_early_secrets(self):
        """
        Advance from state :attr:`CipherState.INIT` to a transitional
        state :attr:`CipherState.EARLY`.

        This state is transitional and serves no other purpose than
        preparing the underlying cipher to move to state
        :attr:`CipherState.HANDSHAKE`.

        A call to :meth:`derive_handshake_secrets` MUST follow
        immediately.
        """
        self._secrets.skip_early_secrets()

    def derive_early_secrets(self, psk, psk_mode, client_hello_th):
        """
        Advance from state :attr:`CipherState.INIT` to state
        state :attr:`CipherState.EARLY`.
        """
        binder_key, early_exporter_master, client_early_traffic = (
            self._secrets.derive_early_secrets(psk, psk_mode, client_hello_th))

        client_key, client_iv = (self._derive_key_and_iv(client_early_traffic))
        if self._side == 'client':
            self._write_cipher = self._ciphermod(client_key)
            self._write_iv = int.from_bytes(client_iv, 'big')
            self._write_seq = peekable(iter(range(NONCE_MAX)))
        else:
            self._read_cipher = self._ciphermod(client_key)
            self._read_iv = int.from_bytes(client_iv, 'big')
            self._read_seq = peekable(iter(range(NONCE_MAX)))

        if self._client_unique_hex:
            key_logger.info("CLIENT_EARLY_TRAFFIC_SECRET %s %s",
                self._client_unique_hex, client_early_traffic.hex())

        return binder_key, early_exporter_master

    def derive_handshake_secrets(self, shared_key, server_hello_th):
        """
        Advance from state :attr:`CipherState.EARLY` to state
        state :attr:`CipherState.HANDSHAKE`.
        """
        client_handshake_traffic, server_handshake_traffic = (
            self._secrets.derive_handshake_secrets(shared_key, server_hello_th))

        self._client_finished_key = hkdf_expand_label(
            self.digestmod,
            client_handshake_traffic,
            b"finished",
            b"",
            self.digestmod().digest_size,
        )
        self._server_finished_key =  hkdf_expand_label(
            self.digestmod,
            server_handshake_traffic,
            b"finished",
            b"",
            self.digestmod().digest_size
        )

        client_key, client_iv = self._derive_key_and_iv(client_handshake_traffic)
        server_key, server_iv = self._derive_key_and_iv(server_handshake_traffic)
        if self._side == 'client':
            self._write_cipher = self._ciphermod(client_key)
            self._write_iv = int.from_bytes(client_iv, 'big')
            self._write_seq = peekable(iter(range(NONCE_MAX)))
            self._read_cipher = self._ciphermod(server_key)
            self._read_iv = int.from_bytes(server_iv, 'big')
            self._read_seq = peekable(iter(range(NONCE_MAX)))
        else:
            self._write_cipher = self._ciphermod(server_key)
            self._write_iv = int.from_bytes(server_iv, 'big')
            self._write_seq = peekable(iter(range(NONCE_MAX)))
            self._read_cipher = self._ciphermod(client_key)
            self._read_iv = int.from_bytes(client_iv, 'big')
            self._read_seq = peekable(iter(range(NONCE_MAX)))
        self._encrypted_blocks_count = 0

        if self._client_unique_hex:
            key_logger.info("CLIENT_HANDSHAKE_TRAFFIC_SECRET %s %s",
                self._client_unique_hex, client_handshake_traffic.hex())
            key_logger.info("SERVER_HANDSHAKE_TRAFFIC_SECRET %s %s",
                self._client_unique_hex, server_handshake_traffic.hex())

    def derive_master_secrets(self, server_finished_th, client_finished_th):
        """
        Advance from state :attr:`CipherState.HANDSHAKE` to state
        state :attr:`CipherState.APPLICATION`.
        """
        (
            client_application_traffic,
            server_application_traffic,
            exporter_master,
            resumption_master
        ) = self._secrets.derive_master_secrets(server_finished_th, client_finished_th)

        client_key, client_iv = self._derive_key_and_iv(client_application_traffic)
        server_key, server_iv = self._derive_key_and_iv(server_application_traffic)
        if self._side == 'client':
            self._write_cipher = self._ciphermod(client_key)
            self._write_iv = int.from_bytes(client_iv, 'big')
            self._write_seq = peekable(iter(range(NONCE_MAX)))
            self._read_cipher = self._ciphermod(server_key)
            self._read_iv = int.from_bytes(server_iv, 'big')
            self._read_seq = peekable(iter(range(NONCE_MAX)))
        else:
            self._write_cipher = self._ciphermod(server_key)
            self._write_iv = int.from_bytes(server_iv, 'big')
            self._write_seq = peekable(iter(range(NONCE_MAX)))
            self._read_cipher = self._ciphermod(client_key)
            self._read_iv = int.from_bytes(client_iv, 'big')
            self._read_seq = peekable(iter(range(NONCE_MAX)))
        self._encrypted_blocks_count = 0

        # not necessary anymore
        self._client_finished_key = None
        self._server_finished_key = None

        if self._client_unique_hex:
            key_logger.info("CLIENT_TRAFFIC_SECRET_0 %s %s",
                self._client_unique_hex, client_application_traffic.hex())
            key_logger.info("SERVER_TRAFFIC_SECRET_0 %s %s",
                self._client_unique_hex, server_application_traffic.hex())
            key_logger.info("EXPORTER_SECRET %s %s",
                self._client_unique_hex, exporter_master.hex())

        return exporter_master, resumption_master


class Aes128GcmMixin:
    """
    Mixin for AES-GCM and a 128 bits keys.

    This mixin can be inherited by crypto backends to feed all the
    attributes required by :class:`TLSCipherSuite` that are specific to
    :attr:`~siotls.iana.CipherSuites.TLS_AES_128_GCM_SHA256`.

    Specifically, this mixin has values for:
    :attr:`~TLSCipherSuite.iana_id`,
    :attr:`~TLSCipherSuite.digestmod`,
    :attr:`~TLSCipherSuite.block_size`,
    :attr:`~TLSCipherSuite.key_length`,
    :attr:`~TLSCipherSuite.tag_length`,
    :attr:`~TLSCipherSuite.nonce_length`,
    :attr:`~TLSCipherSuite.hashempty`, and
    :attr:`~TLSCipherSuite.hashzeros`.
    """
    iana_id = CipherSuites.TLS_AES_128_GCM_SHA256
    digestmod = hashlib.sha256
    block_size = 16
    key_length = 16
    tag_length = 16
    nonce_length = 12
    hashempty = SHA256_EMPTY
    hashzeros = SHA256_ZEROS

    _usage_limit = 2 ** 36 - 1 - REKEY_THRESHOLD

    @property
    def should_rekey(self):
        q = self._write_seq.peek() if self._write_seq else 0
        return self._encrypted_blocks_count + q >= self._usage_limit

class Aes256GcmMixin:
    """
    Mixin for AES-GCM and a 256 bits keys.

    This mixin can be inherited by crypto backends to feed all the
    attributes required by :class:`TLSCipherSuite` that are specific to
    :attr:`~siotls.iana.CipherSuites.TLS_AES_256_GCM_SHA384`.

    Specifically, this mixin has values for:
    :attr:`~TLSCipherSuite.iana_id`,
    :attr:`~TLSCipherSuite.digestmod`,
    :attr:`~TLSCipherSuite.block_size`,
    :attr:`~TLSCipherSuite.key_length`,
    :attr:`~TLSCipherSuite.tag_length`,
    :attr:`~TLSCipherSuite.nonce_length`,
    :attr:`~TLSCipherSuite.hashempty`, and
    :attr:`~TLSCipherSuite.hashzeros`.
    """
    iana_id = CipherSuites.TLS_AES_256_GCM_SHA384
    digestmod = hashlib.sha384
    block_size = 16
    key_length = 32
    tag_length = 16
    nonce_length = 12
    hashempty = SHA384_EMPTY
    hashzeros = SHA384_ZEROS

    _usage_limit = Aes128GcmMixin._usage_limit  # noqa: SLF001
    should_rekey = Aes128GcmMixin.should_rekey

class ChaPolyMixin:
    """
    Mixin for Chacha-Poly1305.

    This mixin can be inherited by crypto backends to feed all the
    attributes required by :class:`TLSCipherSuite` that are specific to
    :attr:`~siotls.iana.CipherSuites.TLS_CHACHA20_POLY1305_SHA256`.

    Specifically, this mixin has values for:
    :attr:`~TLSCipherSuite.iana_id`,
    :attr:`~TLSCipherSuite.digestmod`,
    :attr:`~TLSCipherSuite.block_size`,
    :attr:`~TLSCipherSuite.key_length`,
    :attr:`~TLSCipherSuite.tag_length`,
    :attr:`~TLSCipherSuite.nonce_length`,
    :attr:`~TLSCipherSuite.hashempty`, and
    :attr:`~TLSCipherSuite.hashzeros`.
    """
    iana_id = CipherSuites.TLS_CHACHA20_POLY1305_SHA256
    digestmod = hashlib.sha256
    block_size = 16
    key_length = 32
    tag_length = 16
    nonce_length = 12
    hashempty = SHA256_EMPTY
    hashzeros = SHA256_ZEROS

    _usage_limit = NONCE_MAX - REKEY_THRESHOLD

    @property
    def should_rekey(self):
        return self._write_seq and self._write_seq.peek() >= self._usage_limit

class Aes128CcmMixin:
    """
    Mixin for AES-CCM and a 128 bits tag.

    This mixin can be inherited by crypto backends to feed all the
    attributes required by :class:`TLSCipherSuite` that are specific to
    :attr:`~siotls.iana.CipherSuites.TLS_AES_128_CCM_SHA256`.

    Specifically, this mixin has values for:
    :attr:`~TLSCipherSuite.iana_id`,
    :attr:`~TLSCipherSuite.digestmod`,
    :attr:`~TLSCipherSuite.block_size`,
    :attr:`~TLSCipherSuite.key_length`,
    :attr:`~TLSCipherSuite.tag_length`,
    :attr:`~TLSCipherSuite.nonce_length`,
    :attr:`~TLSCipherSuite.hashempty`, and
    :attr:`~TLSCipherSuite.hashzeros`.
    """
    iana_id = CipherSuites.TLS_AES_128_CCM_SHA256
    digestmod = hashlib.sha256
    block_size = 16
    key_length = 16
    tag_length = 16
    nonce_length = 12
    hashempty = SHA256_EMPTY
    hashzeros = SHA256_ZEROS

    _usage_limit = 2 ** 34.5 - REKEY_THRESHOLD

    @property
    def should_rekey(self):
        q = self._write_seq.peek() if self._write_seq else 0
        return self._encrypted_blocks_count + q // 2 > self._usage_limit

class Aes128Ccm8Mixin:
    """
    Mixin for AES-CCM and a 64 bits tag.

    This mixin can be inherited by crypto backends to feed all the
    attributes required by :class:`TLSCipherSuite` that are specific to
    :attr:`~siotls.iana.CipherSuites.TLS_AES_128_CCM_8_SHA256`.

    Specifically, this mixin has values for:
    :attr:`~TLSCipherSuite.iana_id`,
    :attr:`~TLSCipherSuite.digestmod`,
    :attr:`~TLSCipherSuite.block_size`,
    :attr:`~TLSCipherSuite.key_length`,
    :attr:`~TLSCipherSuite.tag_length`,
    :attr:`~TLSCipherSuite.nonce_length`,
    :attr:`~TLSCipherSuite.hashempty`, and
    :attr:`~TLSCipherSuite.hashzeros`.
    """
    iana_id = CipherSuites.TLS_AES_128_CCM_8_SHA256
    digestmod = hashlib.sha256
    block_size = 16
    key_length = 16
    tag_length = 8
    nonce_length = 12
    hashempty = SHA256_EMPTY
    hashzeros = SHA256_ZEROS

    _usage_limit = Aes128CcmMixin._usage_limit  # noqa: SLF001
    should_rekey = Aes128CcmMixin.should_rekey
