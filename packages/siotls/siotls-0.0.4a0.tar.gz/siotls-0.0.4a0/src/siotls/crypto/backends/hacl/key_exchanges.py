import os

from pyhacl.diffie_hellman import curve25519  # type: ignore[import-untyped]

from siotls.crypto.key_exchanges import TLSKeyExchange, X25519Mixin

__all__ = (
    'X25519',
)


class X25519(X25519Mixin, TLSKeyExchange):
    @classmethod
    def init(cls):
        private_key = os.urandom(32)
        my_key_share = curve25519.secret_to_public(private_key)
        return private_key, my_key_share

    @classmethod
    def resume(cls, private_key, peer_key_share):
        shared_key = curve25519.ecdh(private_key, peer_key_share)
        return shared_key
