# ALT Error Handling

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Advanced error handling utilities for Python applications, providing decorators and context managers for consistent and robust error management.

## Features

- 🎯 **Consistent Error Handling**: Decorators for standardized error handling across your application
- 🔄 **Exception Conversion**: Transform exceptions to match your application's error hierarchy
- 📝 **Contextual Information**: Add context to exceptions for better debugging
- 🛡️ **Safe Execution**: Execute functions with fallback values on error
- 🧹 **Cleanup Guarantees**: Ensure cleanup code runs even when errors occur
- 📊 **Error Aggregation**: Combine multiple errors into comprehensive error reports
- 🔗 **Exception Chain Formatting**: Format exception chains for logging

## Installation

```bash
pip install ALT-error-handling
```

For development:
```bash
git clone https://github.com/Avilir/ALT-error-handling.git
cd ALT-error-handling
pip install -e ".[dev]"
```

## Quick Start

### Basic Error Handling

```python
from alt_error_handling import handle_errors

@handle_errors(ValueError, TypeError, reraise=False, default_return=None)
def risky_function(data):
    # This function might raise ValueError or TypeError
    return process_data(data)

# If an error occurs, it will be logged and None will be returned
result = risky_function(invalid_data)
```

### Adding Context to Errors

```python
from alt_error_handling import error_context

def process_user_data(user_id, data):
    with error_context("processing user data", user_id=user_id, data_size=len(data)):
        # Any exception here will include the context information
        validate_data(data)
        transform_data(data)
        save_data(user_id, data)
```

## Core Features

### 1. Error Handling Decorator

The `handle_errors` decorator provides comprehensive error handling with logging:

```python
from alt_error_handling import handle_errors
import logging

# Set up logging
logger = logging.getLogger(__name__)

@handle_errors(
    IOError, 
    OSError,
    reraise=True,  # Re-raise after logging
    log_level=logging.ERROR,
    context="file operation",
    logger=logger
)
def read_config(path):
    with open(path) as f:
        return json.load(f)
```

### 2. Exception Conversion

Transform exceptions to match your application's error hierarchy:

```python
from alt_error_handling import convert_exceptions

class DataValidationError(Exception):
    """Application-specific validation error"""
    pass

@convert_exceptions({
    ValueError: DataValidationError,
    TypeError: lambda e: DataValidationError(f"Invalid type: {e}"),
    KeyError: lambda e: DataValidationError(f"Missing field: {e}")
})
def validate_user_input(data):
    if not isinstance(data, dict):
        raise TypeError("Data must be a dictionary")
    if "username" not in data:
        raise KeyError("username")
    if not data["username"]:
        raise ValueError("Username cannot be empty")
```

### 3. Safe Execution

Execute functions with fallback values:

```python
from alt_error_handling import safe_execute

# Parse JSON with fallback to empty dict
config = safe_execute(
    json.loads, 
    config_string, 
    default={},
    exceptions=(json.JSONDecodeError,)
)

# Calculate with fallback
result = safe_execute(
    lambda: x / y,
    default=float('inf'),
    exceptions=(ZeroDivisionError,)
)
```

### 4. Error Context Manager

Add debugging context to any code block:

```python
from alt_error_handling import error_context, ErrorHandlingError

class DatabaseError(ErrorHandlingError):
    """Custom database error with context support"""
    pass

def update_user(user_id, updates):
    with error_context(
        "updating user",
        DatabaseError,
        user_id=user_id,
        update_fields=list(updates.keys())
    ):
        user = db.get_user(user_id)
        user.update(updates)
        db.save(user)
```

### 5. Cleanup Guarantees

Ensure cleanup code runs even when errors occur:

```python
from alt_error_handling import ensure_cleanup

def cleanup_resources():
    close_connections()
    release_locks()
    clean_temp_files()

@ensure_cleanup(cleanup_resources)
def process_with_resources():
    acquire_locks()
    open_connections()
    # If this fails, cleanup_resources will still run
    do_processing()
```

### 6. Error Aggregation

Collect multiple errors for comprehensive error reporting:

```python
from alt_error_handling import aggregate_errors

errors = []
for item in items:
    try:
        process_item(item)
    except Exception as e:
        errors.append(e)

if errors:
    # Combine all errors into one comprehensive error
    raise aggregate_errors(
        errors,
        message="Failed to process items",
        exception_type=ProcessingError
    )
```

### 7. Exception Chain Formatting

Format exception chains for logging:

```python
from alt_error_handling import format_exception_chain

try:
    risky_operation()
except Exception as e:
    # Get a formatted string of the exception chain
    error_details = format_exception_chain(e, include_traceback=True)
    logger.error(f"Operation failed:\n{error_details}")
```

## Best Practices

### 1. Consistent Error Handling Strategy

```python
# Define application-specific errors
class AppError(ErrorHandlingError):
    """Base application error"""
    pass

class ValidationError(AppError):
    """Validation error"""
    pass

class ProcessingError(AppError):
    """Processing error"""
    pass

# Use consistent error handling throughout
@handle_errors(Exception, reraise=True, context="data processing")
@convert_exceptions({
    ValueError: ValidationError,
    TypeError: ValidationError,
    RuntimeError: ProcessingError
})
def process_data(data):
    validate(data)
    return transform(data)
```

### 2. Layered Error Handling

```python
# Low-level function with specific error handling
@handle_errors(IOError, OSError, reraise=False, default_return=None)
def read_file(path):
    with open(path) as f:
        return f.read()

# High-level function with broader error handling
@handle_errors(Exception, context="processing pipeline")
def process_files(file_paths):
    results = []
    for path in file_paths:
        with error_context("processing file", path=path):
            data = read_file(path)
            if data:
                results.append(transform_data(data))
    return results
```

### 3. Detailed Error Context

```python
@handle_errors(Exception, reraise=True)
def complex_operation(user_id, data, options):
    with error_context(
        "complex operation",
        user_id=user_id,
        data_size=len(data),
        options=options,
        timestamp=datetime.now().isoformat()
    ):
        # Multiple steps with individual context
        with error_context("validation step"):
            validate_input(data, options)
        
        with error_context("processing step"):
            result = process(data)
        
        with error_context("save step"):
            save_result(user_id, result)
        
        return result
```

## Advanced Usage

### Custom Logging Function

```python
def custom_error_logger(logger, error, context, details):
    # Send to monitoring service
    monitoring.send_error({
        'error_type': type(error).__name__,
        'error_message': str(error),
        'context': context,
        'function': details['function'],
        'timestamp': datetime.now().isoformat()
    })
    
    # Log locally
    logger.error(f"{context} failed: {error}")

@handle_errors(
    Exception,
    log_func=custom_error_logger,
    context="critical operation"
)
def critical_operation():
    # ...
```

### Conditional Error Handling

```python
def make_error_handler(debug_mode=False):
    return handle_errors(
        Exception,
        reraise=debug_mode,  # Reraise in debug mode
        default_return=None if not debug_mode else ...,
        log_level=logging.DEBUG if debug_mode else logging.ERROR
    )

# Use based on configuration
@make_error_handler(debug_mode=app.config.DEBUG)
def application_function():
    # ...
```

## Testing

The library includes comprehensive tests. Run them with:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=alt_error_handling

# Run specific test file
pytest tests/test_core.py
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/Avilir/ALT-error-handling.git
cd ALT-error-handling

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Quality Checks

```bash
# Type checking
mypy src

# Linting
ruff check .

# Formatting
black .

# All checks
make check  # If Makefile is available
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Avi Layani**  
Email: alayani@redhat.com

## Acknowledgments

- Inspired by error handling patterns in various Python frameworks
- Built with modern Python development best practices
- Type hints for better IDE support and code clarity
