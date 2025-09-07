""" Prensentation language as defined in :rfc:`8446#section-3`. """

import abc
import contextlib
import io
import logging
from collections.abc import MutableSequence, Sequence
from os import SEEK_CUR

from siotls import TLSError

logger = logging.getLogger(__name__)


class MissingData(TLSError):  # noqa: N818
    """
    Occurs when reading more data than there are available in the
    buffer. The error is likely to go away once more data are fed into
    the buffer.

    >>> stream = TLSIO(b"abc")
    >>> stream.read_exactly(4)
    Traceback (most recent call last):
    ...
    MissingData: expected 4 bytes but can only read 3
    """


class TLSBufferError(TLSError, BufferError):
    """
    Top error class, occurs when an error occured while parsing or
    serializing data from/into the buffer.

    Closely related to :class:`~siotls.contents.alerts.DecodeError`.
    """


class BufferOverflowError(TLSBufferError):
    """
    Occurs when a :meth:`TLSIO.limit` is active and that an operation
    that would had read/write over the limit was prevented.
    """


class TooMuchDataError(TLSBufferError):
    """
    Occurs when there are remaining unread data but that all the data
    should had been read.

    >>> stream = TLSIO(b"abc")
    >>> stream.ensure_eof()
    Traceback (most recent call last):
    ...
    TooMuchDataError: expected end of stream but 3 bytes remain
    """


class Serializable(metaclass=abc.ABCMeta):
    _struct: str

    @abc.abstractclassmethod  # type: ignore[arg-type]
    def parse(cls, stream, **kwargs):  # pragma: no cover
        pass

    @abc.abstractmethod
    def serialize(self):  # pragma: no cover
        pass


class SerializableBody(metaclass=abc.ABCMeta):
    _struct: str

    @abc.abstractclassmethod  # type: ignore[arg-type]
    def parse_body(cls, stream, **kwargs):  # pragma: no cover
        pass

    @abc.abstractmethod
    def serialize_body(self):  # pragma: no cover
        pass


class TLSIO(io.BytesIO):
    """ BytesIO used to serialize and parse :mod:`siotls.contents`. """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._limits = [float('+inf')]

    def read(self, n: int | None = None) -> bytes:
        """
        Read at most ``n`` bytes, or all bytes until the
        limit/end-of-stream if ``n`` is negative.

        :param n: amount of bytes to read, or ``-1`` to read all
            remaining bytes.

        :raise BufferOverflowError: When trying to read more bytes than
            the current limit allows.
        """
        max_n = self._limits[-1] - self.tell()
        if n is None or n < 0:
            if len(self._limits) > 1:
                n = max_n
        elif n > max_n:
            e = f"expected {n} bytes but can only read {max_n}"
            raise BufferOverflowError(e)
        return super().read(n)

    def read_exactly(self, n: int) -> bytes:
        """
        Read a fixed-length vector of ``n`` bytes.

        :param n: amount of bytes to read, no more, no less.

        :raise ValueError: When ``n`` is negative.
        :raise MissingData: When trying to read more bytes than there
            are available on the buffer.
        :raise BufferOverflowError: When trying to read more bytes than
            the current limit allows.
        """
        if n < 0:
            e = f"cannot read a negative amount of bytes: {n}"
            raise ValueError(e)
        data = b''
        while len(data) != n:
            read = self.read(n - len(data))
            if not read:
                self.seek(-len(data), SEEK_CUR)
                e = f"expected {n} bytes but could only read {len(data)}"
                raise MissingData(e)
            data += read
        return data

    def read_int(self, n: int) -> int:
        """
        Read a big-endian unsigned integer defined over ``n`` bytes.

        :param n: amount of bytes to read.

        :raise ValueError: When n is not a strictly positive integer.
        :raise MissingData: When trying to read more bytes than there
            are available on the buffer.
        :raise BufferOverflowError: When trying to read more bytes than
            the current limit allows.
        """
        if n <= 0:
            e = f"must be a strictly positive integer: {n}"
            raise ValueError(e)
        return int.from_bytes(self.read_exactly(n), 'big')

    def write_int(self, n: int, i: int) -> None:
        """ Write a big-endian unsigned integer ``i`` over ``n`` bytes. """
        self.write(i.to_bytes(n, 'big'))

    def read_var(self, n: int) -> bytes:
        """
        Read a variable-length vector. The vector is prefixed by its
        actual length as a big-endian unsigned integer over ``n`` bytes.

        :param n: amount of bytes reserved for the length of the vector.

        :raise ValueError: When n is not a strictly positive integer.
        :raise MissingData: When trying to read more bytes than there
            are available on the buffer.
        :raise BufferOverflowError: When trying to read more bytes than
            the current limit allows.
        """
        length = self.read_int(n)
        return self.read_exactly(length)

    def write_var(self, n: int, b: bytes) -> None:
        """
        Write a variable-length vector ``b``. The actual length of the
        vector is written first as a big-endian unsigned integer over
        ``n`` bytes, the vector itself is only then written.
        """
        self.write_int(n, len(b))
        self.write(b)

    def read_listint(self, nlist: int, nitem: int) -> MutableSequence[int]:
        """
        Read a variable-length vector where each item is an integer. The
        vector is prefixed by its actual length as a big-endian unsigned
        integer over ``nlist`` bytes. All integers are big-endian
        unsigned integers of ``nitem`` bytes.

        :param nlist: amount of bytes reserved for the length of the
            vector, as the total number of bytes, **not** as the number
            of items.
        :param nitem: amount of bytes of every integer.

        :raise TLSBufferError: when the actual length of the vector
            (read from the first ``nlist`` bytes) is not a multiple of
            ``nitem``.
        :raise MissingData: When trying to read more bytes than there
            are available on the buffer.
        :raise BufferOverflowError: When trying to read more bytes than
            the current limit allows.
        """
        length = self.read_int(nlist)
        if length % nitem != 0:
            e =(f"cannot read {length // nitem + 1} uint{nitem * 8}_t out of "
                f"{length} bytes")
            raise TLSBufferError(e)

        it = iter(self.read_exactly(length))
        return [
            int.from_bytes(bytes(group), 'big')
            for group in zip(*([it] * nitem), strict=True)
        ]

    def write_listint(self, nlist: int, nitem: int, items: Sequence[int]) -> None:
        """ Write ``items`` as a variable-length vector of integers. """
        self.write_int(nlist, len(items) * nitem)
        for item in items:
            self.write_int(nitem, item)

    def read_listvar(self, nlist, nitem) -> MutableSequence[bytes]:
        """
        Read a variable-length vector where each item is itself a
        variable-length vector.

        :param nlist: amount of bytes reserved for the length of the
            vector, as the total number of bytes, **not** as the number
            of items.
        :param nitem: amount of bytes reserved for the length of every
            variable-length vector item.

        :raise MissingData: When trying to read more bytes than there
            are available on the buffer.
        :raise BufferOverflowError: When trying to read more bytes than
            the current limit allows.
        """
        items = []
        list_stream = type(self)(self.read_var(nlist))
        while not list_stream.is_eof():
            items.append(list_stream.read_var(nitem))
        return items

    def write_listvar(self, nlist: int, nitem: int, items: Sequence[bytes]):
        prepos = self.tell()
        self.write_int(nlist, 0)  # placeholder
        for item in items:
            self.write_var(nitem, item)
        postpos = self.tell()
        # write the effective size on the placeholder
        self.seek(prepos, 0)
        self.write_int(nlist, postpos - prepos - nlist)
        self.seek(postpos, 0)


    @contextlib.contextmanager
    def lookahead(self):
        pos = self.tell()
        try:
            yield
        finally:
            self.seek(pos)

    def is_eof(self) -> bool:
        """
        Return whether we are at the end of the stream or not.

        This does NOT account for any :meth:`limit` set.
        """
        current_pos = self.tell()
        eof_pos = self.seek(0, 2)
        self.seek(current_pos, 0)
        return current_pos == eof_pos

    def ensure_eof(self):
        """
        Ensure we are at the end of the stream.

        This does NOT account for any :meth:`limit` set.

        :raise TooMuchDataError: when we are not at the end of the
            stream.
        """
        current_pos = self.tell()
        eof_pos = self.seek(0, 2)
        if remaining := eof_pos - current_pos:
            self.seek(current_pos, 0)
            e = f"expected end of stream but {remaining} bytes remain"
            raise TooMuchDataError(e)

    @contextlib.contextmanager
    def limit(self, length):
        """
        Enters a context-manager that enforces reading the next
        ``length`` bytes, no more, no less.

        This method can be used for parsing advanced data structures
        when the size of that structure is known but that the structure
        cannot be parsed by other (simpler) methods such as
        :meth:`read_listint` and :meth:`read_listvar`.

        It enforces a limit that is understood by all the ``read``
        methods, they will all raise :class:`BufferOverflowError` would
        reading more bytes be attempted.

        :param length: the exact number of bytes to read before exiting
            the context manager.

        :raise ValueError: upon entering the context manager, if another
            more restrictive limit is present already.
        :raise TooMuchDataError: upon exiting the context manager, if
            there are unread bytes remaining.
        """
        new_limit = self.tell() + length
        if new_limit > self._limits[-1]:
            e = "a more restrictive limit is present already"
            raise ValueError(e)

        self._limits.append(new_limit)

        yield new_limit

        if self._limits.pop() != new_limit:  # pragma: no cover
            e = "another limit was pop"
            raise AssertionError(e)
        if not self._limits:  # pragma: no cover
            e = "+inf was pop"
            raise AssertionError(e)
        if (remaining := new_limit - self.tell()):
            e = f"expected end of chunk but {remaining} bytes remain"
            raise TooMuchDataError(e)
