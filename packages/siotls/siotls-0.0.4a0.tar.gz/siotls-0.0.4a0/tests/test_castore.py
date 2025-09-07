import platform
import ssl
import unittest
from unittest.mock import patch

import asn1crypto.x509

from siotls.trust import castore

from . import TestCase

try:
    import certifi
except ImportError:
    certifi = None


is_debian_like = (
    platform.system() == 'Linux'
    and platform.freedesktop_os_release()['ID'] in (
        'debian', 'ubuntu', 'linuxmint',
    )
)


class TestCAStore(TestCase):
    def assertIsCAStore(self, store):  # noqa: N802
        self.assertGreater(len(store), 20)
        asn1crypto.x509.Certificate.load(store[0])

    @unittest.skipUnless(certifi, "certifi not installed")
    def test_castore_certifi(self):
        self.assertIsCAStore(castore.load_certifi_ca_certificates())

    @unittest.skipUnless(is_debian_like, "need debian-like")
    def test_castore_debian_ca_certificates(self):
        m =(r"^detected system like (debian|ubuntu), "
            r"using /etc/ssl/certs/ca-certificates\.crt$")
        with (
            patch.object(castore, 'ssl', None),
            self.assertLogs('siotls.trust', 'INFO', log_pattern=m),
        ):
            self.assertIsCAStore(castore.load_system_ca_certificates())

    @unittest.skipUnless(ssl, "need stdlib ssl")
    def test_castore_stdlib_ssl(self):
        m = r"^using standard ssl ca(file|path) at"
        with (
            patch.object(platform, 'system', lambda: "i don't exist"),
            self.assertLogs('siotls.trust', 'INFO', log_pattern=m),
        ):
            self.assertIsCAStore(castore.load_system_ca_certificates())

    @unittest.skipUnless(
        platform.system() == 'Windows' and ssl,
        "need windows with stdlib ssl")
    def test_castore_windows_stdlib_ssl(self):
        m = "using windows ROOT, CA and MY stores"
        with self.assertLogs('siotls.trust', 'INFO', log_msg=m):
            self.assertIsCAStore(castore.load_system_ca_certificates())

    def test_castore_unknown_system(self):
        e = "could not load a trust store"
        with (
            patch.object(platform, 'system', lambda: "i don't exist"),
            patch.object(castore, 'ssl', None),
            self.assertRaises(RuntimeError, error_msg=e),
        ):
            castore.load_system_ca_certificates()
