from uuid import UUID

from urllib.parse import urlparse


def is_url(x):
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc])
    except AttributeError:
        return False


def is_uuid(uuid_str):
    try:
        uuid_obj = UUID(uuid_str)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_str
