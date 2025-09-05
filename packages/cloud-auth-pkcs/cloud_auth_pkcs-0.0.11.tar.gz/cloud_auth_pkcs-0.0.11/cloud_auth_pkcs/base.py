import pkcs11

from pkcs11 import MGF, Attribute, KeyType, Mechanism, ObjectClass, Key, Mechanism


from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

def sha256(data: bytes) -> bytes:
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(data)
    digest = digest.finalize()
    return digest

class BaseCredential():

    DEFAULT_MODULE = "/usr/lib/x86_64-linux-gnu/softhsm/libsofthsm2.so"

    def __init__(
        self,
        module,
        token,
        label,
        pin,
    ):

        self._module = module or self.DEFAULT_MODULE
        self._token = token
        self._label = label
        self._pin = pin

        try:
            lib = pkcs11.lib(module)
            self._token = lib.get_token(token_label=token)
        except Exception as e:
            raise e
        
    def sign(self, data):
        try:
            with self._token.open(user_pin=self._pin) as session:
                key = session.get_key(label=self._label, key_type=KeyType.RSA) 
                return key.sign(data,mechanism=Mechanism.SHA256_RSA_PKCS)
        except pkcs11.NoSuchKey as e:
            raise Exception("Key with label {} not found {}".format(self._label,repr(e)))
        except pkcs11.MultipleObjectsReturned as e:            
            raise  Exception("Multiple keys with label {} not found {}".format(self._label, repr(e)))
        except Exception as e:
            raise Exception(repr(e))

    # def hmac(self, data):

    #     with self._token.open(user_pin=self._pin) as session:
    #         try:    
    #             key = session.get_key(label=self._label, key_type=pkcs11.KeyType.SHA256_HMAC) 
    #             kDate = key.sign(data, mechanism=pkcs11.mechanisms.Mechanism.SHA256_HMAC) 
    #         except pkcs11.NoSuchKey as e:
    #             try:
    #                 key = session.get_key(label=self._label, key_type=pkcs11.KeyType.GENERIC_SECRET) 
    #                 kDate = key.sign(data, mechanism=pkcs11.mechanisms.Mechanism.SHA256_HMAC)
    #                 pass
    #             except Exception as e:
    #                 raise Exception("Key with label {} not found {}".format(self._label,repr(e)))
    #         except pkcs11.MultipleObjectsReturned as e:
    #             raise  Exception("Multiple keys with label {} not found {}".format(self._label, repr(e)))
    #         except Exception as e:
    #             raise Exception(repr(e))
    #     return kDate
