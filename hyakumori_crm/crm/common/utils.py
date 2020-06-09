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


def get_customer_name(name_dict):
    customer_name = ""
    if name_dict.get("last_name", None) is not None:
        customer_name = name_dict.get("last_name")
    if name_dict.get("first_name", None) is not None:
        customer_name += " " + name_dict.get("first_name")

    return customer_name


def tags_csv_to_dict(tags_data: str):
    result = {}
    if not tags_data:
        return result
    else:
        tags_data_split = tags_data.split("; ")
        for tag in tags_data_split:
            tag_k_v = tag.split(":")
            if len(tag_k_v) == 2:
                tag_key, tag_val = tag_k_v[0], tag_k_v[1]
                result[tag_key] = tag_val
            else:
                raise ValueError()
        return result
