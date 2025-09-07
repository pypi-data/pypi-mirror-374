"""Basic arithmetic operations with high precision."""

import math
import os
from decimal import Decimal, InvalidOperation, getcontext
from typing import Any, Dict, Union

from calculator.models.errors import (
    ComputationError,
    PrecisionError,
    ValidationError,
)

# Set precision from environment variable
PRECISION = int(os.getenv("CALCULATOR_PRECISION", "15"))
getcontext().prec = PRECISION + 5  # Extra precision for intermediate calculations


def _to_decimal(value: Union[int, float, str, Decimal]) -> Decimal:
    """Convert value to Decimal with error handling."""
    try:
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValidationError(
            f"Invalid numeric value: {value}",
            suggestions=[
                "Ensure the value is a valid number",
                "Check for special characters or invalid formats",
            ],
        )


def _validate_finite(value: Union[int, float], name: str = "value") -> None:
    """Validate that a value is finite."""
    if not math.isfinite(value):
        raise ValidationError(
            f"{name} must be finite (not infinity or NaN): {value}",
            field=name,
            value=value,
            suggestions=[
                "Ensure input values are finite numbers",
                "Check for division by zero or overflow conditions",
            ],
        )


def add(a: Union[int, float], b: Union[int, float]) -> Dict[str, Any]:
    """Add two numbers with high precision.

    Args:
        a: First number
        b: Second number

    Returns:
        Dict containing the sum and metadata.

    Raises:
        ValidationError: If inputs are invalid
        ComputationError: If computation fails
    """
    try:
        # Use Decimal for high precision (handles string conversion)
        decimal_a = _to_decimal(a)
        decimal_b = _to_decimal(b)
        
        # Validate after conversion
        _validate_finite(float(decimal_a), "a")
        _validate_finite(float(decimal_b), "b")

        result = decimal_a + decimal_b

        # Convert back to float for JSON serialization
        float_result = float(result)
        _validate_finite(float_result, "result")

        return {
            "result": float_result,
            "operation": "addition",
            "inputs": {"a": a, "b": b},
            "precision": PRECISION,
            "formula": f"{a} + {b}",
            "decimal_result": str(result),
            "success": True,
        }

    except (ValidationError, PrecisionError):
        raise
    except Exception as e:
        raise ComputationError(
            f"Addition failed: {str(e)}", operation="addition", inputs={"a": a, "b": b}
        )


def subtract(a: Union[int, float], b: Union[int, float]) -> Dict[str, Any]:
    """Subtract two numbers with high precision.

    Args:
        a: First number (minuend)
        b: Second number (subtrahend)

    Returns:
        Dict containing the difference and metadata.
    """
    try:
        # Use Decimal for high precision (handles string conversion)
        decimal_a = _to_decimal(a)
        decimal_b = _to_decimal(b)
        
        # Validate after conversion
        _validate_finite(float(decimal_a), "a")
        _validate_finite(float(decimal_b), "b")

        result = decimal_a - decimal_b
        float_result = float(result)
        _validate_finite(float_result, "result")

        return {
            "result": float_result,
            "operation": "subtraction",
            "inputs": {"a": a, "b": b},
            "precision": PRECISION,
            "formula": f"{a} - {b}",
            "decimal_result": str(result),
            "success": True,
        }

    except (ValidationError, PrecisionError):
        raise
    except Exception as e:
        raise ComputationError(
            f"Subtraction failed: {str(e)}", operation="subtraction", inputs={"a": a, "b": b}
        )


def multiply(a: Union[int, float], b: Union[int, float]) -> Dict[str, Any]:
    """Multiply two numbers with high precision.

    Args:
        a: First number
        b: Second number

    Returns:
        Dict containing the product and metadata.
    """
    try:
        # Use Decimal for high precision (handles string conversion)
        decimal_a = _to_decimal(a)
        decimal_b = _to_decimal(b)
        
        # Validate after conversion
        _validate_finite(float(decimal_a), "a")
        _validate_finite(float(decimal_b), "b")

        result = decimal_a * decimal_b
        float_result = float(result)
        _validate_finite(float_result, "result")

        return {
            "result": float_result,
            "operation": "multiplication",
            "inputs": {"a": a, "b": b},
            "precision": PRECISION,
            "formula": f"{a} × {b}",
            "decimal_result": str(result),
            "success": True,
        }

    except (ValidationError, PrecisionError):
        raise
    except Exception as e:
        raise ComputationError(
            f"Multiplication failed: {str(e)}", operation="multiplication", inputs={"a": a, "b": b}
        )


def divide(a: Union[int, float], b: Union[int, float]) -> Dict[str, Any]:
    """Divide two numbers with high precision.

    Args:
        a: Dividend
        b: Divisor

    Returns:
        Dict containing the quotient and metadata.

    Raises:
        ValidationError: If divisor is zero
    """
    try:
        # Use Decimal for high precision (handles string conversion)
        decimal_a = _to_decimal(a)
        decimal_b = _to_decimal(b)
        
        # Validate after conversion
        _validate_finite(float(decimal_a), "a")
        _validate_finite(float(decimal_b), "b")

        if float(decimal_b) == 0:
            raise ValidationError(
                "Division by zero is not allowed",
                field="b",
                value=b,
                suggestions=[
                    "Ensure the divisor is not zero",
                    "Check for edge cases in your calculations",
                ],
            )

        result = decimal_a / decimal_b
        float_result = float(result)
        _validate_finite(float_result, "result")

        return {
            "result": float_result,
            "operation": "division",
            "inputs": {"a": a, "b": b},
            "precision": PRECISION,
            "formula": f"{a} ÷ {b}",
            "decimal_result": str(result),
            "success": True,
        }

    except (ValidationError, PrecisionError):
        raise
    except Exception as e:
        raise ComputationError(
            f"Division failed: {str(e)}", operation="division", inputs={"a": a, "b": b}
        )


def power(base: Union[int, float], exponent: Union[int, float]) -> Dict[str, Any]:
    """Calculate base raised to the power of exponent.

    Args:
        base: Base number
        exponent: Exponent

    Returns:
        Dict containing the result and metadata.
    """
    try:
        # Use Decimal for high precision (handles string conversion)
        decimal_base = _to_decimal(base)
        decimal_exponent = _to_decimal(exponent)
        
        # Validate after conversion
        _validate_finite(float(decimal_base), "base")
        _validate_finite(float(decimal_exponent), "exponent")

        # Handle special cases
        if float(decimal_base) == 0 and float(decimal_exponent) < 0:
            raise ValidationError(
                "Cannot raise zero to a negative power",
                suggestions=[
                    "Ensure base is not zero when exponent is negative",
                    "Check for mathematical validity of the operation",
                ],
            )

        if float(decimal_base) < 0 and not isinstance(float(decimal_exponent), int) and float(decimal_exponent) != int(float(decimal_exponent)):
            raise ValidationError(
                "Cannot raise negative number to non-integer power (would result in complex number)",
                suggestions=[
                    "Use positive base for non-integer exponents",
                    "Use complex number operations for negative bases with non-integer exponents",
                ],
            )

        # Use Python's built-in power for better handling of edge cases
        result = float(decimal_base)**float(decimal_exponent)
        _validate_finite(result, "result")

        return {
            "result": result,
            "operation": "exponentiation",
            "inputs": {"base": base, "exponent": exponent},
            "precision": PRECISION,
            "formula": f"{base}^{exponent}",
            "success": True,
        }

    except (ValidationError, PrecisionError):
        raise
    except Exception as e:
        raise ComputationError(
            f"Power operation failed: {str(e)}",
            operation="exponentiation",
            inputs={"base": base, "exponent": exponent},
        )


def square_root(value: Union[int, float]) -> Dict[str, Any]:
    """Calculate the principal square root of a number.

    Args:
        value: Number to find square root of

    Returns:
        Dict containing the square root and metadata.
    """
    try:
        # Use Decimal for high precision (handles string conversion)
        decimal_value = _to_decimal(value)
        
        # Validate after conversion
        _validate_finite(float(decimal_value), "value")

        if float(decimal_value) < 0:
            raise ValidationError(
                "Cannot calculate square root of negative number (would result in complex number)",
                field="value",
                value=value,
                suggestions=[
                    "Use positive numbers for real square roots",
                    "Use complex number operations for negative values",
                ],
            )

        result = math.sqrt(float(decimal_value))
        _validate_finite(result, "result")

        return {
            "result": result,
            "operation": "square_root",
            "inputs": {"value": value},
            "precision": PRECISION,
            "formula": f"√{value}",
            "success": True,
        }

    except (ValidationError, PrecisionError):
        raise
    except Exception as e:
        raise ComputationError(
            f"Square root calculation failed: {str(e)}",
            operation="square_root",
            inputs={"value": value},
        )


def modulo(a: Union[int, float], b: Union[int, float]) -> Dict[str, Any]:
    """Calculate the remainder of division (modular arithmetic).

    Args:
        a: Dividend
        b: Divisor

    Returns:
        Dict containing the remainder and metadata.
    """
    try:
        _validate_finite(a, "a")
        _validate_finite(b, "b")

        if b == 0:
            raise ValidationError(
                "Modulo by zero is not allowed",
                field="b",
                value=b,
                suggestions=[
                    "Ensure the divisor is not zero",
                    "Check for edge cases in your calculations",
                ],
            )

        result = a % b
        _validate_finite(result, "result")

        return {
            "result": result,
            "operation": "modulo",
            "inputs": {"a": a, "b": b},
            "precision": PRECISION,
            "formula": f"{a} mod {b}",
            "success": True,
        }

    except (ValidationError, PrecisionError):
        raise
    except Exception as e:
        raise ComputationError(
            f"Modulo operation failed: {str(e)}", operation="modulo", inputs={"a": a, "b": b}
        )


def absolute_value(value: Union[int, float]) -> Dict[str, Any]:
    """Calculate the absolute value of a number.

    Args:
        value: Input number

    Returns:
        Dict containing the absolute value and metadata.
    """
    try:
        _validate_finite(value, "value")

        result = abs(value)
        _validate_finite(result, "result")

        return {
            "result": result,
            "operation": "absolute_value",
            "inputs": {"value": value},
            "precision": PRECISION,
            "formula": f"|{value}|",
            "success": True,
        }

    except (ValidationError, PrecisionError):
        raise
    except Exception as e:
        raise ComputationError(
            f"Absolute value calculation failed: {str(e)}",
            operation="absolute_value",
            inputs={"value": value},
        )


def sign(value: Union[int, float]) -> Dict[str, Any]:
    """Get the sign of a number (-1, 0, or 1).

    Args:
        value: Input number

    Returns:
        Dict containing the sign and metadata.
    """
    try:
        _validate_finite(value, "value")

        if value > 0:
            result = 1
        elif value < 0:
            result = -1
        else:
            result = 0

        return {
            "result": result,
            "operation": "sign",
            "inputs": {"value": value},
            "precision": PRECISION,
            "formula": f"sign({value})",
            "success": True,
        }

    except (ValidationError, PrecisionError):
        raise
    except Exception as e:
        raise ComputationError(
            f"Sign calculation failed: {str(e)}", operation="sign", inputs={"value": value}
        )


def factorial(n: int) -> Dict[str, Any]:
    """Calculate the factorial of a non-negative integer.

    Args:
        n: Non-negative integer

    Returns:
        Dict containing the factorial and metadata.
    """
    try:
        if not isinstance(n, int):
            raise ValidationError(
                "Factorial is only defined for integers",
                field="n",
                value=n,
                suggestions=["Use an integer value for factorial calculation"],
            )

        if n < 0:
            raise ValidationError(
                "Factorial is only defined for non-negative integers",
                field="n",
                value=n,
                suggestions=["Use a non-negative integer (0 or positive)"],
            )

        if n > 170:  # Factorial of 171 overflows float64
            raise ValidationError(
                "Factorial input too large (maximum 170)",
                field="n",
                value=n,
                suggestions=[
                    "Use a smaller integer (≤ 170)",
                    "Consider using logarithmic factorial for large values",
                ],
            )

        result = math.factorial(n)

        return {
            "result": result,
            "operation": "factorial",
            "inputs": {"n": n},
            "precision": PRECISION,
            "formula": f"{n}!",
            "success": True,
        }

    except (ValidationError, PrecisionError):
        raise
    except Exception as e:
        raise ComputationError(
            f"Factorial calculation failed: {str(e)}", operation="factorial", inputs={"n": n}
        )
