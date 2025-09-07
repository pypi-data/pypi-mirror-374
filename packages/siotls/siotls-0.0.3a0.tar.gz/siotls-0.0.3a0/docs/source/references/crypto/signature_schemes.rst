Signature Schemes
=================

.. automodule:: siotls.crypto.signature_schemes

   .. autoclass:: siotls.crypto.signature_schemes.TLSSignatureScheme
      :members:

   .. autoclass:: siotls.crypto.signature_schemes.ISign
      :members:
      :exclude-members: __new__

   .. autoclass:: siotls.crypto.signature_schemes.SignatureKeyError
      :exclude-members: __init__, __new__

   .. autoclass:: siotls.crypto.signature_schemes.SignatureSignError
      :exclude-members: __init__, __new__

   .. autoclass:: siotls.crypto.signature_schemes.SignatureVerifyError
      :exclude-members: __init__, __new__

Backend
-------

.. autoclass:: siotls.crypto.signature_schemes.RsaPkcs1Sha256Mixin
   :members:
   :exclude-members: __init__, __new__

.. autoclass:: siotls.crypto.signature_schemes.RsaPkcs1Sha384Mixin
   :members:
   :exclude-members: __init__, __new__

.. autoclass:: siotls.crypto.signature_schemes.RsaPkcs1Sha512Mixin
   :members:
   :exclude-members: __init__, __new__

.. autoclass:: siotls.crypto.signature_schemes.RsaPssRsaeSha256Mixin
   :members:
   :exclude-members: __init__, __new__

.. autoclass:: siotls.crypto.signature_schemes.RsaPssRsaeSha384Mixin
   :members:
   :exclude-members: __init__, __new__

.. autoclass:: siotls.crypto.signature_schemes.RsaPssRsaeSha512Mixin
   :members:
   :exclude-members: __init__, __new__

.. autoclass:: siotls.crypto.signature_schemes.RsaPssPssSha256Mixin
   :members:
   :exclude-members: __init__, __new__

.. autoclass:: siotls.crypto.signature_schemes.RsaPssPssSha384Mixin
   :members:
   :exclude-members: __init__, __new__

.. autoclass:: siotls.crypto.signature_schemes.RsaPssPssSha512Mixin
   :members:
   :exclude-members: __init__, __new__

.. autoclass:: siotls.crypto.signature_schemes.EcdsaSecp256r1Sha256Mixin
   :members:
   :exclude-members: __init__, __new__

.. autoclass:: siotls.crypto.signature_schemes.EcdsaSecp384r1Sha384Mixin
   :members:
   :exclude-members: __init__, __new__

.. autoclass:: siotls.crypto.signature_schemes.EcdsaSecp521r1Sha512Mixin
   :members:
   :exclude-members: __init__, __new__

.. autoclass:: siotls.crypto.signature_schemes.Ed25519Mixin
   :members:
   :exclude-members: __init__, __new__

.. autoclass:: siotls.crypto.signature_schemes.Ed448Mixin
   :members:
   :exclude-members: __init__, __new__
