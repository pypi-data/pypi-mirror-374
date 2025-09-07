""" :rfc:`5869` - HMAC-based Extract-and-Expand Key Derivation Function """

import hmac
import math
import typing

if typing.TYPE_CHECKING:
    import siotls.crypto


def hkdf_extract(
    digestmod: 'siotls.crypto.HashFunction',
    salt: bytes | None,
    input_keying_material: bytes,
) -> bytes:
    """
    Take a random key that is not necessarly distributed uniformly and
    turn it in a short but cryptographically strong key.

    :param digestmod: The hash function for the underlying HMAC.
    :param salt: Some bytes that need to be nor secret, nor unique. Used
        to strengthen the output key.
    :param input_keying_material: The weak input key such as a secret
        shared via a key exchange algorithm (diffie-hellman) or a random
        value coming from a :abbr:`TRNG (True Random Number Generator)`
        (:manpage:`getrandom(2)`).
    :return: A strong pseudo random key, of ``digestmod().digest_size``
        bytes.
    """
    if salt is None:
        salt = b'\x00' * digestmod().digest_size
    pseudorandom_key = hmac.digest(salt, input_keying_material, digestmod)
    return pseudorandom_key

def hkdf_expand(
    digestmod: 'siotls.crypto.HashFunction',
    pseudorandom_key: bytes,
    info: bytes,
    okm_length: int,
) -> bytes:
    """
    Take a strong key and expand it to the desired length. It is
    possible to supply additional info (e.g. a label) to expand a same
    input key into multiple ones (one per different info).

    :param digestmod: The hash function for the underlying HMAC.
    :param pseudorandom_key: A strong key, usually coming from
        :func:`hkdf_extract`.
    :param info: Additional info that need to be nor random, nor secret
        nor unique. It can very well be a human readable label. Used to
        expand a same input key into multiple different ones.
    :param okm_length: The length (in bytes) of the output key.
    :return: Another strong key, of ``okm_length`` bytes.
    """
    if okm_length == digestmod().digest_size:
        return hmac.digest(pseudorandom_key, info + b'\x01', digestmod)

    n = math.ceil(okm_length / digestmod().digest_size)

    t = [b'']
    for i in range(1, n + 1):
        msg = b''.join((t[i - 1], info, i.to_bytes(1, 'big')))
        t.append(hmac.digest(pseudorandom_key, msg, digestmod))

    output_keying_material = b''.join(t)[:okm_length]
    return output_keying_material

def hkdf_expand_label(
    digestmod: 'siotls.crypto.HashFunction',
    secret: bytes,
    label: bytes,
    context: bytes,
    length: int,
) -> bytes:
    """
    Expand multiple TLS secrets from a same strong pseudo random key.

    This function is the TLS take on :func:`hkdf_expand` and is defined
    at :rfc:`8446#section-7.1`.

    :param digestmod: The hash function for the underlying HMAC.
    :param secret: A strong secret, from wich other strong keys will be
        expanded.
    :param label: Free text, usually human readable, used to name the
        output key. Used together with ``context`` as salt.
    :param context: Some additional bytes to use as salt. Usually the
        current TLS transcript digest.
    :param length: The length of the output.
    :return: Another strong key, of ``length`` bytes.
    """
    label = b'tls13 ' + label
    hkdf_label = b''.join([
        length.to_bytes(2, 'big'),
        len(label).to_bytes(1, 'big'),
        label,
        len(context).to_bytes(1, 'big'),
        context,
    ])
    return hkdf_expand(digestmod, secret, hkdf_label, length)
