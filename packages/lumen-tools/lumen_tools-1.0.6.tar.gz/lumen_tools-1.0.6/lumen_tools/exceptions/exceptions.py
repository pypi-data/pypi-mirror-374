"""
File: /exceptions/exceptions.py
Created Date: Tuesday July 29th 2025
Author: Harsh Kumar <fyo9329@gmail.com>
-----
Last Modified: Tuesday August 12th 2025
Modified By: the developer formerly known as Harsh Kumar at <fyo9329@gmail.com>
-----
"""

class LumenError(Exception):
    """Base exception for Lumen Core client"""
    pass

class AuthenticationError(LumenError):
    """Authentication related errors"""
    pass

class NotFoundError(LumenError):
    """Resource not found errors"""
    pass

class ValidationError(LumenError):
    """Request validation errors"""
    pass

class ConnectionError(LumenError):
    """Connection related errors"""
    pass