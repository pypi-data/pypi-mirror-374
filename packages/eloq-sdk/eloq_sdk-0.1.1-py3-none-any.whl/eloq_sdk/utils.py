import base64
import datetime


def compact_mapping(obj):
    """Compact a dict/mapping by removing all None values."""

    return {k: v for k, v in obj.items() if v is not None}


def to_iso8601(dt):
    """Convert a datetime object to an ISO 8601 string."""

    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def from_iso8601(s):
    """Convert an ISO 8601 string to a datetime object."""

    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")


def decode_base64_string(encoded_string: str, error_message: str = "解码失败") -> str:
    """Decode a base64 encoded string to UTF-8.
    
    :param encoded_string: The base64 encoded string to decode.
    :param error_message: Custom error message for the exception.
    :return: The decoded UTF-8 string.
    :raises: ValueError if decoding fails.
    """
    try:
        return base64.b64decode(encoded_string).decode('utf-8')
    except Exception as e:
        raise ValueError(f"{error_message}: {str(e)}")
