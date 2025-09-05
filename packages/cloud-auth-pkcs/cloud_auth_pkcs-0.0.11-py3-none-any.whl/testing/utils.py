from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend

import pkcs11

from pkcs11.constants import Attribute

def loadHMAC(session, keylabel, id,  hmac_key):
    try:
        return session.create_object({
            Attribute.CLASS: pkcs11.ObjectClass.SECRET_KEY,
            Attribute.KEY_TYPE: pkcs11.KeyType.SHA256_HMAC,
            Attribute.VALUE: hmac_key.encode('utf-8'),
            Attribute.LABEL: keylabel,
            Attribute.ID: id.encode('utf-8'),
            Attribute.TOKEN: True,
            Attribute.SENSITIVE: True,  
            Attribute.SIGN: True,
            Attribute.VERIFY: True, 
            Attribute.ENCRYPT: False, 
            Attribute.DECRYPT: False,                                                              
        })

    except Exception as e:
        raise Exception("error occured creating HMAC Key {}".format(e))


def loadRSA(session, keylabel, id,  private_key):
    try:
        der_private_key = private_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        k = pkcs11.util.rsa.decode_rsa_private_key(der_private_key)

        k[Attribute.LABEL] = keylabel
        k[Attribute.ID] = id.encode('utf-8')
        k[Attribute.TOKEN] = True
        k[Attribute.SENSITIVE] = True

        return session.create_object(k)

    except Exception as e:
        raise Exception("error occured creating RSA Key {}".format(repr(e)))