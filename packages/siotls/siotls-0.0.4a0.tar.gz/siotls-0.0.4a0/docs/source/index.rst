siotls: sans-io TLS 1.3 for Python
==================================

**siotls** is a pure Python implementation of the `TLS 1.3`_ protocol
stack. It performs no I/O on its own, supports various cryptographic
libraries and integrates with the OS trust store.

.. _TLS 1.3: https://datatracker.ietf.org/doc/html/rfc8446

In this documentation
---------------------

.. grid:: 1 1 2 2

   .. grid-item:: :doc:`Tutorials <tutorials/index>`

      **Get started** with simple examples to run a TLS client or
      server.

   .. grid-item:: :doc:`References <references/index>`

      **Comprehensive API** documentation.

Sans-IO Philosophy
------------------

**siotls** embraces the `Sans-IO`_ movement: it operates solely on
bytes, leaving all socket operations to the user. By controlling the
flow of bytes in and out of siotls, the users retain the freedom to
choose the network stack they want, may it be threads, asyncio, twisted
or any other.

.. _Sans-IO: https://sans-io.readthedocs.io/

Bring your own Cryptography
---------------------------

**siotls** leverages external libraries for all cryptographic
computations. It is not tied to a specific one; rather, it defines a way
to bridge with existing cryptographic backends.

Out of the box `OpenSSL`_ (via `cryptography`_) and `HACL\*`_ (via
`pyhacl`_) are supported. Support for other backends is possible, given
a bridge is added, with no modification to the source code.

.. _OpenSSL: https://openssl-library.org/
.. _cryptography: https://cryptography.io/
.. _HACL*: https://hacl-star.github.io/
.. _pyhacl: https://pypi.org/project/pyhacl/

Why another SSL/TLS Library?
----------------------------

The Python standard library includes the `ssl`_ module, which can be
used to establish TLS connections, also sans-io via the `Memory BIO`_
mode. It is mostly C code and makes heavy use of OpenSSL under the hood.

That it uses OpenSSL is a *good* thing. It is a mature and well deployed
library. It implements all cryptographic primitives supported by TLS. It
is capable of establishing connections using previous TLS versions (a
safe way). It integrates well with operating systems that use OpenSSL
themselves, mostly Linux ones.

That it *only* uses OpenSSL isn't so much a good thing. OpenSSL is more
a *framework* than a *library*: you need to embrace the OpenSSL
philosophy and make a comprehensive usage of the framework in order to
be effective. The ssl module is a testament to that: many of its objects
and methods map to OpenSSL concepts with minimal abstraction.

It also doesn't integrate very well with Windows. Windows uses and
exposes the Microsoft CryptoAPI, a comprehensive cryptography library
with utilities to manage the system trust store. Ideally the ssl module
should use it and not OpenSSL, but OpenSSL is so entangled with CPython
that CPython ships with OpenSSL to work on Windows.

There have been various discussions about the future of OpenSSL within
Python, mostly regarding the ssl module and its integration with other
standard libraries (urllib, smtplib, ...). We, the authors of siotls,
want to take part in this effort, to make a better SSL/TLS stack happens
for Python. We have no pretensions to replace the existing ssl module;
rather, we provide the community with a fresh vision of what could a TLS
library look like for Python.

.. _ssl: https://docs.python.org/3/library/ssl.html
.. _Memory BIO: https://docs.python.org/3/library/ssl.html#memory-bio-support

.. toctree::
   :maxdepth: 2
   :hidden:

   tutorials/index
   references/index
