""" A simple HTTPS client. """

import logging
import socket

from siotls import USER_AGENT, TLSConfiguration, TLSConnection
from siotls.trust import get_truststore

logger = logging.getLogger(__name__)


def connect(host, port, *, check_certificate: bool, log_keys: bool):
    """
    Connect to a HTTPS server.

    :param host: The hostname or IPv6 address to reach.
    :param port: The TCP port to reach (usually 443).
    :param check_certificate: Whether to verify the server's certificate
        or not. It is insecure to bypass the check.
    :param log_keys: Whether to log the TLS secrets, for network
        analyzing tools such as wireshark.
    """

    # We then create a TLSConfiguration object for a client. A single
    # configuration object can be used for many TLS connections. The
    # truststore option is for verifying the server certificate,
    # to check that the certificate is valid and was delivered for the
    # requested hostname. The ALPN option is welcome when connecting to
    # a HTTP host, for servers that are capable of understanding both
    # HTTP/1 and HTTP/2. Here we use it to select a HTTP/1 server. Many
    # more configuration options are available.
    options = {}
    if check_certificate:
        options['truststore'] = get_truststore()
    config = TLSConfiguration(
        'client',
        alpn=[b'http/1.1', b'http/1.0'],
        log_keys=log_keys,
        **options,  # type: ignore[arg-type]
    )

    # We then proceed to open a TCP connection to the remote server.
    with socket.create_connection((host, port), timeout=5) as server:
        logger.info("connection with %s established", (host, port))

        # A TCP connection has been established with a server but no
        # byte has been exchanged yet (beside the initial TCP triple
        # handshake), it is time to secure the connection with TLS. We
        # create a TLSConnection object for this client, and use it to
        # wrap the TCP socket.
        conn = TLSConnection(config, server_hostname=host)

        # wrap() has the do_handhskake() and the close() methods to
        # initialize and finilize a secure TLS connection. Those two
        # methods are automatically called when entering a context
        # manager. Please note that wrap() only works with regular
        # blocking sockets. Other networking libraries (e.g. asyncio)
        # can't use wrap().
        with conn.wrap(server) as sserver:
            # Starting here the connection has been secured: the next
            # bytes (received and sent) are encrypted. The sserver
            # object encrypts and decrypts the messages on the fly.
            logger.info("connection with %s secured", (host, port))
            http_connect_one(host, sserver)
    logger.info("connection with %s closed", (host, port))


def http_connect_one(host, sserver):
    """ Exhange a HTTP/1.1 request.  """
    http_req = make_http11_request(host, 'GET', '/', '')
    logger.debug("sending payload:\n%s", http_req.decode())
    sserver.write(http_req)

    http_res = sserver.read()
    headers, _, body = http_res.partition(b'\r\n\r\n')
    logger.debug("received headers:\n%s", headers.decode(errors='replace'))
    print(body.decode(errors='replace'))  # noqa: T201


def make_http11_request(host: str, method: str, path: str, textbody: str):
    return (
        f"{method} {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"Connection: close\r\n"
        f"Content-Type: text/plain; charset=utf-8\r\n"
        f"Content-Length: {len(textbody)}\r\n"
        f"User-Agent: {USER_AGENT}\r\n"
        "\r\n"
    ).encode() + textbody.encode()
