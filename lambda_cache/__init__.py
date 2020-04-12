__all__ = ["cache", "get_entry"]
__version__ = "0.8.0"

from .ssm import cache, get_entry
from .secrets_manager import cache, get_entry
from .s3 import cache, get_entry
