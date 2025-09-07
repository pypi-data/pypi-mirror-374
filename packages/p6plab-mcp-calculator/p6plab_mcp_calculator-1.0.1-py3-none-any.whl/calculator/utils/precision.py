"""
Precision handling utilities for the Scientific Calculator MCP Server.

This module provides high-precision arithmetic using Python's Decimal module,
precision validation, rounding functions, and precision metadata tracking.
"""

import os
from decimal import Decimal, getcontext, ROUND_HALF_UP, ROUND_HALF_EVEN, InvalidOperation
from typing import Union, Dict, Any, Optional
import math

from calculator.models.errors import CalculatorError, ValidationError


class PrecisionError(CalculatorError):
    """Error for precision-related operations."""
    pass


# Get precision configuration from environment
DEFAULT_PRECISION = int(os.getenv("CALCULATOR_PRECISION", "15"))
MAX_PRECISION = int(os.getenv("CALCULATOR_MAX_PRECISION", "50"))
MIN_PRECISION = int(os.getenv("CALCULATOR_MIN_PRECISION", "1"))

# Set global decimal context
getcontext().prec = max(DEFAULT_PRECISION, 28)  # Ensure sufficient precision for calculations


def set_precision(precision: int) -> Dict[str, Any]:
    """Set the global precision for decimal calculations.
    
    Args:
        precision: Number of significant digits
    """
    try:
        if not isinstance(precision, int):
            raise ValidationError("Precision must be an integer")
        
        if precision < MIN_PRECISION or precision > MAX_PRECISION:
            raise ValidationError(f"Precision must be between {MIN_PRECISION} and {MAX_PRECISION}")
        
        old_precision = getcontext().prec
        getcontext().prec = precision
        
        return {
            "old_precision": old_precision,
            "new_precision": precision,
            "min_precision": MIN_PRECISION,
            "max_precision": MAX_PRECISION,
            "operation": "set_precision"
        }
        
    except Exception as e:
        raise PrecisionError(f"Error setting precision: {e}") from e


def get_precision() -> Dict[str, Any]:
    """Get current precision settings."""
    return {
        "current_precision": getcontext().prec,
        "default_precision": DEFAULT_PRECISION,
        "min_precision": MIN_PRECISION,
        "max_precision": MAX_PRECISION,
        "rounding_mode": str(getcontext().rounding),
        "operation": "get_precision"
    }


def to_decimal(value: Union[float, int, str, Decimal], precision: Optional[int] = None) -> Decimal:
    """Convert a value to Decimal with specified precision.
    
    Args:
        value: Value to convert
        precision: Optional precision override
    """
    try:
        if precision is not None:
            if precision < MIN_PRECISION or precision > MAX_PRECISION:
                raise ValidationError(f"Precision must be between {MIN_PRECISION} and {MAX_PRECISION}")
            
            # Temporarily set precision
            old_prec = getcontext().prec
            getcontext().prec = precision
            
            try:
                if isinstance(value, Decimal):
                    result = +value  # Apply current precision
                else:
                    result = Decimal(str(value))
                return result
            finally:
                getcontext().prec = old_prec
        else:
            if isinstance(value, Decimal):
                return value
            else:
                return Decimal(str(value))
                
    except (InvalidOperation, ValueError, TypeError) as e:
        raise PrecisionError(f"Error converting to Decimal: {e}") from e


def from_decimal(decimal_value: Decimal, output_type: str = "float") -> Union[float, str, int]:
    """Convert Decimal to specified output type.
    
    Args:
        decimal_value: Decimal value to convert
        output_type: "float", "string", or "int"
    """
    try:
        if not isinstance(decimal_value, Decimal):
            raise ValidationError("Input must be a Decimal")
        
        if output_type == "float":
            return float(decimal_value)
        elif output_type == "string":
            return str(decimal_value)
        elif output_type == "int":
            return int(decimal_value)
        else:
            raise ValidationError("Output type must be 'float', 'string', or 'int'")
            
    except Exception as e:
        raise PrecisionError(f"Error converting from Decimal: {e}") from e


def round_decimal(value: Union[Decimal, float, int], 
                 decimal_places: int, 
                 rounding_mode: str = "ROUND_HALF_UP") -> Decimal:
    """Round a decimal value to specified decimal places.
    
    Args:
        value: Value to round
        decimal_places: Number of decimal places
        rounding_mode: Rounding mode ("ROUND_HALF_UP", "ROUND_HALF_EVEN", etc.)
    """
    try:
        if decimal_places < 0 or decimal_places > 50:
            raise ValidationError("Decimal places must be between 0 and 50")
        
        # Map rounding mode strings to constants
        rounding_modes = {
            "ROUND_HALF_UP": ROUND_HALF_UP,
            "ROUND_HALF_EVEN": ROUND_HALF_EVEN,
            "ROUND_UP": "ROUND_UP",
            "ROUND_DOWN": "ROUND_DOWN",
            "ROUND_CEILING": "ROUND_CEILING",
            "ROUND_FLOOR": "ROUND_FLOOR"
        }
        
        if rounding_mode not in rounding_modes:
            available_modes = ', '.join(rounding_modes.keys())
            raise ValidationError(f"Invalid rounding mode. Available: {available_modes}")
        
        decimal_value = to_decimal(value)
        
        # Create quantizer for the desired decimal places
        quantizer = Decimal('0.1') ** decimal_places
        
        # Set rounding mode temporarily
        old_rounding = getcontext().rounding
        getcontext().rounding = rounding_modes[rounding_mode]
        
        try:
            result = decimal_value.quantize(quantizer)
            return result
        finally:
            getcontext().rounding = old_rounding
            
    except Exception as e:
        raise PrecisionError(f"Error rounding decimal: {e}") from e


def significant_figures(value: Union[Decimal, float, int], sig_figs: int) -> Decimal:
    """Round a value to specified number of significant figures.
    
    Args:
        value: Value to round
        sig_figs: Number of significant figures
    """
    try:
        if sig_figs < 1 or sig_figs > 50:
            raise ValidationError("Significant figures must be between 1 and 50")
        
        decimal_value = to_decimal(value)
        
        if decimal_value == 0:
            return decimal_value
        
        # Find the order of magnitude
        magnitude = decimal_value.log10().to_integral_value()
        
        # Calculate the position for rounding
        round_position = sig_figs - int(magnitude) - 1
        
        # Round to the calculated position
        quantizer = Decimal('0.1') ** round_position
        result = decimal_value.quantize(quantizer, rounding=ROUND_HALF_UP)
        
        return result
        
    except Exception as e:
        raise PrecisionError(f"Error applying significant figures: {e}") from e


def precision_add(a: Union[Decimal, float, int], 
                 b: Union[Decimal, float, int],
                 precision: Optional[int] = None) -> Dict[str, Any]:
    """High-precision addition with metadata.
    
    Args:
        a: First operand
        b: Second operand
        precision: Optional precision override
    """
    try:
        decimal_a = to_decimal(a, precision)
        decimal_b = to_decimal(b, precision)
        
        result = decimal_a + decimal_b
        
        return {
            "result": result,
            "result_float": float(result),
            "result_string": str(result),
            "operands": {"a": str(decimal_a), "b": str(decimal_b)},
            "precision": getcontext().prec,
            "operation": "precision_add"
        }
        
    except Exception as e:
        raise PrecisionError(f"Error in precision addition: {e}") from e


def precision_multiply(a: Union[Decimal, float, int], 
                      b: Union[Decimal, float, int],
                      precision: Optional[int] = None) -> Dict[str, Any]:
    """High-precision multiplication with metadata.
    
    Args:
        a: First operand
        b: Second operand
        precision: Optional precision override
    """
    try:
        decimal_a = to_decimal(a, precision)
        decimal_b = to_decimal(b, precision)
        
        result = decimal_a * decimal_b
        
        return {
            "result": result,
            "result_float": float(result),
            "result_string": str(result),
            "operands": {"a": str(decimal_a), "b": str(decimal_b)},
            "precision": getcontext().prec,
            "operation": "precision_multiply"
        }
        
    except Exception as e:
        raise PrecisionError(f"Error in precision multiplication: {e}") from e


def precision_divide(a: Union[Decimal, float, int], 
                    b: Union[Decimal, float, int],
                    precision: Optional[int] = None) -> Dict[str, Any]:
    """High-precision division with metadata.
    
    Args:
        a: Dividend
        b: Divisor
        precision: Optional precision override
    """
    try:
        decimal_a = to_decimal(a, precision)
        decimal_b = to_decimal(b, precision)
        
        if decimal_b == 0:
            raise PrecisionError("Division by zero")
        
        result = decimal_a / decimal_b
        
        return {
            "result": result,
            "result_float": float(result),
            "result_string": str(result),
            "operands": {"a": str(decimal_a), "b": str(decimal_b)},
            "precision": getcontext().prec,
            "operation": "precision_divide"
        }
        
    except Exception as e:
        raise PrecisionError(f"Error in precision division: {e}") from e


def precision_power(base: Union[Decimal, float, int], 
                   exponent: Union[Decimal, float, int],
                   precision: Optional[int] = None) -> Dict[str, Any]:
    """High-precision exponentiation with metadata.
    
    Args:
        base: Base value
        exponent: Exponent value
        precision: Optional precision override
    """
    try:
        decimal_base = to_decimal(base, precision)
        decimal_exp = to_decimal(exponent, precision)
        
        # Handle special cases
        if decimal_base == 0 and decimal_exp < 0:
            raise PrecisionError("Cannot raise 0 to a negative power")
        
        if decimal_base == 0 and decimal_exp == 0:
            raise PrecisionError("0^0 is undefined")
        
        result = decimal_base ** decimal_exp
        
        return {
            "result": result,
            "result_float": float(result),
            "result_string": str(result),
            "operands": {"base": str(decimal_base), "exponent": str(decimal_exp)},
            "precision": getcontext().prec,
            "operation": "precision_power"
        }
        
    except Exception as e:
        raise PrecisionError(f"Error in precision exponentiation: {e}") from e


def precision_sqrt(value: Union[Decimal, float, int],
                  precision: Optional[int] = None) -> Dict[str, Any]:
    """High-precision square root with metadata.
    
    Args:
        value: Value to find square root of
        precision: Optional precision override
    """
    try:
        decimal_value = to_decimal(value, precision)
        
        if decimal_value < 0:
            raise PrecisionError("Cannot take square root of negative number")
        
        result = decimal_value.sqrt()
        
        return {
            "result": result,
            "result_float": float(result),
            "result_string": str(result),
            "operand": str(decimal_value),
            "precision": getcontext().prec,
            "operation": "precision_sqrt"
        }
        
    except Exception as e:
        raise PrecisionError(f"Error in precision square root: {e}") from e


def compare_precision(a: Union[Decimal, float, int], 
                     b: Union[Decimal, float, int],
                     tolerance: Union[Decimal, float, int] = None) -> Dict[str, Any]:
    """Compare two values with precision considerations.
    
    Args:
        a: First value
        b: Second value
        tolerance: Optional tolerance for equality comparison
    """
    try:
        decimal_a = to_decimal(a)
        decimal_b = to_decimal(b)
        
        if tolerance is not None:
            decimal_tolerance = to_decimal(tolerance)
            difference = abs(decimal_a - decimal_b)
            is_equal = difference <= decimal_tolerance
        else:
            is_equal = decimal_a == decimal_b
            difference = abs(decimal_a - decimal_b)
        
        return {
            "a": str(decimal_a),
            "b": str(decimal_b),
            "difference": str(difference),
            "is_equal": is_equal,
            "tolerance": str(tolerance) if tolerance is not None else None,
            "comparison": "equal" if is_equal else ("greater" if decimal_a > decimal_b else "less"),
            "operation": "compare_precision"
        }
        
    except Exception as e:
        raise PrecisionError(f"Error in precision comparison: {e}") from e


def format_number(value: Union[Decimal, float, int], 
                 format_type: str = "auto",
                 decimal_places: Optional[int] = None) -> Dict[str, Any]:
    """Format a number for display with various options.
    
    Args:
        value: Value to format
        format_type: "auto", "fixed", "scientific", "engineering"
        decimal_places: Number of decimal places for fixed format
    """
    try:
        decimal_value = to_decimal(value)
        
        if format_type == "fixed":
            if decimal_places is None:
                decimal_places = 6
            formatted = f"{float(decimal_value):.{decimal_places}f}"
        elif format_type == "scientific":
            formatted = f"{float(decimal_value):.6e}"
        elif format_type == "engineering":
            # Engineering notation (powers of 1000)
            exp = int(decimal_value.log10() // 3) * 3
            mantissa = decimal_value / (Decimal(10) ** exp)
            formatted = f"{float(mantissa):.3f}e{exp:+d}"
        else:  # auto
            # Choose best format based on magnitude
            abs_val = abs(decimal_value)
            if abs_val == 0:
                formatted = "0"
            elif abs_val >= Decimal('1e6') or abs_val < Decimal('1e-3'):
                formatted = f"{float(decimal_value):.6e}"
            else:
                formatted = str(decimal_value)
        
        return {
            "original": str(decimal_value),
            "formatted": formatted,
            "format_type": format_type,
            "decimal_places": decimal_places,
            "operation": "format_number"
        }
        
    except Exception as e:
        raise PrecisionError(f"Error formatting number: {e}") from e


def detect_precision_loss(original: Union[float, int], 
                         calculated: Union[Decimal, float, int]) -> Dict[str, Any]:
    """Detect potential precision loss in calculations.
    
    Args:
        original: Original input value
        calculated: Calculated result value
    """
    try:
        original_decimal = to_decimal(original)
        calculated_decimal = to_decimal(calculated)
        
        # Convert back to float and compare
        float_result = float(calculated_decimal)
        float_original = float(original_decimal)
        
        # Calculate relative error
        if float_original != 0:
            relative_error = abs((float_result - float_original) / float_original)
        else:
            relative_error = abs(float_result - float_original)
        
        # Determine precision loss level
        if relative_error < 1e-15:
            precision_loss = "none"
        elif relative_error < 1e-12:
            precision_loss = "minimal"
        elif relative_error < 1e-9:
            precision_loss = "moderate"
        else:
            precision_loss = "significant"
        
        return {
            "original": str(original_decimal),
            "calculated": str(calculated_decimal),
            "float_conversion": float_result,
            "relative_error": relative_error,
            "precision_loss": precision_loss,
            "recommendation": "Use Decimal arithmetic" if precision_loss in ["moderate", "significant"] else "Float precision sufficient",
            "operation": "detect_precision_loss"
        }
        
    except Exception as e:
        raise PrecisionError(f"Error detecting precision loss: {e}") from e