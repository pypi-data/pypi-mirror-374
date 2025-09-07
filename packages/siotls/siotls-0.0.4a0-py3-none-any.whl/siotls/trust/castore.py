import itertools
import logging
import platform
import re
from os import PathLike
from pathlib import Path

from siotls.asn1types import DerCertificate
from siotls.pem import decode_pem_certificate, decode_pem_certificate_chain

try:
    import ssl
except ImportError:
    ssl = None  # type: ignore[assignment]


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# OPENSSL-REHASH(1SSL)
# The links created are of the form HHHHHHHH.D, where each H is a
# hexadecimal character and D is a single decimal digit.  Hashes for
# CRL's look similar except the letter r appears after the period, like
# this: HHHHHHHH.rD.
OPENSSL_REHASH_RE = re.compile(r'^[0-9a-fA-f]{8}\.[0-9]$')
OPENSSL_REHASH_CRL_RE = re.compile(r'^[0-9a-fA-f]{8}\.r[0-9]$')

LINUX_CA_CERTIFICATES_PATHS = {
    'alpine': '/etc/ssl/certs/ca-certificates.crt',
    'arch': '/etc/ca-certificates/extracted/tls-ca-bundle.pem',
    'debian': '/etc/ssl/certs/ca-certificates.crt',
    'fedora': '/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem',
    'suse': '/var/lib/ca-certificates/ca-bundle.pem',
    'ubuntu': '/etc/ssl/certs/ca-certificates.crt',
}


def _get_linux_cafile(fd_release: dict) -> tuple[str, PathLike | str | bytes | None]:
    fd_release.setdefault('ID_LIKE', '')
    for release in [fd_release['ID'], *fd_release['ID_LIKE'].split()]:
        path = LINUX_CA_CERTIFICATES_PATHS.get(release)
        if path and Path(path).is_file():
            return release, path
    return fd_release['ID'], None


def load_system_ca_certificates() -> list[DerCertificate]:
    """
    Load the chain of trust of the operating system.

    On Linux, it relies on the `ca-certificates`_ package (the package
    name differs depending on the distribution). It lookups the
    well-known place where the certificate bundle should be installed
    and load it if found. It uses :func:`platform.freedesktop_os_release`
    and fields ``ID`` and ``ID_LIKE`` to determine the distribution.

    On Windows, it uses :func:`ssl.enum_certificates` from the python
    standard library to load all three ``ROOT``, ``CA`` and ``MY``.

    If the operating system is unknown, or that loading a trust for
    for that operating system failed, it fallbacks on
    :func:`ssl.get_default_verify_paths` from the python standard
    library to find a trust store of last resort. An error is raised
    if that last resort fails too.

    :raises RuntimeError: When no chain of trust was found.

    .. _ca-certificates: https://packages.debian.org/stable/ca-certificates
    """
    match platform.system():
        case 'Linux':
            release, linux_cafile = _get_linux_cafile(platform.freedesktop_os_release())
            if linux_cafile:
                logger.info("detected system like %s, using %s", release, linux_cafile)
                with open(linux_cafile, 'rb') as file:
                    return decode_pem_certificate_chain(file.read())

        case 'Windows' if ssl:
            logger.info("using windows ROOT, CA and MY stores")
            return [
                der_data
                for der_data, asn_type, _oid in itertools.chain(
                    ssl.enum_certificates('ROOT'),  # type: ignore[attr-defined]
                    ssl.enum_certificates('CA'),  # type: ignore[attr-defined]
                    ssl.enum_certificates('MY'),  # type: ignore[attr-defined]
                )
                if asn_type == 'x509_asn'
            ]

    if ssl:
        defaults = ssl.get_default_verify_paths()
        if defaults.cafile:
            # OPENSSL-VERIFICATION-OPTIONS(1SSL)
            # -CAfile file
            #    Load the specified file which contains a certificate or
            #    several of them in case the input is in PEM or PKCS#12
            #    format.
            logger.info("using standard ssl cafile at %s", defaults.cafile)
            with open(defaults.cafile, 'rb') as file:
                return decode_pem_certificate_chain(file.read())
        if defaults.capath:
            # OPENSSL-VERIFICATION-OPTIONS(1SSL)
            # -CApath dir
            #     Use the specified directory as a collection of trusted
            #     certificates, i.e., a trust store.  Files should be
            #     named with the hash value of the X.509 SubjectName of
            #     each certificate. This is so that the library can
            #     extract the IssuerName, hash it, and directly lookup
            #     the file to get the issuer certificate.
            logger.info("using standard ssl capath at %s", defaults.capath)
            return [
                decode_pem_certificate(path.read_bytes())
                for path
                in Path(defaults.capath).iterdir()
                if OPENSSL_REHASH_RE.match(path.name)
            ]

    e = "could not load a trust store"
    raise RuntimeError(e)


def load_certifi_ca_certificates() -> list[DerCertificate]:
    """
    Load the same chain of trust as the Mozilla Firefox browser, via
    the `certifi`_ bundle of ca certificates.

    .. _certifi: https://pypi.org/project/certifi/
    """
    import certifi  # noqa: PLC0415
    with open(certifi.where(), 'rb') as file:
        return decode_pem_certificate_chain(file.read())














# Easter egg
#
# This file is named "castore.py" which is close to "Castor", french for
# beaver. So here is a cute beaver :D
#
#                    |    :|
#                    |     |
#                    |    .|
#                ____|    .|
#              .' .  ).   ,'
#            .' c   '7 ) (
#        _.-"       |.'   `.
#      .'           "8E   :|
#      |          _}""    :|
#      |         (   |     |
#     .'         )   |    :|
# .odCG8o_.---.__8E  |    .|
# `Y8MMP""       ""  `-...-'   cgmm
