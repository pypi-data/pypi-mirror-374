import argparse
import atexit
import contextlib
import dataclasses
import errno
import io
import logging
import re
import selectors
import shutil
import socket
import subprocess
import tempfile
import unittest
from os import fspath, getenv
from pathlib import Path

import siotls.crypto
from siotls.__main__ import setup_logging
from siotls.contents import Content
from siotls.language import TLSIO

parser = argparse.ArgumentParser()
parser.add_argument('-v', dest='verbosity', action='count', default=0)
options, _ = parser.parse_known_args()

logging.basicConfig()
setup_logging(logging.ERROR - 10 * options.verbosity)
logging.getLogger('').handlers[0].addFilter(
    lambda record: record.msg not in (
        'not implemented section skipped',
    )
)

test_temp_dir = Path(tempfile.mkdtemp(prefix='siotls-test-'))
atexit.register(shutil.rmtree, fspath(test_temp_dir), ignore_errors=True)

CRYPTO_BACKEND = getenv('SIOTLS_CRYPTO_BACKEND', 'openssl')
siotls.crypto.install(CRYPTO_BACKEND)

TAG_EXTERNAL = getenv('SIOTLS_EXTERNAL') == '1'
TAG_INTEGRATION = getenv('SIOTLS_INTEGRATION') == '1'
TAG_SLOW = getenv('SIOTLS_SLOW') == '1'


def counter(format='{n}', n=0):  # noqa: A002
    """ Helper for ``parameterized.expand``. """
    def counter_(testcase_func, param_num, param):  # noqa: ARG001
        return testcase_func.__name__ + '_' + format.format(n=int(param_num) + n)
    return counter_


class TestCase(unittest.TestCase):
    def assertRaises(  # noqa: N802
        self,
        exception,
        *args,
        error_msg=None,
        error_pattern=None,
        **kwds
    ):
        """
        Context manager that assert that the block raises an exception.

        :param str error_msg: assert that the exception's ``args[0]`` is
            equal to this string
        :param str error_pattern: assert that the exception's
            ``args[0]`` matches this regexp pattern
        """
        if error_msg is None:
            return super().assertRaises(exception, *args, **kwds)
        if error_msg:
            error_pattern = re.escape(error_msg)
        return self.assertRaisesRegex(exception, error_pattern, *args, **kwds)

    @contextlib.contextmanager
    def assertLogs(  # noqa: N802
        self,
        logger='',
        level=logging.NOTSET,
        *args,
        log_msg=None,
        log_pattern=None,
        **kwds
    ):
        """
        Context manager that assert that the block logs a message.

        :param str log_msg: assert that at least one of the log lines is
            equal to this string
        :param str log_pattern: assert that at least one of the log
            lines matches this regexp pattern
        """
        with super().assertLogs(logger, level, *args, **kwds) as capture:
            yield capture
        if log_msg is not None:
            log_pattern = re.escape(log_msg)
        if log_pattern is not None:
            for logline in capture.output:
                message = logline.split(':', 2)[2]
                if re.match(log_pattern, message):
                    break
            else:
                self.assertRegex(message, log_pattern)  # it fails


    def popen(
        self,
        *args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        **kwargs,
    ):
        proc = subprocess.Popen(  # noqa: S603
            *args,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            **kwargs
        )
        self.addCleanup(self._popen_kill, proc)
        if stdin is subprocess.PIPE:
            self.addCleanup(proc.stdin.close)
        if stdout is subprocess.PIPE:
            self.addCleanup(proc.stdout.close)
        if stderr is subprocess.PIPE:
            self.addCleanup(proc.stderr.close)
        return proc

    def _popen_kill(self, proc, timeout=.1):
        if proc.returncode is not None:
            return
        proc.terminate()
        try:
            proc.wait(timeout)
        except TimeoutError:
            proc.kill()

    def selector(self, file, event=selectors.EVENT_READ):
        sel = selectors.DefaultSelector()
        sel.register(file, event)
        self.addCleanup(sel.close)
        return sel



class NetworkMixin:
    host = '127.0.0.2'
    port = 8446

    socket: socket.socket

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.socket = socket.socket()
        cls.addClassCleanup(cls.socket.close)
        cls.addClassCleanup(cls.socket.shutdown, socket.SHUT_RDWR)
        cls.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        cls.socket.bind((cls.host, cls.port))
        cls.socket.listen(1)
        cls.socket.settimeout(1)

    def setUp(self):
        # make sure no request is pending
        self.socket.settimeout(0)
        try:
            self.socket.accept()
        except OSError as exc:
            if exc.errno not in (errno.EAGAIN, errno.ECONNABORTED):
                raise
        self.socket.settimeout(1)


def tls_decode(tls_connection, new_data=None):
    contents = []
    input_data = tls_connection._input_data
    input_handshake = tls_connection._input_handshake
    try:
        if new_data:
            tls_connection._input_data += new_data
        while next_content := tls_connection._read_next_content():
            content_type, content_data = next_content
            stream = TLSIO(content_data)
            content = Content.get_parser(content_type).parse(stream)
            stream.ensure_eof()
            contents.append(content)
    finally:
        tls_connection._input_data = input_data
        tls_connection._input_handshake = input_handshake
    return contents
