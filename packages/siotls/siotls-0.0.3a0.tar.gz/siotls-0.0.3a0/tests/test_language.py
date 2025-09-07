from siotls.language import (
    TLSIO,
    BufferOverflowError,
    MissingData,
    TLSBufferError,
    TooMuchDataError,
)

from . import TestCase


class TestTlsIO(TestCase):
    def test_tlsio_init_empty(self):
        stream = TLSIO()
        self.assertEqual(stream.getvalue(), b"")
        self.assertEqual(stream.tell(), 0)
        self.assertTrue(stream.is_eof())
        stream.ensure_eof()
        self.assertEqual(stream.read(), b"")
        stream.ensure_eof()

    def test_tlsio_init_full(self):
        stream = TLSIO(b"some data")
        self.assertEqual(stream.getvalue(), b"some data")
        self.assertEqual(stream.tell(), 0)
        self.assertFalse(stream.is_eof())
        self.assertRaises(TooMuchDataError, stream.ensure_eof)
        self.assertEqual(stream.read(), b"some data")
        stream.ensure_eof()

    def test_tlsio_read_exactly(self):
        stream = TLSIO(b"some data")
        self.assertEqual(stream.read_exactly(0), b"")
        self.assertEqual(stream.read_exactly(3), b"som")
        self.assertFalse(stream.is_eof())
        self.assertEqual(stream.read_exactly(3), b"e d")
        self.assertFalse(stream.is_eof())
        self.assertRaises(MissingData, stream.read_exactly, 4)
        self.assertFalse(stream.is_eof())
        self.assertEqual(stream.read_exactly(3), b"ata")
        self.assertTrue(stream.is_eof())

    def test_tlsio_read_int(self):
        self.assertEqual(TLSIO(b"\x00ab").read_int(1), 0)
        self.assertEqual(TLSIO(b"\x01\x00ab").read_int(2), 256)
        self.assertRaises(ValueError, TLSIO(b"\x00").read_int, 0)
        self.assertRaises(MissingData, TLSIO().read_int, 1)
        self.assertRaises(MissingData, TLSIO(b"\x00").read_int, 2)

    def test_tlsio_write_int(self):
        stream = TLSIO()
        stream.write_int(1, 0)
        self.assertEqual(stream.getvalue(), b"\x00")
        self.assertEqual(stream.tell(), 1)
        self.assertTrue(stream.is_eof())

        stream = TLSIO()
        stream.write_int(2, 0)
        self.assertEqual(stream.getvalue(), b"\x00\x00")
        self.assertEqual(stream.tell(), 2)
        self.assertTrue(stream.is_eof())

        stream = TLSIO()
        self.assertRaises(OverflowError, stream.write_int, 1, 256)
        self.assertEqual(stream.tell(), 0)
        self.assertTrue(stream.is_eof())

        stream = TLSIO()
        stream.write_int(2, 256)
        self.assertEqual(stream.getvalue(), b"\x01\x00")
        self.assertEqual(stream.tell(), 2)
        self.assertTrue(stream.is_eof())

    def test_tlsio_read_var(self):
        self.assertEqual(TLSIO(b"\x00").read_var(1), b"")
        self.assertRaises(MissingData, TLSIO(b"").read_var, 1)
        self.assertEqual(TLSIO(b"\x01\x00ab").read_var(1), b"\x00")
        self.assertRaises(MissingData, TLSIO(b"\x01").read_var, 1)

        stream = TLSIO(b"\x05123456")
        self.assertEqual(stream.read_var(1), b"12345")
        self.assertEqual(stream.tell(), 6)
        self.assertEqual(stream.read(), b"6")

    def test_tlsio_write_var(self):
        stream = TLSIO()
        stream.write_var(1, b"hello")
        self.assertEqual(stream.getvalue(), b"\x05hello")

        stream = TLSIO()
        self.assertRaises(OverflowError, stream.write_var, 0, b"hello")

        stream = TLSIO()
        stream.write_var(2, b"hello")
        self.assertEqual(stream.getvalue(), b"\x00\x05hello")

        stream = TLSIO()
        stream.write_var(2, b"hello")
        self.assertRaises(OverflowError, stream.write_var, 1, b" " * 256)

    def test_tlsio_read_listint(self):
        self.assertRaises(MissingData, TLSIO().read_listint, 1, 1)
        self.assertEqual(TLSIO(b"\x01\x00").read_listint(1, 1), [0])
        self.assertEqual(TLSIO(b"\x03\x00\x02\x01").read_listint(1, 1), [0, 2, 1])
        self.assertRaises(MissingData, TLSIO(b"\x03\x00\x02").read_listint, 1, 1)
        self.assertEqual(TLSIO(b"\x04\x00\x02\x01\x01").read_listint(1, 2), [2, 257])
        self.assertRaises(TLSBufferError, TLSIO(b"\x01\x00").read_listint, 1, 2)
        self.assertEqual(TLSIO(b"\x00\x04\x00\x02\x01\x01").read_listint(2, 1), [0, 2, 1, 1])
        self.assertEqual(TLSIO(b"\x00\x04\x00\x02\x01\x01").read_listint(2, 2), [2, 257])

    def test_tlsio_write_listint(self):
        stream = TLSIO()
        stream.write_listint(1, 1, [0, 2, 1])
        self.assertEqual(stream.getvalue(), b"\x03\x00\x02\x01")

        stream = TLSIO()
        stream.write_listint(2, 1, [0, 2, 1])
        self.assertEqual(stream.getvalue(), b"\x00\x03\x00\x02\x01")

        stream = TLSIO()
        self.assertRaises(OverflowError, stream.write_listint, 1, 1, [256])
        self.assertRaises(OverflowError, stream.write_listint, 1, 1, [0] * 256)

        stream = TLSIO()
        stream.write_listint(1, 2, [2, 257])
        self.assertEqual(stream.getvalue(), b"\x04\x00\x02\x01\x01")

        stream = TLSIO()
        stream.write_listint(2, 2, [2, 257])
        self.assertEqual(stream.getvalue(), b"\x00\x04\x00\x02\x01\x01")

    def test_tlsio_read_listvar(self):
        self.assertRaises(MissingData, TLSIO().read_listvar, 1, 1)
        self.assertEqual(TLSIO(b"\x01\x00").read_listvar(1, 1), [b""])
        self.assertEqual(TLSIO(b"\x05\x00\x01a\x01a").read_listvar(1, 1), [b"", b"a", b"a"])
        self.assertRaises(MissingData, TLSIO(b"\x03\x00\x02").read_listvar, 1, 1)
        self.assertRaises(MissingData, TLSIO(b"\x02\x00\x02").read_listvar, 1, 1)
        self.assertEqual(TLSIO(b"\x00\x04\x00\x02ab").read_listvar(2, 1), [b"", b"ab"])
        self.assertEqual(TLSIO(b"\x00\x04\x00\x02ab").read_listvar(2, 2), [b"ab"])

    def test_tlsio_write_listvar(self):
        stream = TLSIO()
        stream.write_listvar(1, 1, [b""])
        self.assertEqual(stream.getvalue(), b"\x01\x00")

        stream = TLSIO()
        stream.write_listvar(1, 1, [b"", b"ab", b"a"])
        self.assertEqual(stream.getvalue(), b"\x06\x00\x02ab\x01a")

        stream = TLSIO()
        self.assertRaises(OverflowError, stream.write_listvar, 1, 1, [b" " * 256])
        self.assertRaises(OverflowError, stream.write_listvar, 1, 1, [b" "] * 256)

        stream = TLSIO()
        stream.write_listvar(2, 1, [b"", b"ab"])
        self.assertEqual(stream.getvalue(), b"\x00\x04\x00\x02ab")

        stream = TLSIO()
        stream.write_listvar(2, 2, [b"", b"ab"])
        self.assertEqual(stream.getvalue(), b"\x00\x06\x00\x00\x00\x02ab")

    def test_tlsio_limit(self):
        stream = TLSIO(b"\x02\x01\x01\x01some data")
        with stream.limit(3):
            with stream.lookahead():
                self.assertEqual(stream.read(3), b"\x02\x01\x01")
                self.assertRaises(BufferOverflowError, stream.read, 1)
            with stream.lookahead():
                self.assertEqual(stream.read_exactly(3), b"\x02\x01\x01")
                self.assertRaises(BufferOverflowError, stream.read_exactly, 1)
            with stream.lookahead():
                self.assertEqual(stream.read_int(3), 2*256**2 + 1*256 + 1)
                self.assertRaises(BufferOverflowError, stream.read_int, 1)
            with stream.lookahead():
                self.assertEqual(stream.read_var(1), b"\x01\x01")
                self.assertRaises(BufferOverflowError, stream.read_var, 1)
            with stream.lookahead():
                self.assertEqual(stream.read_listint(1, 1), [1, 1])
                self.assertRaises(BufferOverflowError, stream.read_listint, 1, 1)
            with stream.lookahead():
                self.assertEqual(stream.read_listvar(1, 1), [b"\x01"])
                self.assertRaises(BufferOverflowError, stream.read_listvar, 1, 1)
            self.assertEqual(stream.read(), b"\x02\x01\x01")

        stream = TLSIO(b"some data")
        with stream.limit(4):
            e = "a more restrictive limit is present already"
            with self.assertRaises(ValueError, error_msg=e):  # noqa: SIM117
                with stream.limit(5):
                    pass
            stream.read(1)
            with self.assertRaises(ValueError, error_msg=e):  # noqa: SIM117
                with stream.limit(4):
                    pass

            with stream.limit(1):
                stream.read(1)

            e = "expected end of chunk but 1 bytes remain"
            with self.assertRaises(TooMuchDataError, error_msg=e):  # noqa: SIM117
                with stream.limit(2):
                    stream.read(1)
            stream.read()

    def test_tlsio_lookahead(self):
        stream = TLSIO(b"some data")
        self.assertEqual(stream.tell(), 0)
        with stream.lookahead():
            self.assertEqual(stream.read(3), b"som")
            self.assertEqual(stream.tell(), 3)
            with stream.lookahead():
                self.assertEqual(stream.read(3), b"e d")
                self.assertEqual(stream.tell(), 6)
            self.assertEqual(stream.tell(), 3)
            self.assertEqual(stream.read(3), b"e d")
        self.assertEqual(stream.tell(), 0)
        self.assertEqual(stream.read(3), b"som")
