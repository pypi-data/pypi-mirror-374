from collections.abc import Collection

import asn1crypto.pem  # type: ignore[import-untyped]


def decode_pem(
    pem_bytes: bytes,
    name: str | None = None,
    *,
    multiple: bool = False,
) -> bytes | Collection[bytes]:
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


def decode_pem_certificate(pem_data):
    return decode_pem(pem_data, 'CERTIFICATE')


def decode_pem_certificates(pem_data):
    return decode_pem(pem_data, 'CERTIFICATE', multiple=True)


def decode_pem_private_key(pem_data):
    return decode_pem(pem_data, 'PRIVATE KEY')


def decode_pem_public_key(pem_data):
    return decode_pem(pem_data, 'PUBLIC KEY')
