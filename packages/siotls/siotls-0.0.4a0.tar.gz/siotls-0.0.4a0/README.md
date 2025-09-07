![pypi version badge](https://img.shields.io/pypi/v/siotls)
![coverage badge](./coverage-badge.svg)

siotls
======

Sans-IO Python implementation of the TLS 1.3 (RFC 8446) protocol stack.


Quick Start
-----------

Install the library and select a cryptographic backend, [openssl](#) is
a sane choice.

```bash
pip install siotls[openssl]
```

Use [`siotls.crypto.install`](#) to load the cryptography backend you
installed.

```py
import siotls

siotls.crypto.install('openssl')
```

### Client config

Create a client-side [`TLSConfiguration`](#) object.

A [`truststore`](#) is required to verify the server certificates,
leaving it out makes the configuration *insecure* (as no certificate
will be verified). The [`get_truststore`](#) function attempts to locate
and load the truststore of the operating system, and fallbacks on using
[`certifi`](#) (Mozilla's bundled root CA certificates) if installed.

```py
from siotls import TLSConfiguration
from siotls.trust import get_truststore

tls_client_config = TLSConfiguration(
    side='client',
    truststore=get_truststore(),
)
```

### Server config

Create a server-side [`TLSConfiguration`](#) object.

Bth a [`private_key`](#) and [`certificate_chain`](#) are required, they
must be in DER-format, the [`siotls.pem`](#) module has utilities to
convert PEM to DER.

```py
from siotls import TLSConfiguration
from siotls.pem import decode_pem_certificate_chain, decode_pem_private_key

with open('/path/to/private_key.pem', 'rb') as file:
    der_private_key = decode_pem_private_key(file.read())
with open('/path/to/certificate_chain.pem', 'rb') as file:
    der_certificate_chain = decode_pem_certificate_chain(file.read())

tls_server_config = TLSConfiguration(
    side='server',
    private_key=der_private_key,
    certificate_chain=der_certificate,
)
```

### Connection

Then establish a connection using your favorite network library and
create a [`TLSConnection`](#) object for that connection. The following
examples show a plain blocking socket client. A server connection would
be very similar.

```py
import socket
from siotls import TLSConnection

tls_client_config = ...  # above snippet

sock = socket.create_connection(('example.com', 443))
conn = TLSConnection(tls_client_config, server_hostname='example.com')
```

The next step is to exchange messages with the peer to secure the
connection.

```py
conn.initiate_connection()
if conn.config.side == 'client':
    sock.sendall(conn.data_to_send())
while not conn.is_post_handshake():
    if input_data := sock.recv(4096):
        try:
            conn.receive_data(input_data)
        finally:
            if output_data := conn.data_to_send():
                sock.sendall(output_data)
    else:
        conn.close_receiving_end()  # it goes post handshake
```

### Exchange

The above `while` loop stops once the connection has been secured (or
closed). At this moment it is safe to exchange data, the following
example sends a basic HTTP request and prints the result.

```py
req = """\
GET / HTTP/1.1\r
Host: example.com\r
Connection: close\r
\r
"""
res = bytearray()

if conn.is_connected():
    conn.send_data(req.encode())
    sock.sendall(conn.data_to_send())

    while conn.is_connected():
        if input_data := sock.recv(4096):
            try:
                conn.receive_data(input_data)
            finally:
                if output_data := conn.data_to_send():
                    sock.sendall(output_data)
            res += conn.data_to_read()
        else:
            conn.close_receiving_end()  # it disconnects

    conn.close_sending_end()
    sock.sendall(conn.data_to_send())

sock.close()

print(res.decode())
```

Documentation
-------------

Available online at [readthedocs.io](#).

Contribute
----------

The same as usual: fork, branch, pull request.

We are using [uv] and [pre-commit]:

    # make sure to be in the right directory
    cd path/to/siotls

    # install dependencies in a venv
    uv venv
    uv sync --group precommit --group tests --group docs --extra hacl --extra openssl
    uv run pre-commit install

    # run tests
    SIOTLS_INTEGRATION=1 uv run python -m unittest -v

    # build docs
    uv run sphinx-build -j auto docs/source/ docs/build/

Not all tests run by default, only the fast unittests do. Enable more
test suites setting the below environment variables to `1`.

* `SIOTLS_INTEGRATION`: tests that test more than a single function at a
  time.
* `SIOTLS_SLOW`: tests that make heavy use of the CPU.
* `SIOTLS_EXTERNAL`: tests that connect to remote servers on the
  internet.

The code is linted using [ruff] and [isort], the typehints are validated
using [mypy]. All of them run automatically with pre-commit, so you
don't have any command to know.

[uv]: https://docs.astral.sh/uv/
[pre-commit]: https://pre-commit.com/
[ruff]: https://docs.astral.sh/ruff/
[isort]: https://pycqa.github.io/isort/
[mypy]: https://mypy.readthedocs.io/en/stable/index.html
