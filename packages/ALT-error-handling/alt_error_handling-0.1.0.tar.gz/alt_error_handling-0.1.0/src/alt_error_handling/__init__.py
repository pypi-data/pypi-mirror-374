"""
ALT-error-handling: Advanced error handling utilities for Python.

This package provides decorators and utilities for consistent error handling
across Python applications.
"""

from alt_error_handling.constants import PACKAGE_NAME, PACKAGE_VERSION
from alt_error_handling.core import (
    ErrorHandlingError,
    aggregate_errors,
    convert_exceptions,
    ensure_cleanup,
    error_context,
    format_exception_chain,
    handle_errors,
    safe_execute,
)

__version__ = PACKAGE_VERSION
__author__ = "Avi Layani"
__email__ = "alayani@redhat.com"

__all__ = [
    # Main utilities
    "handle_errors",
    "convert_exceptions",
    "error_context",
    "safe_execute",
    "ensure_cleanup",
    "aggregate_errors",
    "format_exception_chain",
    # Exception classes
    "ErrorHandlingError",
    # Constants
    "PACKAGE_NAME",
    "PACKAGE_VERSION",
]
