import json

from cryptography.fernet import Fernet
from django.core.serializers.json import DjangoJSONEncoder

key = Fernet.generate_key()


class EncryptError(Exception):
    pass


class DecryptError(Exception):
    pass


def encrypt_string(data, from_dict=True):
    try:
        fernet = Fernet(key)
        if from_dict:
            data = json.dumps(data, cls=DjangoJSONEncoder).encode("utf8")
        return fernet.encrypt(data).decode("utf8")
    except:
        raise EncryptError


def decrypt_string(data, to_dict=True):
    try:
        fernet = Fernet(key)
        content = fernet.decrypt(data.encode("utf8"))
        if to_dict:
            return json.loads(content)
        return content
    except:
        raise DecryptError
