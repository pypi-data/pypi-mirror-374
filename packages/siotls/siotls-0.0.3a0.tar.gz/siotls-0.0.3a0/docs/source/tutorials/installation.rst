Installation
============

siotls is a typical pure Python library that can be installed using pip,
but it requires additional backend libraries to perform cryptographic
calculations and validate certificates against a trusted authority.


Choose the backends
-------------------

Choose a *crypto backend*. It dictates what *cryptographic algorithms*
are available when establishing a connection. The first step done by TLS
is to agree with the peer on a common set of cryptographic algorithms,
to secure the rest of the connection. The more algorithms are available
for negotiation, the higher the chance is to agree with the peer on one.
`OpenSSL / cryptography`_ is recommended.

Choose a *trust backend*. It authenticates the peer and makes sure the
connection has not been compromised. Depending on your needs you might
want a general-purpose trust backend or a ligher one where only a
handfull of root certificates are allowed. `OpenSSL / cryptography`_
using your OS certificate store is recommended.


OpenSSL / cryptography
~~~~~~~~~~~~~~~~~~~~~~

*Recommended for general purpose.*

* ☑ crypto backend
* ☑ trust backend

`OpenSSL`_ is a robust, commercial-grade, full-featured toolkit for
general-purpose cryptography and secure communication. `cryptography`_
is the official python binding, maintained by :abbr:`PyCA (Python
Cryprographic Authority)`.

The *crypto backend* supports all the cryptographic suites of TLS 1.3.
It also offers a *trust backend* that aims to be compliant with the
`Baseline Requirements`_, a document that defines guidelines for the
management of publicly-trusted TLS Server Certificates. This makes this
backend well equipped to safely browse the web.

To use siotls with openssl/cryptography run:

.. code::

	pip install siotls[openssl]

.. _OpenSSL: https://openssl-library.org/
.. _cryptography: https://cryptography.io/
.. _Baseline Requirements:
	https://cabforum.org/working-groups/server/baseline-requirements/documents/


HACL* / pyhacl
~~~~~~~~~~~~~~

* ☑ crypto backend
* ☐ trust backend

The `HACL*`_ library is a High Assurance Cryptographic Library written
in `F*`_, a general-purpose proof-oriented programming language, and
compiled in C. `pyhacl`_ is an unofficial cython binding, maintained
by one of the authors of siotls.

There are only a very few algorithms available in pyhacl. It is notably
lacking support for RSA and ECDSA P-384, both of which are required
to validate certificates signed by Let's Encrypt. This makes this
backend ill-suited to browse the web. On the other hand, its small size
and portable C code makes for an excellent choice for IoT devices and
:attr:`~siotls.configuration.TLSConfiguration.trusted_public_keys`.

To use siotls with HACL*/pyhacl run:

.. code::

	pip install siotls[hacl]

.. _HACL*: https://hacl-star.github.io/
.. _F*: https://fstar-lang.org/
.. _pyhacl: https://pypi.org/project/pyhacl/


OS Trust store
~~~~~~~~~~~~~~

Planned.

* ☐ crypto backend
* ☑ trust backend


Use a crypto backend
--------------------

Use :func:`siotls.crypto.install` to install one or several crypto
backends.

Example:

.. code-block:: python

	import siotls.crypto

	siotls.crypto.install('openssl')

Another example to install Chacha from HACL*, and the rest from OpenSSL:

.. code-block:: python

	import siotls.crypto
	from siotls.iana import CipherSuites

	siotls.crypto.install('hacl', [CipherSuites.TLS_CHACHA20_POLY1305_SHA256])
	siotls.crypto.install('openssl', duplicate='skip')


Use a trust backend
-------------------

Use :func:`siotls.trust.get_default_verifier` to automatically locate
and instantiate the best available
:attr:`~siotls.configuration.TLSConfiguration.x509verifier`.


Example:

.. code-block:: python

	from siotls import TLSConfiguration
	from siotls.trust import get_default_verifier

	tls_config = TLSConfiguration('client', x509verifier=get_default_verifier())


Alternatively, it is possible to manually import and instanciate a
:class:`~siotls.trust.X509Verifier`.

Example:

.. code-block:: python

	# attempt to load the system's list of trusted CA root certificates
	# fallback on using certifi
	from siotls.trust import get_default_store
	der_ca_certs = get_default_store()

	# use cryptography.x509.verification
	from siotls.trust.openssl import X509Verifier
	x509verifier = X509Verifier(ca_certs)

	# make a configuration
	from siotls import TLSConfiguration
	tls_config = TLSConfiguration('client', x509verifier=x509verifier)
