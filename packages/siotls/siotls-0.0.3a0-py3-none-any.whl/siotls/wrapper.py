from __future__ import annotations

import logging
import typing

if typing.TYPE_CHECKING:
    import socket

    import siotls.connection


logger = logging.getLogger(__name__)


# TODO: do like ssl.SSLSocket and inherit from socket.socket?
class WrappedSocket:
    r"""
    Bind a :class:`~siotls.connection.TLSConnection` to a TCP
    :class:`~socket.socket` and get a file-like object with
    :meth:`read`, :meth:`write`, :meth:`close`.

    .. code-block:: python

       conf = TLSConfiguration('client')
       conn = TLSConnection(conf, server_hostname='example.com')
       with socket.create_connection(('example.com', 443)) as sock:
           sock.settimeout(5)
           with conn.wrap(sock) as sfile:
               sfile.write(b"GET / HTTP/1.0\r\nHost: example.com\r\n\r\n")
               while conn.is_connected():
                   print(sfile.read().decode(errors='replace'))
    """
    conn: siotls.connection.TLSConnection  #:
    sock: socket.socket  #:

    def __init__(self, conn: siotls.connection.TLSConnection, sock: socket.socket):
        self.conn = conn
        self.sock = sock

    def __enter__(self) -> typing.Self:
        self.do_handhskake()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self.conn.fail()
        self.close()

    def do_handhskake(self) -> None:
        """
        Take over the TCP socket to perform the TLS handshake, sending
        and receiving as many TCP segments as necessary.
        """
        self.conn.initiate_connection()
        if self.conn.config.side == 'client':
            self.sock.send(self.conn.data_to_send())
        while not self.conn.is_post_handshake():
            if input_data := self.sock.recv(self.conn.max_fragment_length):
                try:
                    self.conn.receive_data(input_data)
                finally:
                    if output_data := self.conn.data_to_send():
                        self.sock.send(output_data)
            else:
                self.conn.close_receiving_end()  # it goes post handshake

    def read(self) -> bytes:
        """
        Read from the TCP socket, decrypt and return the incomming
        application data.

        Handle the protocol messages (key update, heartbeat, ...)
        automatically, sending replies when necessary.

        Return empty bytes when the peer closed its sending side.
        """
        application_data = self.conn.data_to_read()
        while self.conn.is_connected() and not application_data:
            if input_data := self.sock.recv(self.conn.max_fragment_length):
                try:
                    self.conn.receive_data(input_data)
                finally:
                    if output_data := self.conn.data_to_send():
                        self.sock.send(output_data)
                application_data += self.conn.data_to_read()
            else:
                self.conn.close_receiving_end()
        return application_data

    def write(self, data: bytes) -> None:
        """ Encrypt the data and send it over the TCP socket. """
        self.conn.send_data(data)
        self.sock.send(self.conn.data_to_send())

    def close(self) -> None:
        """
        Signal the peer we won't send any other message and then close
        the TCP socket.

        There's a risk of data loss / truncation attack if this method
        is called before the peer closed its sending side, use
        :meth:`read`.
        """
        self.conn.close_sending_end()
        if alert := self.conn.data_to_send():
            self.sock.send(alert)
        self.sock.close()
