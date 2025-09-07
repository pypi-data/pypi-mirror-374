import asn1crypto.pem  # type: ignore[import-untyped]

from .asn1types import (
    DerCertificate,
    DerPrivateKey,
    DerPublicKey,
    PemCertificate,
    PemCertificateChain,
    PemPrivateKey,
    PemPublicKey,
)


def decode_pem(pem_bytes, name=None, *, multiple=False):
    res = asn1crypto.pem.unarmor(pem_bytes, multiple=multiple)
    if not multiple:
        res = (res,)
    out = []
    for object_name, headers, der_bytes in res:
        if object_name != name:
            e = f"expected {name!r} but found {object_name!r} in PEM file"
            raise ValueError(e)
        if headers:
            e = f"found unexpected headers in PEM file: {headers}"
            raise ValueError(e)
        out.append(der_bytes)
    if not multiple:
        return out[0]
    return out


def decode_pem_certificate(pem_data: PemCertificate) -> DerCertificate:
    return decode_pem(pem_data, 'CERTIFICATE')


def decode_pem_certificate_chain(
    pem_data: PemCertificateChain
) -> list[DerCertificate]:
    return decode_pem(pem_data, 'CERTIFICATE', multiple=True)


def decode_pem_private_key(pem_data: PemPrivateKey) -> DerPrivateKey:
    return decode_pem(pem_data, 'PRIVATE KEY')


def decode_pem_public_key(pem_data: PemPublicKey) -> DerPublicKey:
    return decode_pem(pem_data, 'PUBLIC KEY')
