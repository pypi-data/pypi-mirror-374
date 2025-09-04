from .client import EloqAPI
from .__version__ import __version__
from .exceptions import EloqAPIError


def from_environ():
    """Create a EloqAPI instance from environment variables."""

    return EloqAPI.from_environ()


def from_token(token):
    """Create a EloqAPI instance from a token."""

    return EloqAPI.from_token(token)
