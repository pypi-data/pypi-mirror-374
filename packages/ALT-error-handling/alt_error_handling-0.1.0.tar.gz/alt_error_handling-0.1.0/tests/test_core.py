"""
Test module for alt_error_handling.core functionality.

This module contains comprehensive tests for all error handling utilities
provided by the alt_error_handling package.
"""

import logging
from typing import Any, Dict, List
from unittest.mock import Mock

import pytest

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


class TestErrorHandlingError:
    """Tests for the ErrorHandlingError base exception."""

    def test_init_with_message_only(self) -> None:
        """Test exception initialization with message only."""
        error = ErrorHandlingError("Test error")
        assert str(error) == "Test error"
        assert error.context == {}

    def test_init_with_context(self) -> None:
        """Test exception initialization with message and context."""
        context = {"key": "value", "code": 404}
        error = ErrorHandlingError("Test error", context)
        assert str(error) == "Test error"
        assert error.context == context


class TestHandleErrors:
    """Tests for the handle_errors decorator."""

    def test_decorator_no_error(self) -> None:
        """Test decorator when no error occurs."""

        @handle_errors(ValueError, reraise=False)
        def test_func(x: int) -> int:
            return x * 2

        result = test_func(5)  # type: ignore[misc]
        assert result == 10

    def test_decorator_catches_specific_error(self) -> None:
        """Test decorator catches only specified error types."""

        @handle_errors(ValueError, reraise=False, default_return=-1)
        def test_func(x: int) -> int:
            if x < 0:
                raise ValueError("Negative value")
            if x > 100:
                raise RuntimeError("Too large")
            return x * 2

        # Should catch ValueError
        assert test_func(-5) == -1  # type: ignore[misc]

        # Should not catch RuntimeError
        with pytest.raises(RuntimeError):
            test_func(150)  # type: ignore[misc]

    def test_decorator_reraises_error(self) -> None:
        """Test decorator reraises error when configured."""

        @handle_errors(ValueError, reraise=True)
        def test_func(x: int) -> int:  # noqa: ARG001
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            test_func(5)  # type: ignore[misc]

    def test_decorator_with_custom_logger(self) -> None:
        """Test decorator with custom logger."""
        mock_logger = Mock(spec=logging.Logger)

        @handle_errors(ValueError, reraise=False, logger=mock_logger, log_level=logging.WARNING)
        def test_func() -> None:
            raise ValueError("Test error")

        test_func()  # type: ignore[misc]
        mock_logger.log.assert_called_once()
        call_args = mock_logger.log.call_args
        assert call_args[0][0] == logging.WARNING
        assert "Test error" in call_args[0][1]

    def test_decorator_with_custom_log_func(self) -> None:
        """Test decorator with custom logging function."""
        log_calls: List[Dict[str, Any]] = []

        def custom_log(
            logger: logging.Logger,
            error: Exception,
            context: str,
            details: dict,
        ) -> None:
            log_calls.append(
                {
                    "logger": logger,
                    "error": str(error),
                    "context": context,
                    "details": details,
                }
            )

        @handle_errors(
            ValueError,
            reraise=False,
            context="custom operation",
            log_func=custom_log,
        )
        def test_func(x: int, y: int = 2) -> int:  # noqa: ARG001
            raise ValueError("Custom error")

        test_func(1, y=3)  # type: ignore[misc]
        assert len(log_calls) == 1
        assert log_calls[0]["error"] == "Custom error"
        assert log_calls[0]["context"] == "custom operation"
        assert log_calls[0]["details"]["func_args"] == (1,)
        assert log_calls[0]["details"]["func_kwargs"] == {"y": 3}

    def test_decorator_multiple_exception_types(self) -> None:
        """Test decorator with multiple exception types."""

        @handle_errors(ValueError, TypeError, IOError, reraise=False, default_return=0)
        def test_func(error_type: str) -> int:
            if error_type == "value":
                raise ValueError("Value error")
            elif error_type == "type":
                raise TypeError("Type error")
            elif error_type == "io":
                raise OSError("IO error")
            elif error_type == "runtime":
                raise RuntimeError("Runtime error")
            return 42

        assert test_func("value") == 0  # type: ignore[misc]
        assert test_func("type") == 0  # type: ignore[misc]
        assert test_func("io") == 0  # type: ignore[misc]
        assert test_func("ok") == 42  # type: ignore[misc]

        with pytest.raises(RuntimeError):
            test_func("runtime")  # type: ignore[misc]


class TestConvertExceptions:
    """Tests for the convert_exceptions decorator."""

    def test_convert_to_exception_class(self) -> None:
        """Test converting exception to another exception class."""

        class CustomError(Exception):
            pass

        @convert_exceptions({ValueError: CustomError})
        def test_func(x: int) -> int:
            if x < 0:
                raise ValueError("Negative value")
            return x

        # Normal case
        assert test_func(5) == 5

        # Conversion case
        with pytest.raises(CustomError) as exc_info:
            test_func(-1)
        assert str(exc_info.value) == "Negative value"
        assert isinstance(exc_info.value.__cause__, ValueError)

    def test_convert_with_function(self) -> None:
        """Test converting exception using a converter function."""

        class DataError(Exception):
            def __init__(self, message: str, code: int) -> None:
                super().__init__(message)
                self.code = code

        @convert_exceptions(
            {
                ValueError: lambda e: DataError(f"Data error: {e}", 400),
                TypeError: lambda e: DataError(f"Type error: {e}", 422),
            }
        )
        def test_func(error_type: str) -> str:
            if error_type == "value":
                raise ValueError("Invalid value")
            elif error_type == "type":
                raise TypeError("Wrong type")
            return "success"

        # Normal case
        assert test_func("ok") == "success"

        # ValueError conversion
        with pytest.raises(DataError) as exc_info:
            test_func("value")
        assert str(exc_info.value) == "Data error: Invalid value"
        assert exc_info.value.code == 400

        # TypeError conversion
        with pytest.raises(DataError) as exc_info:
            test_func("type")
        assert str(exc_info.value) == "Type error: Wrong type"
        assert exc_info.value.code == 422

    def test_convert_unhandled_exception(self) -> None:
        """Test that unhandled exceptions pass through."""

        @convert_exceptions({ValueError: RuntimeError})
        def test_func() -> None:
            raise TypeError("Not handled")

        with pytest.raises(TypeError, match="Not handled"):
            test_func()

    def test_convert_invalid_mapping(self) -> None:
        """Test handling of invalid mapping targets."""

        @convert_exceptions({ValueError: "not_callable_or_type"})  # type: ignore
        def test_func() -> None:
            raise ValueError("Test")

        with pytest.raises(TypeError, match="Invalid mapping target"):
            test_func()


class TestErrorContext:
    """Tests for the error_context context manager."""

    def test_context_manager_no_error(self) -> None:
        """Test context manager when no error occurs."""
        with error_context("test operation"):
            result = 1 + 1
        assert result == 2

    def test_context_manager_wraps_exception(self) -> None:
        """Test context manager wraps exceptions with context."""
        with pytest.raises(ErrorHandlingError) as exc_info:  # noqa: SIM117
            with error_context("database operation", user_id=123):
                raise ValueError("Connection failed")

        assert "Error during database operation" in str(exc_info.value)
        assert "Connection failed" in str(exc_info.value)
        assert exc_info.value.context["user_id"] == 123
        assert isinstance(exc_info.value.__cause__, ValueError)

    def test_context_manager_custom_exception(self) -> None:
        """Test context manager with custom exception type."""

        class DatabaseError(Exception):
            pass

        with pytest.raises(DatabaseError) as exc_info:  # noqa: SIM117
            with error_context("query execution", DatabaseError):
                raise ValueError("SQL error")

        assert "Error during query execution" in str(exc_info.value)
        assert isinstance(exc_info.value.__cause__, ValueError)

    def test_context_manager_preserves_same_type(self) -> None:
        """Test context manager preserves exception if already correct type."""
        with pytest.raises(ErrorHandlingError) as exc_info:  # noqa: SIM117
            with error_context("operation", ErrorHandlingError):
                raise ErrorHandlingError("Original error", {"key": "value"})

        # Should reraise the original without wrapping
        assert str(exc_info.value) == "Original error"
        assert exc_info.value.context == {"key": "value"}
        assert exc_info.value.__cause__ is None


class TestSafeExecute:
    """Tests for the safe_execute function."""

    def test_safe_execute_success(self) -> None:
        """Test safe_execute with successful execution."""

        def add(x: int, y: int) -> int:
            return x + y

        result = safe_execute(add, 2, 3)
        assert result == 5

    def test_safe_execute_with_error(self) -> None:
        """Test safe_execute with error and default value."""

        def divide(x: int, y: int) -> float:
            return x / y

        result = safe_execute(divide, 10, 0, default=-1.0)
        assert result == -1.0

    def test_safe_execute_specific_exceptions(self) -> None:
        """Test safe_execute catches only specified exceptions."""

        def risky_func(error_type: str) -> str:
            if error_type == "value":
                raise ValueError("Value error")
            elif error_type == "runtime":
                raise RuntimeError("Runtime error")
            return "success"

        # Catch ValueError only
        result = safe_execute(
            risky_func,
            "value",
            default="caught",
            exceptions=(ValueError,),
        )
        assert result == "caught"

        # RuntimeError not caught when only ValueError is specified
        with pytest.raises(RuntimeError):
            safe_execute(
                risky_func,
                "runtime",
                default="caught",
                exceptions=(ValueError,),
            )

    def test_safe_execute_with_kwargs(self) -> None:
        """Test safe_execute with keyword arguments."""

        def greet(name: str, prefix: str = "Hello") -> str:
            if not name:
                raise ValueError("Name required")
            return f"{prefix}, {name}!"

        result = safe_execute(greet, "World", prefix="Hi")
        assert result == "Hi, World!"

        result = safe_execute(greet, "", default="No greeting")
        assert result == "No greeting"

    def test_safe_execute_with_logger(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test safe_execute with logging."""

        def failing_func() -> str:  # Changed return type to match default
            raise ValueError("Test error")

        # Use caplog to capture logs
        with caplog.at_level(logging.ERROR):
            result = safe_execute(failing_func, default="failed")

        assert result == "failed"
        assert "Error executing failing_func" in caplog.text
        assert "Test error" in caplog.text


class TestEnsureCleanup:
    """Tests for the ensure_cleanup decorator."""

    def test_cleanup_on_success(self) -> None:
        """Test cleanup is NOT called on successful execution."""
        cleanup_called = False

        def cleanup() -> None:
            nonlocal cleanup_called
            cleanup_called = True

        @ensure_cleanup(cleanup)
        def test_func() -> str:
            return "success"

        result = test_func()
        assert result == "success"
        assert not cleanup_called

    def test_cleanup_on_error(self) -> None:
        """Test cleanup IS called on error."""
        cleanup_called = False

        def cleanup() -> None:
            nonlocal cleanup_called
            cleanup_called = True

        @ensure_cleanup(cleanup)
        def test_func() -> None:
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            test_func()

        assert cleanup_called

    def test_cleanup_specific_exceptions(self) -> None:
        """Test cleanup only for specific exception types."""
        cleanup_count = 0

        def cleanup() -> None:
            nonlocal cleanup_count
            cleanup_count += 1

        @ensure_cleanup(cleanup, exceptions=(ValueError,))
        def test_func(error_type: str) -> None:
            if error_type == "value":
                raise ValueError("Value error")
            elif error_type == "type":
                raise TypeError("Type error")

        # Cleanup called for ValueError
        with pytest.raises(ValueError):
            test_func("value")
        assert cleanup_count == 1

        # Cleanup NOT called for TypeError
        with pytest.raises(TypeError):
            test_func("type")
        assert cleanup_count == 1  # Still 1, not incremented

    def test_cleanup_preserves_exception(self) -> None:
        """Test that original exception is preserved after cleanup."""

        def cleanup() -> None:
            pass  # Just needs to run

        @ensure_cleanup(cleanup)
        def test_func() -> None:
            raise ValueError("Original error")

        with pytest.raises(ValueError) as exc_info:
            test_func()

        assert str(exc_info.value) == "Original error"


class TestAggregateErrors:
    """Tests for the aggregate_errors function."""

    def test_aggregate_empty_list(self) -> None:
        """Test aggregating empty error list raises ValueError."""
        with pytest.raises(ValueError, match="No errors to aggregate"):
            aggregate_errors([])

    def test_aggregate_single_error(self) -> None:
        """Test aggregating single error returns it unchanged."""
        error = ValueError("Single error")
        result = aggregate_errors([error])
        assert result is error

    def test_aggregate_multiple_errors(self) -> None:
        """Test aggregating multiple errors."""
        errors: List[Exception] = [
            ValueError("First error"),
            TypeError("Second error"),
            RuntimeError("Third error"),
        ]

        result = aggregate_errors(errors)
        assert isinstance(result, ErrorHandlingError)
        assert "Multiple errors occurred" in str(result)
        assert "1. ValueError: First error" in str(result)
        assert "2. TypeError: Second error" in str(result)
        assert "3. RuntimeError: Third error" in str(result)
        assert result.context["error_count"] == 3
        assert result.context["error_types"] == ["ValueError", "TypeError", "RuntimeError"]

    def test_aggregate_custom_message(self) -> None:
        """Test aggregating with custom message."""
        errors = [ValueError("Error 1"), ValueError("Error 2")]

        result = aggregate_errors(errors, message="Validation failed")
        assert isinstance(result, ErrorHandlingError)
        assert "Validation failed" in str(result)

    def test_aggregate_custom_exception_type(self) -> None:
        """Test aggregating with custom exception type."""

        class ValidationError(Exception):
            pass

        errors: List[Exception] = [ValueError("Error 1"), TypeError("Error 2")]

        result = aggregate_errors(errors, message="Custom", exception_type=ValidationError)
        assert isinstance(result, ValidationError)
        assert "Custom" in str(result)


class TestFormatExceptionChain:
    """Tests for the format_exception_chain function."""

    def test_format_single_exception(self) -> None:
        """Test formatting single exception without traceback."""
        error = ValueError("Test error")
        result = format_exception_chain(error)
        assert result == "ValueError: Test error"

    def test_format_chained_exceptions(self) -> None:
        """Test formatting chained exceptions."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise RuntimeError("Wrapper error") from e
        except RuntimeError as e:
            result = format_exception_chain(e)

        assert "RuntimeError: Wrapper error" in result
        assert "Caused by:" in result
        assert "ValueError: Original error" in result

    def test_format_with_traceback(self) -> None:
        """Test formatting with full traceback."""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            result = format_exception_chain(e, include_traceback=True)

        assert "Traceback" in result
        assert "ValueError: Test error" in result
        assert __file__ in result  # Should include this file in traceback

    def test_format_no_cause(self) -> None:
        """Test formatting exception with no cause."""
        error = RuntimeError("Standalone error")
        result = format_exception_chain(error)
        assert result == "RuntimeError: Standalone error"
        assert "Caused by:" not in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
