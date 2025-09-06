"""
apikit: A Python library for building API collections.
"""

from .api_collection import APICollection
from .client import Client
from .schema import API, BaseRequest, BaseResponse
from .envvar import EnvVar

__version__ = "1.0.0"
__all__ = ["APICollection", "Client", "API", "BaseRequest", "BaseResponse", "EnvVar"]
