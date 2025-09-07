"""
Core error handling utilities for consistent error management.

This module provides decorators and utilities for standardized error handling
in Python applications.
"""

import functools
import logging
import traceback
from contextlib import contextmanager
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)

T = TypeVar("T")


class ErrorHandlingError(Exception):
    """Base exception for error handling utilities."""

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize exception with message and optional context.

        Args:
            message: Error message
            context: Optional context information for debugging
        """
        super().__init__(message)
        self.context = context or {}


def handle_errors(
    *exception_types: Type[Exception],
    default_return: Optional[T] = None,
    reraise: bool = True,
    log_level: int = logging.ERROR,
    context: str = "operation",
    logger: Optional[logging.Logger] = None,
    log_func: Optional[Callable[[logging.Logger, Exception, str, Dict[str, Any]], None]] = None,
) -> Callable[[Callable[..., T]], Callable[..., Optional[T]]]:
    """
    Decorator for consistent error handling.

    Args:
        *exception_types: Exception types to catch
        default_return: Value to return on error (if not reraising)
        reraise: Whether to reraise the exception after logging
        log_level: Logging level for errors
        context: Context description for error messages
        logger: Logger instance to use (defaults to function's module logger)
        log_func: Custom logging function (defaults to standard logging)

    Returns:
        Decorated function

    Example:
        @handle_errors(FileNotFoundError, IOError, context="reading file")
        def read_file(path):
            return open(path).read()
    """

    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Optional[T]:
            # Get logger for the decorated function's module
            log = logger or logging.getLogger(func.__module__)

            try:
                return func(*args, **kwargs)
            except exception_types as e:
                # Get function context for better error messages
                func_context = f"{func.__module__}.{func.__name__}"

                # Log the error with context
                if log_func:
                    log_func(
                        log,
                        e,
                        context,
                        {
                            "function": func_context,
                            "func_args": args,
                            "func_kwargs": kwargs,
                        },
                    )
                else:
                    # Default logging
                    log.log(
                        log_level,
                        f"Error {context} in {func_context}: {e}",
                        exc_info=True,
                        extra={
                            "function": func_context,
                            "func_args": str(args),
                            "func_kwargs": str(kwargs),
                        },
                    )

                if reraise:
                    raise
                return default_return

        return wrapper

    return decorator


def convert_exceptions(
    mapping: Dict[Type[Exception], Union[Type[Exception], Callable[[Exception], Exception]]],
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to convert exceptions to different types.

    Args:
        mapping: Dictionary mapping source exception types to target types or converter functions

    Returns:
        Decorated function

    Example:
        @convert_exceptions({
            IOError: FileReadError,
            ValueError: lambda e: DataValidationError(f"Invalid data: {e}")
        })
        def process_file(path):
            # IOError will be converted to FileReadError
            # ValueError will be converted using the lambda
            pass
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except tuple(mapping.keys()) as e:
                for source_type, target in mapping.items():
                    if isinstance(e, source_type):
                        if callable(target) and not isinstance(target, type):
                            # It's a converter function
                            raise target(e) from e
                        elif isinstance(target, type):
                            # It's an exception class
                            raise target(str(e)) from e
                        else:
                            raise TypeError(f"Invalid mapping target: {target}") from None
                raise  # Should never reach here

        return wrapper

    return decorator


@contextmanager
def error_context(
    context: str,
    exception_type: Type[Exception] = ErrorHandlingError,
    **context_data: Any,
) -> Generator[None, None, None]:
    """
    Context manager for adding context to exceptions.

    Args:
        context: Description of the operation
        exception_type: Exception type to raise on error
        **context_data: Additional context data

    Example:
        with error_context("processing data", item_id=123):
            # Any exception here will be wrapped with context
            process_item()
    """
    try:
        yield
    except exception_type:
        # Already the right type, just reraise
        raise
    except Exception as e:
        # Wrap in the specified exception type with context
        # Check if exception supports context parameter
        if issubclass(exception_type, ErrorHandlingError):
            # ErrorHandlingError supports context parameter
            raise exception_type(f"Error during {context}: {e}", context=context_data) from e
        else:
            # Standard exception
            raise exception_type(f"Error during {context}: {e}") from e


def safe_execute(
    func: Callable[..., T],
    *args: Any,
    default: Optional[T] = None,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    logger: Optional[logging.Logger] = None,
    **kwargs: Any,
) -> Optional[T]:
    """
    Safely execute a function and return default on error.

    Args:
        func: Function to execute
        *args: Positional arguments for the function
        default: Default value to return on error
        exceptions: Exception types to catch
        logger: Logger to use (defaults to function's module logger)
        **kwargs: Keyword arguments for the function

    Returns:
        Function result or default value

    Example:
        result = safe_execute(parse_json, data, default={}, logger=logger)
    """
    log = logger or logging.getLogger(func.__module__)

    try:
        return func(*args, **kwargs)
    except exceptions as e:
        log.error(
            f"Error executing {func.__name__}: {e}",
            exc_info=True,
            extra={
                "function": f"{func.__module__}.{func.__name__}",
                "func_args": str(args),
                "func_kwargs": str(kwargs),
            },
        )
        return default


def ensure_cleanup(
    cleanup_func: Callable[[], None],
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to ensure cleanup function is called even on error.

    Args:
        cleanup_func: Function to call for cleanup
        exceptions: Exception types that trigger cleanup

    Returns:
        Decorated function

    Example:
        @ensure_cleanup(lambda: close_connections())
        def process_data():
            # cleanup_func will be called even if this raises
            pass
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except exceptions:
                cleanup_func()
                raise

        return wrapper

    return decorator


def aggregate_errors(
    errors: List[Exception],
    message: str = "Multiple errors occurred",
    exception_type: Type[Exception] = ErrorHandlingError,
) -> Exception:
    """
    Aggregate multiple errors into a single exception.

    Args:
        errors: List of exceptions to aggregate
        message: Overall error message
        exception_type: Type of exception to raise

    Returns:
        Single exception containing all error information
    """
    if not errors:
        raise ValueError("No errors to aggregate")

    if len(errors) == 1:
        return errors[0]

    error_details = []
    for i, error in enumerate(errors, 1):
        error_details.append(f"{i}. {type(error).__name__}: {error}")

    full_message = f"{message}:\n" + "\n".join(error_details)

    # Check if exception type supports context parameter
    if issubclass(exception_type, ErrorHandlingError):
        return exception_type(
            full_message,
            context={
                "error_count": len(errors),
                "error_types": [type(e).__name__ for e in errors],
                "errors": errors,
            },
        )
    else:
        # Standard exception
        return exception_type(full_message)


def format_exception_chain(e: Exception, include_traceback: bool = False) -> str:
    """
    Format an exception chain for logging.

    Args:
        e: Exception to format
        include_traceback: Whether to include full traceback

    Returns:
        Formatted exception string
    """
    parts: List[str] = []
    current: Optional[Exception] = e

    while current is not None:
        if include_traceback:
            # format_exception returns a list of strings, extend parts
            parts.extend(traceback.format_exception(type(current), current, current.__traceback__))
        else:
            parts.append(f"{type(current).__name__}: {current}")

        current = getattr(current, "__cause__", None)
        if current:
            parts.append("Caused by:")

    return "\n".join(parts)

