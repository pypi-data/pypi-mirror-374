"""
Advanced mathematical functions module for the Scientific Calculator MCP Server.

This module provides trigonometric, logarithmic, exponential, and hyperbolic functions
with proper domain validation and error handling.
"""

import math
import numpy as np
from decimal import Decimal, getcontext
from typing import Union, Tuple
from calculator.models.errors import CalculatorError, ValidationError


class AdvancedMathError(CalculatorError):
    """Error for advanced mathematical operations."""
    pass


def _validate_numeric_input(value: Union[float, int, Decimal]) -> float:
    """Validate and convert numeric input to float."""
    try:
        if isinstance(value, Decimal):
            return float(value)
        return float(value)
    except (ValueError, TypeError, OverflowError) as e:
        raise ValidationError(f"Invalid numeric input: {value}") from e


def _convert_angle_to_radians(value: float, unit: str) -> float:
    """Convert angle from specified unit to radians."""
    if unit.lower() == "radians":
        return value
    elif unit.lower() == "degrees":
        return math.radians(value)
    else:
        raise ValidationError(f"Invalid angle unit: {unit}. Must be 'radians' or 'degrees'")


def _convert_angle_from_radians(value: float, unit: str) -> float:
    """Convert angle from radians to specified unit."""
    if unit.lower() == "radians":
        return value
    elif unit.lower() == "degrees":
        return math.degrees(value)
    else:
        raise ValidationError(f"Invalid angle unit: {unit}. Must be 'radians' or 'degrees'")


# Trigonometric Functions
def sin(value: Union[float, int], unit: str = "radians") -> float:
    """Calculate sine of an angle."""
    try:
        numeric_value = _validate_numeric_input(value)
        radians_value = _convert_angle_to_radians(numeric_value, unit)
        
        # Check for potential overflow
        if abs(radians_value) > 1e10:
            raise AdvancedMathError("Input value too large for sine calculation")
            
        result = math.sin(radians_value)
        
        # Handle floating point precision issues near zero
        if abs(result) < 1e-15:
            result = 0.0
            
        return result
        
    except (ValueError, OverflowError) as e:
        raise AdvancedMathError(f"Error calculating sine: {e}") from e


def cos(value: Union[float, int], unit: str = "radians") -> float:
    """Calculate cosine of an angle."""
    try:
        numeric_value = _validate_numeric_input(value)
        radians_value = _convert_angle_to_radians(numeric_value, unit)
        
        # Check for potential overflow
        if abs(radians_value) > 1e10:
            raise AdvancedMathError("Input value too large for cosine calculation")
            
        result = math.cos(radians_value)
        
        # Handle floating point precision issues near zero
        if abs(result) < 1e-15:
            result = 0.0
            
        return result
        
    except (ValueError, OverflowError) as e:
        raise AdvancedMathError(f"Error calculating cosine: {e}") from e


def tan(value: Union[float, int], unit: str = "radians") -> float:
    """Calculate tangent of an angle."""
    try:
        numeric_value = _validate_numeric_input(value)
        radians_value = _convert_angle_to_radians(numeric_value, unit)
        
        # Check for potential overflow
        if abs(radians_value) > 1e10:
            raise AdvancedMathError("Input value too large for tangent calculation")
        
        # Check for values where tangent is undefined (odd multiples of π/2)
        # Allow for small floating point errors
        normalized = radians_value / (math.pi / 2)
        if abs(normalized - round(normalized)) < 1e-10 and round(normalized) % 2 == 1:
            raise AdvancedMathError("Tangent is undefined at odd multiples of π/2")
            
        result = math.tan(radians_value)
        
        # Handle floating point precision issues near zero
        if abs(result) < 1e-15:
            result = 0.0
        
        # Check for very large results that might indicate near-asymptote
        if abs(result) > 1e10:
            raise AdvancedMathError("Tangent result too large (near asymptote)")
            
        return result
        
    except (ValueError, OverflowError) as e:
        raise AdvancedMathError(f"Error calculating tangent: {e}") from e


def sec(value: Union[float, int], unit: str = "radians") -> float:
    """Calculate secant of an angle (1/cos)."""
    try:
        cos_value = cos(value, unit)
        
        if abs(cos_value) < 1e-15:
            raise AdvancedMathError("Secant is undefined when cosine is zero")
            
        result = 1.0 / cos_value
        
        # Check for very large results
        if abs(result) > 1e10:
            raise AdvancedMathError("Secant result too large")
            
        return result
        
    except AdvancedMathError:
        raise
    except Exception as e:
        raise AdvancedMathError(f"Error calculating secant: {e}") from e


def csc(value: Union[float, int], unit: str = "radians") -> float:
    """Calculate cosecant of an angle (1/sin)."""
    try:
        sin_value = sin(value, unit)
        
        if abs(sin_value) < 1e-15:
            raise AdvancedMathError("Cosecant is undefined when sine is zero")
            
        result = 1.0 / sin_value
        
        # Check for very large results
        if abs(result) > 1e10:
            raise AdvancedMathError("Cosecant result too large")
            
        return result
        
    except AdvancedMathError:
        raise
    except Exception as e:
        raise AdvancedMathError(f"Error calculating cosecant: {e}") from e


def cot(value: Union[float, int], unit: str = "radians") -> float:
    """Calculate cotangent of an angle (1/tan)."""
    try:
        tan_value = tan(value, unit)
        
        if abs(tan_value) < 1e-15:
            raise AdvancedMathError("Cotangent is undefined when tangent is zero")
            
        result = 1.0 / tan_value
        
        # Check for very large results
        if abs(result) > 1e10:
            raise AdvancedMathError("Cotangent result too large")
            
        return result
        
    except AdvancedMathError:
        raise
    except Exception as e:
        raise AdvancedMathError(f"Error calculating cotangent: {e}") from e


# Inverse Trigonometric Functions
def arcsin(value: Union[float, int], unit: str = "radians") -> float:
    """Calculate arcsine (inverse sine) of a value."""
    try:
        numeric_value = _validate_numeric_input(value)
        
        # Domain check: -1 <= value <= 1
        if numeric_value < -1 or numeric_value > 1:
            raise AdvancedMathError(f"Arcsine domain error: {numeric_value} is not in [-1, 1]")
            
        result_radians = math.asin(numeric_value)
        return _convert_angle_from_radians(result_radians, unit)
        
    except (ValueError, OverflowError) as e:
        raise AdvancedMathError(f"Error calculating arcsine: {e}") from e


def arccos(value: Union[float, int], unit: str = "radians") -> float:
    """Calculate arccosine (inverse cosine) of a value."""
    try:
        numeric_value = _validate_numeric_input(value)
        
        # Domain check: -1 <= value <= 1
        if numeric_value < -1 or numeric_value > 1:
            raise AdvancedMathError(f"Arccosine domain error: {numeric_value} is not in [-1, 1]")
            
        result_radians = math.acos(numeric_value)
        return _convert_angle_from_radians(result_radians, unit)
        
    except (ValueError, OverflowError) as e:
        raise AdvancedMathError(f"Error calculating arccosine: {e}") from e


def arctan(value: Union[float, int], unit: str = "radians") -> float:
    """Calculate arctangent (inverse tangent) of a value."""
    try:
        numeric_value = _validate_numeric_input(value)
        
        result_radians = math.atan(numeric_value)
        return _convert_angle_from_radians(result_radians, unit)
        
    except (ValueError, OverflowError) as e:
        raise AdvancedMathError(f"Error calculating arctangent: {e}") from e


def arctan2(y: Union[float, int], x: Union[float, int], unit: str = "radians") -> float:
    """Calculate two-argument arctangent of y/x."""
    try:
        y_value = _validate_numeric_input(y)
        x_value = _validate_numeric_input(x)
        
        if x_value == 0 and y_value == 0:
            raise AdvancedMathError("Arctan2 is undefined for (0, 0)")
            
        result_radians = math.atan2(y_value, x_value)
        return _convert_angle_from_radians(result_radians, unit)
        
    except (ValueError, OverflowError) as e:
        raise AdvancedMathError(f"Error calculating arctan2: {e}") from e


# Hyperbolic Functions
def sinh(value: Union[float, int]) -> float:
    """Calculate hyperbolic sine of a value."""
    try:
        numeric_value = _validate_numeric_input(value)
        
        # Check for potential overflow
        if abs(numeric_value) > 700:  # e^700 is near float overflow
            raise AdvancedMathError("Input value too large for sinh calculation")
            
        return math.sinh(numeric_value)
        
    except (ValueError, OverflowError) as e:
        raise AdvancedMathError(f"Error calculating sinh: {e}") from e


def cosh(value: Union[float, int]) -> float:
    """Calculate hyperbolic cosine of a value."""
    try:
        numeric_value = _validate_numeric_input(value)
        
        # Check for potential overflow
        if abs(numeric_value) > 700:  # e^700 is near float overflow
            raise AdvancedMathError("Input value too large for cosh calculation")
            
        return math.cosh(numeric_value)
        
    except (ValueError, OverflowError) as e:
        raise AdvancedMathError(f"Error calculating cosh: {e}") from e


def tanh(value: Union[float, int]) -> float:
    """Calculate hyperbolic tangent of a value."""
    try:
        numeric_value = _validate_numeric_input(value)
        
        return math.tanh(numeric_value)
        
    except (ValueError, OverflowError) as e:
        raise AdvancedMathError(f"Error calculating tanh: {e}") from e


# Logarithmic Functions
def natural_log(value: Union[float, int]) -> float:
    """Calculate natural logarithm (base e) of a value."""
    try:
        numeric_value = _validate_numeric_input(value)
        
        if numeric_value <= 0:
            raise AdvancedMathError(f"Natural log domain error: {numeric_value} must be positive")
            
        return math.log(numeric_value)
        
    except (ValueError, OverflowError) as e:
        raise AdvancedMathError(f"Error calculating natural log: {e}") from e


def log10(value: Union[float, int]) -> float:
    """Calculate base-10 logarithm of a value."""
    try:
        numeric_value = _validate_numeric_input(value)
        
        if numeric_value <= 0:
            raise AdvancedMathError(f"Log10 domain error: {numeric_value} must be positive")
            
        return math.log10(numeric_value)
        
    except (ValueError, OverflowError) as e:
        raise AdvancedMathError(f"Error calculating log10: {e}") from e


def log_base(value: Union[float, int], base: Union[float, int]) -> float:
    """Calculate logarithm of a value with custom base."""
    try:
        numeric_value = _validate_numeric_input(value)
        base_value = _validate_numeric_input(base)
        
        if numeric_value <= 0:
            raise AdvancedMathError(f"Log domain error: {numeric_value} must be positive")
            
        if base_value <= 0 or base_value == 1:
            raise AdvancedMathError(f"Log base error: {base_value} must be positive and not equal to 1")
            
        return math.log(numeric_value) / math.log(base_value)
        
    except (ValueError, OverflowError) as e:
        raise AdvancedMathError(f"Error calculating log base {base}: {e}") from e


# Exponential Functions
def exp(value: Union[float, int]) -> float:
    """Calculate e raised to the power of value."""
    try:
        numeric_value = _validate_numeric_input(value)
        
        # Check for potential overflow
        if numeric_value > 700:  # e^700 is near float overflow
            raise AdvancedMathError("Exponent too large for exp calculation")
            
        # Check for potential underflow
        if numeric_value < -700:
            return 0.0  # Graceful underflow to zero
            
        return math.exp(numeric_value)
        
    except (ValueError, OverflowError) as e:
        raise AdvancedMathError(f"Error calculating exp: {e}") from e


def power_base(base: Union[float, int], exponent: Union[float, int]) -> float:
    """Calculate base raised to the power of exponent."""
    try:
        base_value = _validate_numeric_input(base)
        exp_value = _validate_numeric_input(exponent)
        
        # Handle special cases
        if base_value == 0:
            if exp_value < 0:
                raise AdvancedMathError("Cannot raise 0 to a negative power")
            elif exp_value == 0:
                raise AdvancedMathError("0^0 is undefined")
            else:
                return 0.0
                
        if base_value < 0 and not exp_value.is_integer():
            raise AdvancedMathError("Cannot raise negative number to non-integer power")
            
        # Check for potential overflow
        if abs(base_value) > 1 and abs(exp_value) > 100:
            # Rough overflow check
            if abs(base_value) ** abs(exp_value) > 1e100:
                raise AdvancedMathError("Result would be too large")
                
        return base_value ** exp_value
        
    except (ValueError, OverflowError) as e:
        raise AdvancedMathError(f"Error calculating power: {e}") from e


# Utility Functions
def degrees_to_radians(degrees: Union[float, int]) -> float:
    """Convert degrees to radians."""
    try:
        numeric_value = _validate_numeric_input(degrees)
        return math.radians(numeric_value)
    except Exception as e:
        raise AdvancedMathError(f"Error converting degrees to radians: {e}") from e


def radians_to_degrees(radians: Union[float, int]) -> float:
    """Convert radians to degrees."""
    try:
        numeric_value = _validate_numeric_input(radians)
        return math.degrees(numeric_value)
    except Exception as e:
        raise AdvancedMathError(f"Error converting radians to degrees: {e}") from e


# Function registry for dynamic access
TRIGONOMETRIC_FUNCTIONS = {
    'sin': sin,
    'cos': cos,
    'tan': tan,
    'sec': sec,
    'csc': csc,
    'cot': cot,
    'arcsin': arcsin,
    'asin': arcsin,
    'arccos': arccos,
    'acos': arccos,
    'arctan': arctan,
    'atan': arctan,
    'arctan2': arctan2,
    'atan2': arctan2,
}

HYPERBOLIC_FUNCTIONS = {
    'sinh': sinh,
    'cosh': cosh,
    'tanh': tanh,
}

LOGARITHMIC_FUNCTIONS = {
    'ln': natural_log,
    'log': natural_log,
    'log10': log10,
    'log_base': log_base,
}

EXPONENTIAL_FUNCTIONS = {
    'exp': exp,
    'power': power_base,
    'pow': power_base,
}

ALL_ADVANCED_FUNCTIONS = {
    **TRIGONOMETRIC_FUNCTIONS,
    **HYPERBOLIC_FUNCTIONS,
    **LOGARITHMIC_FUNCTIONS,
    **EXPONENTIAL_FUNCTIONS,
}


def get_function(function_name: str):
    """Get a function by name from the registry."""
    if function_name not in ALL_ADVANCED_FUNCTIONS:
        available_functions = ', '.join(sorted(ALL_ADVANCED_FUNCTIONS.keys()))
        raise ValidationError(
            f"Unknown function: {function_name}. "
            f"Available functions: {available_functions}"
        )
    return ALL_ADVANCED_FUNCTIONS[function_name]