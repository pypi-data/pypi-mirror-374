Cipher Suites
=============

.. automodule:: siotls.crypto.cipher_suites

   .. autoclass:: siotls.crypto.cipher_suites.TLSCipherSuite
      :members:
      :member-order: bysource

   .. autoclass:: siotls.crypto.cipher_suites.CipherState
      :members:
      :no-special-members:
      :member-order: bysource

Backend
-------

.. autoclass:: siotls.crypto.cipher_suites.ICipher
   :private-members: _ciphermod, _encrypt, _decrypt
   :exclude-members: __init__, __new__

.. autoclass:: siotls.crypto.cipher_suites.Aes128GcmMixin
   :exclude-members: __init__, __new__

.. autoclass:: siotls.crypto.cipher_suites.Aes256GcmMixin
   :exclude-members: __init__, __new__

.. autoclass:: siotls.crypto.cipher_suites.ChaPolyMixin
   :exclude-members: __init__, __new__

.. autoclass:: siotls.crypto.cipher_suites.Aes128CcmMixin
   :exclude-members: __init__, __new__

.. autoclass:: siotls.crypto.cipher_suites.Aes128Ccm8Mixin
   :exclude-members: __init__, __new__
