"""
File: /exceptions/__init__.py
Created Date: Tuesday July 29th 2025
Author: Harsh Kumar <fyo9329@gmail.com>
-----
Last Modified: Tuesday August 12th 2025
Modified By: the developer formerly known as Harsh Kumar at <fyo9329@gmail.com>
-----
"""

from .exceptions import AuthenticationError, ConnectionError, LumenError, NotFoundError, ValidationError

__version__ = "1.0.5"

__all__ = [
    "LumenError",
    "AuthenticationError", 
    "NotFoundError",
    "ValidationError",
    "ConnectionError",
]