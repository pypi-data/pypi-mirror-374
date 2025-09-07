""" A simple HTTPS server. """

import logging
import socket
from datetime import UTC, datetime
from http import HTTPStatus
from wsgiref.handlers import format_date_time

from siotls import USER_AGENT, TLSConfiguration, TLSConnection
from siotls.pem import decode_pem_certificate_chain, decode_pem_private_key

logger = logging.getLogger(__name__)


def serve(
    host: str,
    port: int,
    certificate_chain_path: str,
    private_key_path: str,
    *,
    log_keys: bool
):
    """
    Start a HTTPS server.

    :param host: The hostname or IPv6 address to bind.
    :param port: The TCP port to bind.
    :param certificate_chain_path: The path to a PEM-encoded certificate
        chain.
    :param private_key_path: The path to the PEM-encoded private key for
        the certificate chain.
    :param log_keys: Whether to log the TLS secrets, for network
        analyzing tools such as wireshark.
    """

    # We start by loading the certificate chain and private key. There
    # are two dominants formats: PEM and DER. A PEM file is only a DER
    # file that has been base64-ified and placed between
    # "-----BEGIN XXX-----" and "-----END XXX-----". If you have a DER
    # file you can use it immediately. If you have a PEM file you first
    # need to decode it to DER.
    # This code assumes the file is PEM-encoded.
    with (open(certificate_chain_path, 'rb') as certificate_chain_file,
          open(private_key_path, 'rb') as private_key_file):
        certificate_chain = decode_pem_certificate_chain(certificate_chain_file.read())
        private_key = decode_pem_private_key(private_key_file.read())

    # We then create a TLSConfiguration object for a server. A single
    # configuration object can be used for many TLS connections. The
    # private key and certificate chain are required to start a server.
    # The ALPN value advertises that this server is a HTTP server but
    # only compatible with HTTP/1 and not HTTP/2 or HTTP/3. Log keys is
    # for wireshark and other compatible network analysing tools for
    # debugging purpose. Many more configuration options are available.
    tls_config = TLSConfiguration(
        'server',
        private_key=private_key,
        certificate_chain=certificate_chain,
        alpn=[b'http/1.1', b'http/1.0'],
        log_keys=log_keys,
    )

    # The following few lines create a IPv6/TCP server socket and start
    # accepting new clients. The server is terrible, it only accepts and
    # processes one client at a time, but it is enough for the sake of
    # this example.
    server = socket.create_server((host, port), family=socket.AF_INET6)
    logger.info("serving https on %s port %s", host, port)
    with server:
        while True:
            client, client_addr = server.accept()
            with client:
                logger.info("connection with %s established", client_addr[:2])

                # A TCP connection has been established with a client
                # but no byte has been exchanged yet (beside the initial
                # TCP triple handshake), it is time to secure the
                # connection with TLS. We create a TLSConnection object
                # for this client, and use it to wrap the TCP socket.
                conn = TLSConnection(tls_config)
                try:
                    # wrap() has the do_handhskake() and the close()
                    # methods to initialize and finilize a secure TLS
                    # connection. Those two methods are automatically
                    # called when entering a context manager.
                    # Please note that wrap() only works with regular
                    # blocking sockets. Other networking libraries (e.g.
                    # asyncio) can't use wrap().
                    with conn.wrap(client) as sclient:
                        # Starting here the connection has been secured:
                        # the next bytes (received and sent) are
                        # encrypted. The sclient object encrypts and
                        # decrypts the messages on the fly.
                        logger.info("connection with %s secured", client_addr[:2])
                        http_serve_one(sclient, client_addr)
                except Exception:
                    logger.exception("connection with %s failed", client_addr[:2])
            logger.info("connection with %s closed", client_addr[:2])


def http_serve_one(sclient, client_addr):
    """ Exchange a HTTP/1.1 request and response with a client. """

    # The first step of any HTTP server is to receive the client
    # request. Here a call to read() blocks until there are decrypted
    # data available for the application, and read them. It is possible
    # that siotls makes multiple call to recv()/send() on the underlying
    # socket, to exchange additional TLS handshakes (e.g. session
    # ticket, new key).
    http_req = sclient.read()

    # The following code decodes the HTTP request and produce a
    # response. Again the implementation is terrible but it is enough
    # for the sake of this example.
    request_line = http_req.partition(b'\r\n')[0].decode(errors='replace')
    try:
        method, path, version = request_line.split(' ')
    except ValueError:
        code, body = 505, ""
    else:
        code, body = (
                 (405, "") if method != 'GET'
            else (404, "") if path != '/'
            else (200, "Hello from siotls\n")
        )
    now = datetime.now().astimezone()
    http_res = make_http11_response(code, body, now=now)
    logger.info(
        '%s - - [%s] "%s" %d %d',
        client_addr[0],
        now.strftime('%d/%b/%Y:%H:%M:%S %z'),
        request_line,
        code,
        len(body),
    )

    # Now that we have a response ready we can send it to the client.
    # Here a call to send() blocks until the data has been encrypted and
    # sent in its entirety. It is possible that siotls fragments the
    # data and sends it over multiple TLS records.
    sclient.write(http_res)


def make_http11_response(code: int, textbody: str, now: datetime | None = None):
    date = format_date_time((now or datetime.now(UTC)).timestamp())
    status = HTTPStatus(code)
    return (
        f"HTTP/1.1 {status.value} {status.phrase}\r\n"
        f"Date: {date}\r\n"
        f"Server: {USER_AGENT}\r\n"
        f"Connection: close\r\n"
        f"Content-Type: text/plain; charset=utf-8\r\n"
        f"Content-Length: {len(textbody)}\r\n"
        f"\r\n"
    ).encode() + textbody.encode()
