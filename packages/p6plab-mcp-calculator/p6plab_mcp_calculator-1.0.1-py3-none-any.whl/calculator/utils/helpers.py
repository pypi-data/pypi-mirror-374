"""
General utility functions for the Scientific Calculator MCP Server.

This module provides common mathematical utilities, input sanitization,
caching utilities, logging helpers, and configuration management.
"""

import os
import re
import time
import hashlib
import functools
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from decimal import Decimal, getcontext
import numpy as np
from functools import lru_cache
import logging


# Configuration management
def get_env_var(
    name: str,
    default: Any = None,
    var_type: type = str,
    required: bool = False
) -> Any:
    """
    Get environment variable with type conversion and validation.
    
    Args:
        name: Environment variable name
        default: Default value if not found
        var_type: Type to convert to
        required: Whether the variable is required
        
    Returns:
        Environment variable value
        
    Raises:
        ValueError: If required variable is missing or conversion fails
    """
    value = os.getenv(name)
    
    if value is None:
        if required:
            raise ValueError(f"Required environment variable '{name}' is not set")
        return default
    
    try:
        if var_type == bool:
            return value.lower() in ('true', '1', 'yes', 'on')
        elif var_type == int:
            return int(value)
        elif var_type == float:
            return float(value)
        elif var_type == list:
            return [item.strip() for item in value.split(',') if item.strip()]
        else:
            return var_type(value)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Cannot convert environment variable '{name}' to {var_type.__name__}: {e}")


def get_calculator_config() -> Dict[str, Any]:
    """
    Get calculator configuration from environment variables.
    
    Returns:
        Configuration dictionary
    """
    return {
        'precision': get_env_var('CALCULATOR_PRECISION', 15, int),
        'max_precision': get_env_var('CALCULATOR_MAX_PRECISION', 50, int),
        'min_precision': get_env_var('CALCULATOR_MIN_PRECISION', 1, int),
        'log_level': get_env_var('CALCULATOR_LOG_LEVEL', 'INFO', str),
        'log_file': get_env_var('CALCULATOR_LOG_FILE', None, str),
        'log_format': get_env_var('CALCULATOR_LOG_FORMAT', 'text', str),
        'cache_size': get_env_var('CALCULATOR_CACHE_SIZE', 1000, int),
        'memory_limit': get_env_var('CALCULATOR_MEMORY_LIMIT', 512, int),
        'timeout': get_env_var('CALCULATOR_TIMEOUT', 30, int),
        'debug': get_env_var('CALCULATOR_DEBUG', False, bool),
        'enable_currency': get_env_var('CALCULATOR_ENABLE_CURRENCY_CONVERSION', False, bool),
        'currency_api_key': get_env_var('CALCULATOR_CURRENCY_API_KEY', None, str),
        'currency_cache_hours': get_env_var('CALCULATOR_CURRENCY_CACHE_HOURS', 24, int),
    }


# Input sanitization and validation
def sanitize_input(value: Any) -> Any:
    """
    Sanitize input value for mathematical operations.
    
    Args:
        value: Input value to sanitize
        
    Returns:
        Sanitized value
    """
    if isinstance(value, str):
        # Remove extra whitespace
        value = value.strip()
        
        # Handle special mathematical constants
        value = value.replace('π', str(np.pi))
        value = value.replace('pi', str(np.pi))
        value = value.replace('e', str(np.e))
        
        # Try to convert to number
        try:
            if '.' in value or 'e' in value.lower():
                return float(value)
            else:
                return int(value)
        except ValueError:
            return value
    
    return value


def validate_numeric_input(
    value: Any,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    allow_complex: bool = False,
    allow_zero: bool = True,
    allow_negative: bool = True
) -> Union[float, complex]:
    """
    Validate and convert numeric input.
    
    Args:
        value: Input value
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        allow_complex: Whether complex numbers are allowed
        allow_zero: Whether zero is allowed
        allow_negative: Whether negative numbers are allowed
        
    Returns:
        Validated numeric value
        
    Raises:
        ValueError: If validation fails
    """
    # Handle string representations of complex numbers
    if isinstance(value, str):
        value = value.strip()
        if 'j' in value or 'i' in value:
            if not allow_complex:
                raise ValueError("Complex numbers are not allowed for this operation")
            # Convert 'i' to 'j' for Python complex parsing
            value = value.replace('i', 'j')
            try:
                return complex(value)
            except ValueError:
                raise ValueError(f"Invalid complex number format: {value}")
    
    # Convert to appropriate numeric type
    try:
        if isinstance(value, complex):
            if not allow_complex:
                raise ValueError("Complex numbers are not allowed for this operation")
            numeric_value = value
        else:
            numeric_value = float(value)
    except (ValueError, TypeError):
        raise ValueError(f"Cannot convert '{value}' to a number")
    
    # Validate real part constraints
    real_part = numeric_value.real if isinstance(numeric_value, complex) else numeric_value
    
    if not allow_zero and real_part == 0:
        raise ValueError("Zero is not allowed for this operation")
    
    if not allow_negative and real_part < 0:
        raise ValueError("Negative numbers are not allowed for this operation")
    
    if min_value is not None and real_part < min_value:
        raise ValueError(f"Value must be at least {min_value}")
    
    if max_value is not None and real_part > max_value:
        raise ValueError(f"Value must be at most {max_value}")
    
    return numeric_value


def validate_matrix_input(matrix: Any) -> np.ndarray:
    """
    Validate and convert matrix input.
    
    Args:
        matrix: Input matrix
        
    Returns:
        Validated numpy array
        
    Raises:
        ValueError: If validation fails
    """
    if not isinstance(matrix, (list, np.ndarray)):
        raise ValueError("Matrix must be a list or numpy array")
    
    try:
        np_matrix = np.array(matrix, dtype=float)
    except (ValueError, TypeError):
        raise ValueError("Matrix must contain only numeric values")
    
    if np_matrix.size == 0:
        raise ValueError("Matrix cannot be empty")
    
    if np_matrix.ndim != 2:
        raise ValueError("Matrix must be 2-dimensional")
    
    return np_matrix


def validate_vector_input(vector: Any) -> np.ndarray:
    """
    Validate and convert vector input.
    
    Args:
        vector: Input vector
        
    Returns:
        Validated numpy array
        
    Raises:
        ValueError: If validation fails
    """
    if not isinstance(vector, (list, np.ndarray)):
        raise ValueError("Vector must be a list or numpy array")
    
    try:
        np_vector = np.array(vector, dtype=float)
    except (ValueError, TypeError):
        raise ValueError("Vector must contain only numeric values")
    
    if np_vector.size == 0:
        raise ValueError("Vector cannot be empty")
    
    if np_vector.ndim != 1:
        raise ValueError("Vector must be 1-dimensional")
    
    return np_vector


# Mathematical utility functions
def is_close(a: float, b: float, tolerance: float = 1e-10) -> bool:
    """
    Check if two numbers are close within tolerance.
    
    Args:
        a: First number
        b: Second number
        tolerance: Tolerance for comparison
        
    Returns:
        True if numbers are close
    """
    return abs(a - b) < tolerance


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default on division by zero.
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value for division by zero
        
    Returns:
        Division result or default
    """
    if abs(denominator) < 1e-15:
        return default
    return numerator / denominator


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Clamp value between minimum and maximum.
    
    Args:
        value: Value to clamp
        min_value: Minimum value
        max_value: Maximum value
        
    Returns:
        Clamped value
    """
    return max(min_value, min(value, max_value))


def normalize_angle(angle: float, unit: str = "radians") -> float:
    """
    Normalize angle to standard range.
    
    Args:
        angle: Angle to normalize
        unit: "radians" or "degrees"
        
    Returns:
        Normalized angle
    """
    if unit == "degrees":
        return angle % 360
    else:
        return angle % (2 * np.pi)


def degrees_to_radians(degrees: float) -> float:
    """Convert degrees to radians."""
    return degrees * np.pi / 180


def radians_to_degrees(radians: float) -> float:
    """Convert radians to degrees."""
    return radians * 180 / np.pi


def factorial(n: int) -> int:
    """
    Calculate factorial of a number.
    
    Args:
        n: Non-negative integer
        
    Returns:
        Factorial of n
        
    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def gcd(a: int, b: int) -> int:
    """
    Calculate greatest common divisor using Euclidean algorithm.
    
    Args:
        a: First integer
        b: Second integer
        
    Returns:
        Greatest common divisor
    """
    while b:
        a, b = b, a % b
    return abs(a)


def lcm(a: int, b: int) -> int:
    """
    Calculate least common multiple.
    
    Args:
        a: First integer
        b: Second integer
        
    Returns:
        Least common multiple
    """
    return abs(a * b) // gcd(a, b) if a and b else 0


# Caching utilities
class TimedCache:
    """Simple timed cache implementation."""
    
    def __init__(self, ttl: int = 3600):
        """
        Initialize timed cache.
        
        Args:
            ttl: Time to live in seconds
        """
        self.ttl = ttl
        self.cache = {}
        self.timestamps = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key in self.cache:
            if time.time() - self.timestamps[key] < self.ttl:
                return self.cache[key]
            else:
                # Remove expired entry
                del self.cache[key]
                del self.timestamps[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        self.cache[key] = value
        self.timestamps[key] = time.time()
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        self.timestamps.clear()


def cache_key(*args, **kwargs) -> str:
    """
    Generate cache key from arguments.
    
    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Cache key string
    """
    key_parts = []
    
    for arg in args:
        if isinstance(arg, (list, tuple)):
            key_parts.append(str(tuple(arg)))
        elif isinstance(arg, dict):
            key_parts.append(str(sorted(arg.items())))
        else:
            key_parts.append(str(arg))
    
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}={v}")
    
    key_string = "|".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def memoize_with_ttl(ttl: int = 3600):
    """
    Decorator for memoizing function results with TTL.
    
    Args:
        ttl: Time to live in seconds
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        cache = TimedCache(ttl)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = cache_key(*args, **kwargs)
            result = cache.get(key)
            
            if result is None:
                result = func(*args, **kwargs)
                cache.set(key, result)
            
            return result
        
        wrapper.cache_clear = cache.clear
        return wrapper
    
    return decorator


# Performance monitoring
class PerformanceTimer:
    """Context manager for timing operations."""
    
    def __init__(self, operation_name: str = "operation"):
        """
        Initialize performance timer.
        
        Args:
            operation_name: Name of the operation being timed
        """
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        """Start timing."""
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and log result."""
        self.end_time = time.perf_counter()
        duration = self.end_time - self.start_time
        
        logger = logging.getLogger(__name__)
        logger.debug(f"{self.operation_name} completed in {duration:.4f} seconds")
    
    @property
    def duration(self) -> Optional[float]:
        """Get operation duration."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


def timeout_handler(timeout_seconds: int):
    """
    Decorator to add timeout to function execution.
    
    Args:
        timeout_seconds: Timeout in seconds
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import signal
            
            def timeout_signal_handler(signum, frame):
                raise TimeoutError(f"Function '{func.__name__}' timed out after {timeout_seconds} seconds")
            
            # Set up timeout signal
            old_handler = signal.signal(signal.SIGALRM, timeout_signal_handler)
            signal.alarm(timeout_seconds)
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # Restore old signal handler
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
        
        return wrapper
    return decorator


# Logging helpers
def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: str = "text"
) -> logging.Logger:
    """
    Set up logging configuration.
    
    Args:
        level: Logging level
        log_file: Optional log file path
        log_format: "text" or "json"
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger("calculator")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    if log_format == "json":
        import json
        
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    "timestamp": self.formatTime(record),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno
                }
                
                if record.exc_info:
                    log_entry["exception"] = self.formatException(record.exc_info)
                
                return json.dumps(log_entry)
        
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# String utilities
def parse_expression(expression: str) -> str:
    """
    Parse and clean mathematical expression.
    
    Args:
        expression: Mathematical expression string
        
    Returns:
        Cleaned expression
    """
    # Remove extra whitespace
    expression = re.sub(r'\s+', '', expression)
    
    # Replace common mathematical symbols
    replacements = {
        '×': '*',
        '÷': '/',
        '²': '**2',
        '³': '**3',
        '√': 'sqrt',
        'π': 'pi',
        '∞': 'inf'
    }
    
    for old, new in replacements.items():
        expression = expression.replace(old, new)
    
    return expression


def extract_variables(expression: str) -> List[str]:
    """
    Extract variable names from mathematical expression.
    
    Args:
        expression: Mathematical expression
        
    Returns:
        List of variable names
    """
    # Find all alphabetic sequences that aren't function names
    function_names = {
        'sin', 'cos', 'tan', 'sec', 'csc', 'cot',
        'arcsin', 'arccos', 'arctan', 'sinh', 'cosh', 'tanh',
        'log', 'ln', 'exp', 'sqrt', 'abs', 'pi', 'e'
    }
    
    variables = set()
    tokens = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', expression)
    
    for token in tokens:
        if token.lower() not in function_names:
            variables.add(token)
    
    return sorted(list(variables))


# Data structure utilities
def flatten_list(nested_list: List[Any]) -> List[Any]:
    """
    Flatten nested list structure.
    
    Args:
        nested_list: Nested list
        
    Returns:
        Flattened list
    """
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split list into chunks of specified size.
    
    Args:
        lst: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def remove_outliers(data: List[float], method: str = "iqr", factor: float = 1.5) -> List[float]:
    """
    Remove outliers from data using specified method.
    
    Args:
        data: Input data
        method: "iqr" or "zscore"
        factor: Outlier factor
        
    Returns:
        Data with outliers removed
    """
    if not data:
        return data
    
    data_array = np.array(data)
    
    if method == "iqr":
        q1 = np.percentile(data_array, 25)
        q3 = np.percentile(data_array, 75)
        iqr = q3 - q1
        lower_bound = q1 - factor * iqr
        upper_bound = q3 + factor * iqr
        
        mask = (data_array >= lower_bound) & (data_array <= upper_bound)
        return data_array[mask].tolist()
    
    elif method == "zscore":
        mean = np.mean(data_array)
        std = np.std(data_array)
        z_scores = np.abs((data_array - mean) / std)
        
        mask = z_scores < factor
        return data_array[mask].tolist()
    
    else:
        raise ValueError(f"Unknown outlier removal method: {method}")


# Memory management
def get_memory_usage() -> Dict[str, float]:
    """
    Get current memory usage information.
    
    Returns:
        Memory usage dictionary
    """
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    return {
        "rss": memory_info.rss / 1024 / 1024,  # MB
        "vms": memory_info.vms / 1024 / 1024,  # MB
        "percent": process.memory_percent(),
        "available": psutil.virtual_memory().available / 1024 / 1024  # MB
    }


def check_memory_limit(limit_mb: int = 512) -> bool:
    """
    Check if memory usage exceeds limit.
    
    Args:
        limit_mb: Memory limit in MB
        
    Returns:
        True if within limit
    """
    try:
        memory_usage = get_memory_usage()
        return memory_usage["rss"] < limit_mb
    except ImportError:
        # psutil not available, assume OK
        return True