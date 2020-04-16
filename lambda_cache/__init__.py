# -*- coding: utf-8 -*-

"""
lambda-cache
~~~~~~~~~~~~

A python package for caching within AWS Lambda Functions

Full Documentation is at <https://lambda-cache.rtfd.io>.
:license: MIT, see LICENSE for more details.
"""

__version__ = "0.8.1"

from .ssm import cache, get_entry
from .secrets_manager import cache, get_entry
from .s3 import cache, get_entry
