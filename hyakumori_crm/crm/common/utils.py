import json
import random

from cryptography.fernet import Fernet
from django.core.serializers.json import DjangoJSONEncoder
from sequences import get_next_value

key = Fernet.generate_key()
fernet = Fernet(key)


class EncryptError(Exception):
    pass


class DecryptError(Exception):
    pass


def encrypt_string(data, from_dict=True):
    try:
        if from_dict:
            data = json.dumps(data, cls=DjangoJSONEncoder).encode("utf8")
        return fernet.encrypt(data).decode("utf8")
    except:
        raise EncryptError


def decrypt_string(data, to_dict=True):
    try:
        content = fernet.decrypt(data.encode("utf8"))
        if to_dict:
            return json.loads(content)
        return content
    except:
        raise DecryptError


def generate_sequential_id(prefix, id_sequence):
    """
    Generate ids using true sequential index
    Example:
    >>> generate_sequential_id("DFFC", "customer_ids")
    :param prefix:
    :param id_sequence: name of the sequence
    :return:
    """
    rand = "{:02d}".format(int(random.random() * 100))
    index = get_next_value(id_sequence)
    formatted_index = "{:08d}".format(index)
    return f"{prefix}{formatted_index}{rand}"
