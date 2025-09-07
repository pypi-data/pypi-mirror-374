from cryptography.exceptions import InvalidSignature, UnsupportedAlgorithm
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, padding
from cryptography.hazmat.primitives.serialization import (
    load_der_private_key,
    load_der_public_key,
)

from siotls.crypto.signature_schemes import (
    EcdsaSecp256r1Sha256Mixin,
    EcdsaSecp384r1Sha384Mixin,
    EcdsaSecp521r1Sha512Mixin,
    Ed448Mixin,
    Ed25519Mixin,
    RsaPkcs1Sha256Mixin,
    RsaPkcs1Sha384Mixin,
    RsaPkcs1Sha512Mixin,
    RsaPssPssSha256Mixin,
    RsaPssPssSha384Mixin,
    RsaPssPssSha512Mixin,
    RsaPssRsaeSha256Mixin,
    RsaPssRsaeSha384Mixin,
    RsaPssRsaeSha512Mixin,
    SignatureKeyError,
    SignatureVerifyError,
    TLSSignatureScheme,
)

__all__ = (
    'EcdsaSecp256r1Sha256',
    'EcdsaSecp384r1Sha384',
    'EcdsaSecp521r1Sha512',
    'Ed448',
    'Ed25519',
    'RsaPkcs1Sha256',
    'RsaPkcs1Sha384',
    'RsaPkcs1Sha512',
    'RsaPssPssSha256',
    'RsaPssPssSha384',
    'RsaPssPssSha512',
    'RsaPssRsaeSha256',
    'RsaPssRsaeSha384',
    'RsaPssRsaeSha512',
)


class _InitMixin:
    def __init__(self, *, public_key=None, private_key=None):
        if public_key:
            try:
                self._public_key = load_der_public_key(public_key)
            except (ValueError, KeyError, UnsupportedAlgorithm) as exc:
                raise SignatureKeyError from exc
        if private_key:
            try:
                self._private_key = load_der_private_key(private_key, None)
            except (ValueError, KeyError, UnsupportedAlgorithm) as exc:
                raise SignatureKeyError from exc


class _RSAMixin(_InitMixin):
    digestmod: hashes.HashAlgorithm
    padding: padding.PKCS1v15 | padding.PSS

    def sign(self, message):
        return self._private_key.sign(message, self.padding, self.digestmod)

    def verify(self, signature, message):
        try:
            self._public_key.verify(signature, message, self.padding, self.digestmod)
        except InvalidSignature as exc:
            raise SignatureVerifyError from exc

class RsaPkcs1Sha256(RsaPkcs1Sha256Mixin, _RSAMixin, TLSSignatureScheme):
    digestmod = hashes.SHA256()
    padding = padding.PKCS1v15()

class RsaPkcs1Sha384(RsaPkcs1Sha384Mixin, _RSAMixin, TLSSignatureScheme):
    digestmod = hashes.SHA384()
    padding = padding.PKCS1v15()

class RsaPkcs1Sha512(RsaPkcs1Sha512Mixin, _RSAMixin, TLSSignatureScheme):
    digestmod = hashes.SHA512()
    padding = padding.PKCS1v15()

class RsaPssRsaeSha256(RsaPssRsaeSha256Mixin, _RSAMixin, TLSSignatureScheme):
    digestmod = hashes.SHA256()
    padding = padding.PSS(padding.MGF1(hashes.SHA256()), padding.PSS.DIGEST_LENGTH)

class RsaPssRsaeSha384(RsaPssRsaeSha384Mixin, _RSAMixin, TLSSignatureScheme):
    digestmod = hashes.SHA384()
    padding = padding.PSS(padding.MGF1(hashes.SHA384()), padding.PSS.DIGEST_LENGTH)

class RsaPssRsaeSha512(RsaPssRsaeSha512Mixin, _RSAMixin, TLSSignatureScheme):
    digestmod = hashes.SHA512()
    padding = padding.PSS(padding.MGF1(hashes.SHA512()), padding.PSS.DIGEST_LENGTH)

class RsaPssPssSha256(RsaPssPssSha256Mixin, _RSAMixin, TLSSignatureScheme):
    digestmod = hashes.SHA256()
    padding = padding.PSS(padding.MGF1(hashes.SHA256()), padding.PSS.DIGEST_LENGTH)

class RsaPssPssSha384(RsaPssPssSha384Mixin, _RSAMixin, TLSSignatureScheme):
    digestmod = hashes.SHA384()
    padding = padding.PSS(padding.MGF1(hashes.SHA384()), padding.PSS.DIGEST_LENGTH)

class RsaPssPssSha512(RsaPssPssSha512Mixin, _RSAMixin, TLSSignatureScheme):
    digestmod = hashes.SHA512()
    padding = padding.PSS(padding.MGF1(hashes.SHA512()), padding.PSS.DIGEST_LENGTH)


class _ECDSAMixin(_InitMixin):
    digestmod: hashes.HashAlgorithm

    def sign(self, message):
        return self._private_key.sign(message, ec.ECDSA(self.digestmod))

    def verify(self, signature, message):
        try:
            self._public_key.verify(signature, message, ec.ECDSA(self.digestmod))
        except InvalidSignature as exc:
            raise SignatureVerifyError from exc

class EcdsaSecp256r1Sha256(EcdsaSecp256r1Sha256Mixin, _ECDSAMixin, TLSSignatureScheme):
    digestmod = hashes.SHA256()

class EcdsaSecp384r1Sha384(EcdsaSecp384r1Sha384Mixin, _ECDSAMixin, TLSSignatureScheme):
    digestmod = hashes.SHA384()

class EcdsaSecp521r1Sha512(EcdsaSecp521r1Sha512Mixin, _ECDSAMixin, TLSSignatureScheme):
    digestmod = hashes.SHA512()


class _EDMixin(_InitMixin):
    def sign(self, message):
        return self._private_key.sign(message)

    def verify(self, signature, message):
        try:
            self._public_key.verify(signature, message)
        except InvalidSignature as exc:
            raise SignatureVerifyError from exc

class Ed25519(Ed25519Mixin, _EDMixin, TLSSignatureScheme):
    pass

class Ed448(Ed448Mixin, _EDMixin, TLSSignatureScheme):
    pass
