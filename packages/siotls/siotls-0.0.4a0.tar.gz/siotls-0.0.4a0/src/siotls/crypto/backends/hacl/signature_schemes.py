import os

from asn1crypto.keys import (  # type: ignore[import-untyped]
    PrivateKeyInfo,
    PublicKeyInfo,
)
from pyhacl import HACLError  # type: ignore[import-untyped]
from pyhacl.signature import ed25519, p256  # type: ignore[import-untyped]

from siotls.crypto.signature_schemes import (
    EcdsaSecp256r1Sha256Mixin,
    Ed25519Mixin,
    SignatureKeyError,
    SignatureSignError,
    SignatureVerifyError,
    TLSSignatureScheme,
)

__all__ = (
    'EcdsaSecp256r1Sha256',
    'Ed25519',
)


def _der_encode_dss_sig_value(r: bytes, s: bytes) -> bytes:
    # 2-complement, ensure left-most bit is 0
    if s[0] & 0b10000000:
        s = b'\x00' + s
    if r[0] & 0b10000000:
        r = b'\x00' + r
    # Dss-Sig-Value  ::=  SEQUENCE  {
    #     r       INTEGER,
    #     s       INTEGER  }
    return b''.join((
        b'\x30', (len(r) + len(s) + 4).to_bytes(1, 'big'),
            b'\x02', len(r).to_bytes(1, 'big'), r,
            b'\x02', len(s).to_bytes(1, 'big'), s,
    ))


def _der_decode_dss_sig_value(signature: bytes) -> tuple[bytes, bytes]:
    if len(signature) < 70:  # minimum possible Dss_Sig_Value  # noqa: PLR2004
        raise ValueError
    if signature[0] != 48:  # sequence  # noqa: PLR2004
        raise ValueError(signature[0])
    seq_len = signature[1]
    if seq_len & 0b10000000:
        e = "don't support long length yet"
        raise ValueError(e)
    if seq_len != len(signature) - 2:
        raise ValueError(seq_len)
    if signature[2] != 2:  # integer  # noqa: PLR2004
        raise ValueError(signature[2])
    r_len = signature[3]
    if r_len > seq_len - 5:
        raise ValueError((r_len, seq_len))
    r = signature[4:4+r_len]
    s_len = signature[4 + r_len + 1]
    if s_len > seq_len - 5:
        raise ValueError((r_len, s_len, seq_len))
    if r_len + s_len + 4 != seq_len:
        raise ValueError((r_len, s_len, seq_len))
    s = signature[-s_len:]
    return _normalize_integer(r, 32), _normalize_integer(s, 32)


def _normalize_integer(integer: bytes, length: int):
    if len(integer) > length:
        if any(digit != 0 for digit in integer[:-length]):
            raise ValueError(integer)
        return integer[-length:]
    if len(integer) < length:
        return b'\x00' * (length - len(integer)) + integer
    return integer


class EcdsaSecp256r1Sha256(EcdsaSecp256r1Sha256Mixin, TLSSignatureScheme):
    def __init__(self, *, public_key=None, private_key=None):
        if public_key:
            public_key = bytes(PublicKeyInfo.load(public_key)['public_key'])
            if len(public_key) == 64 + 1 and public_key[:1] == b'\x04':
                public_key = public_key[1:]
            if not p256.validate_public_key(public_key):
                e = "invalid public key"
                raise SignatureKeyError(e)
            self.public_key = public_key
        if private_key:
            private_key = bytes(PrivateKeyInfo.load(public_key)['private_key'])
            if not p256.validate_private_key(private_key):
                e = "invalid private key"
                raise SignatureKeyError(e)
            self.private_key = private_key

    def sign(self, message):
        try:
            raw_signature = p256.sign_sha256(
                message,
                self.private_key,
                nonce=os.urandom(32)
            )
        except HACLError as exc:
            raise SignatureSignError from exc
        r = raw_signature[:32]
        s = raw_signature[32:]
        return _der_encode_dss_sig_value(r, s)

    def verify(self, signature, message):
        r, s = _der_decode_dss_sig_value(signature)
        ok = p256.verif_sha256(message, self.public_key, r + s)
        if not ok:
            raise SignatureVerifyError


class Ed25519(Ed25519Mixin, TLSSignatureScheme):
    def __init__(self, *, public_key=None, private_key=None):
        if public_key:
            if len(public_key) != 32:  # noqa: PLR2004
                e = "invalid private key"
                raise SignatureKeyError(e)
            self.public_key = public_key
        if private_key:
            if len(private_key) != 32:  # noqa: PLR2004
                e = "invalid private key"
                raise SignatureKeyError(e)
            self.private_key = private_key

    def sign(self, message):
        return ed25519.sign(self.private_key, message)

    def verify(self, signature, message):
        ok = ed25519.verify(self.public_key, message, signature)
        if not ok:
            raise SignatureVerifyError
