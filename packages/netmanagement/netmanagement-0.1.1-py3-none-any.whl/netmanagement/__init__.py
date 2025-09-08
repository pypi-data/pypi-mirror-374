"""
netmanagement - A standalone requests-like library with logging and special features

This module provides a standalone implementation that mimics the requests library
interface, with additional logging and special features running transparently.
"""

# Import our standalone implementation
from .core import get, Response, RequestException, ConnectionError, HTTPError, Timeout

# Package metadata
__version__ = "0.1.1"
__author__ = "Your Name"
__title__ = "netmanagement"
__license__ = "MIT"
__description__ = "A standalone requests-like library with hidden logging and special features"

# Export the main interface
__all__ = [
    'get', 'Response', 'RequestException', 'ConnectionError', 'HTTPError', 'Timeout',
    '__version__', '__author__', '__title__', '__license__', '__description__'
]
