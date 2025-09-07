from pyhacl import HACLError  # type: ignore[import-untyped]
from pyhacl.aead import chacha_poly1305  # type: ignore[import-untyped]

from siotls.contents import alerts
from siotls.crypto.cipher_suites import ChaPolyMixin, TLSCipherSuite

__all__ = (
    'ChaPoly',
)


class ChaPoly(ChaPolyMixin, TLSCipherSuite):
    @classmethod
    def _ciphermod(cls, key):
        return key

    def _encrypt(self, nonce, data, associated_data):
        cipher, tag = chacha_poly1305.encrypt(
            data,
            associated_data,
            self._write_cipher,
            nonce,
        )
        return cipher + tag

    def _decrypt(self, nonce, data, associated_data):
        cipher = bytes(data[:-16])
        tag = bytes(data[-16:])
        try:
            return chacha_poly1305.decrypt(
                cipher,
                bytes(associated_data),
                self._read_cipher,
                nonce,
                tag,
            )
        except HACLError as exc:
            raise alerts.DecryptError from exc
