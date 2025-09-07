"""
Complex number operations module for the Scientific Calculator MCP Server.

This module provides comprehensive complex number arithmetic, conversions,
and mathematical operations with proper validation and error handling.
"""

import cmath
import math
from typing import Union, Dict, Any, Tuple
from decimal import Decimal

from calculator.models.errors import CalculatorError, ValidationError


class ComplexError(CalculatorError):
    """Error for complex number operations."""
    pass


def _parse_complex_input(value: Union[complex, str, float, int, Dict[str, float]]) -> complex:
    """Parse and validate complex number input from various formats."""
    try:
        if isinstance(value, complex):
            return value
        elif isinstance(value, (int, float)):
            return complex(value, 0)
        elif isinstance(value, str):
            # Handle string representations like "3+4j", "3-4j", "5j", "3", etc.
            value = value.strip().replace(' ', '').replace('i', 'j')
            if value == '':
                raise ValueError("Empty string")
            return complex(value)
        elif isinstance(value, dict):
            # Handle dictionary format like {"real": 3, "imag": 4}
            if 'real' in value and 'imag' in value:
                return complex(float(value['real']), float(value['imag']))
            elif 'r' in value and 'i' in value:
                return complex(float(value['r']), float(value['i']))
            else:
                raise ValueError("Dictionary must contain 'real'/'imag' or 'r'/'i' keys")
        else:
            raise ValueError(f"Unsupported complex number format: {type(value)}")
            
    except (ValueError, TypeError) as e:
        raise ValidationError(f"Invalid complex number format: {value}. Error: {e}") from e


def _validate_finite_complex(z: complex, name: str = "complex number") -> complex:
    """Validate that a complex number has finite real and imaginary parts."""
    if not (math.isfinite(z.real) and math.isfinite(z.imag)):
        raise ComplexError(f"{name} contains infinite or NaN values: {z}")
    return z


def _complex_to_dict(z: complex) -> Dict[str, float]:
    """Convert complex number to dictionary representation."""
    return {
        "real": float(z.real),
        "imag": float(z.imag)
    }


def _format_complex_string(z: complex) -> str:
    """Format complex number as a readable string."""
    real_part = z.real
    imag_part = z.imag
    
    if imag_part == 0:
        return f"{real_part}"
    elif real_part == 0:
        if imag_part == 1:
            return "j"
        elif imag_part == -1:
            return "-j"
        else:
            return f"{imag_part}j"
    else:
        if imag_part == 1:
            return f"{real_part}+j"
        elif imag_part == -1:
            return f"{real_part}-j"
        elif imag_part > 0:
            return f"{real_part}+{imag_part}j"
        else:
            return f"{real_part}{imag_part}j"


# Basic Complex Arithmetic
def complex_add(z1: Union[complex, str, float, int, Dict[str, float]], 
               z2: Union[complex, str, float, int, Dict[str, float]]) -> Dict[str, Any]:
    """Add two complex numbers."""
    try:
        c1 = _parse_complex_input(z1)
        c2 = _parse_complex_input(z2)
        
        _validate_finite_complex(c1, "first complex number")
        _validate_finite_complex(c2, "second complex number")
        
        result = c1 + c2
        _validate_finite_complex(result, "result")
        
        return {
            "result": _complex_to_dict(result),
            "result_string": _format_complex_string(result),
            "operation": "complex_addition",
            "operands": {
                "z1": _complex_to_dict(c1),
                "z2": _complex_to_dict(c2)
            }
        }
        
    except Exception as e:
        raise ComplexError(f"Error in complex addition: {e}") from e


def complex_subtract(z1: Union[complex, str, float, int, Dict[str, float]], 
                    z2: Union[complex, str, float, int, Dict[str, float]]) -> Dict[str, Any]:
    """Subtract two complex numbers."""
    try:
        c1 = _parse_complex_input(z1)
        c2 = _parse_complex_input(z2)
        
        _validate_finite_complex(c1, "first complex number")
        _validate_finite_complex(c2, "second complex number")
        
        result = c1 - c2
        _validate_finite_complex(result, "result")
        
        return {
            "result": _complex_to_dict(result),
            "result_string": _format_complex_string(result),
            "operation": "complex_subtraction",
            "operands": {
                "z1": _complex_to_dict(c1),
                "z2": _complex_to_dict(c2)
            }
        }
        
    except Exception as e:
        raise ComplexError(f"Error in complex subtraction: {e}") from e


def complex_multiply(z1: Union[complex, str, float, int, Dict[str, float]], 
                    z2: Union[complex, str, float, int, Dict[str, float]]) -> Dict[str, Any]:
    """Multiply two complex numbers."""
    try:
        c1 = _parse_complex_input(z1)
        c2 = _parse_complex_input(z2)
        
        _validate_finite_complex(c1, "first complex number")
        _validate_finite_complex(c2, "second complex number")
        
        result = c1 * c2
        _validate_finite_complex(result, "result")
        
        return {
            "result": _complex_to_dict(result),
            "result_string": _format_complex_string(result),
            "operation": "complex_multiplication",
            "operands": {
                "z1": _complex_to_dict(c1),
                "z2": _complex_to_dict(c2)
            }
        }
        
    except Exception as e:
        raise ComplexError(f"Error in complex multiplication: {e}") from e


def complex_divide(z1: Union[complex, str, float, int, Dict[str, float]], 
                  z2: Union[complex, str, float, int, Dict[str, float]]) -> Dict[str, Any]:
    """Divide two complex numbers."""
    try:
        c1 = _parse_complex_input(z1)
        c2 = _parse_complex_input(z2)
        
        _validate_finite_complex(c1, "dividend")
        _validate_finite_complex(c2, "divisor")
        
        if c2 == 0:
            raise ComplexError("Division by zero is not allowed")
        
        result = c1 / c2
        _validate_finite_complex(result, "result")
        
        return {
            "result": _complex_to_dict(result),
            "result_string": _format_complex_string(result),
            "operation": "complex_division",
            "operands": {
                "z1": _complex_to_dict(c1),
                "z2": _complex_to_dict(c2)
            }
        }
        
    except Exception as e:
        raise ComplexError(f"Error in complex division: {e}") from e


def complex_power(z: Union[complex, str, float, int, Dict[str, float]], 
                 exponent: Union[complex, str, float, int, Dict[str, float]]) -> Dict[str, Any]:
    """Raise a complex number to a power."""
    try:
        base = _parse_complex_input(z)
        exp = _parse_complex_input(exponent)
        
        _validate_finite_complex(base, "base")
        _validate_finite_complex(exp, "exponent")
        
        # Handle special cases
        if base == 0 and exp.real <= 0:
            raise ComplexError("Cannot raise 0 to a non-positive power")
        
        result = base ** exp
        _validate_finite_complex(result, "result")
        
        return {
            "result": _complex_to_dict(result),
            "result_string": _format_complex_string(result),
            "operation": "complex_power",
            "operands": {
                "base": _complex_to_dict(base),
                "exponent": _complex_to_dict(exp)
            }
        }
        
    except Exception as e:
        raise ComplexError(f"Error in complex power: {e}") from e


# Complex Number Properties
def complex_magnitude(z: Union[complex, str, float, int, Dict[str, float]]) -> Dict[str, Any]:
    """Calculate the magnitude (absolute value) of a complex number."""
    try:
        c = _parse_complex_input(z)
        _validate_finite_complex(c, "complex number")
        
        magnitude = abs(c)
        
        return {
            "result": float(magnitude),
            "operation": "complex_magnitude",
            "input": _complex_to_dict(c),
            "input_string": _format_complex_string(c)
        }
        
    except Exception as e:
        raise ComplexError(f"Error calculating complex magnitude: {e}") from e


def complex_phase(z: Union[complex, str, float, int, Dict[str, float]], 
                 unit: str = "radians") -> Dict[str, Any]:
    """Calculate the phase (argument) of a complex number."""
    try:
        c = _parse_complex_input(z)
        _validate_finite_complex(c, "complex number")
        
        if c == 0:
            raise ComplexError("Phase is undefined for zero")
        
        phase_rad = cmath.phase(c)
        
        if unit.lower() == "radians":
            phase_result = phase_rad
        elif unit.lower() == "degrees":
            phase_result = math.degrees(phase_rad)
        else:
            raise ValidationError(f"Invalid unit: {unit}. Must be 'radians' or 'degrees'")
        
        return {
            "result": float(phase_result),
            "unit": unit,
            "operation": "complex_phase",
            "input": _complex_to_dict(c),
            "input_string": _format_complex_string(c)
        }
        
    except Exception as e:
        raise ComplexError(f"Error calculating complex phase: {e}") from e


def complex_conjugate(z: Union[complex, str, float, int, Dict[str, float]]) -> Dict[str, Any]:
    """Calculate the complex conjugate of a complex number."""
    try:
        c = _parse_complex_input(z)
        _validate_finite_complex(c, "complex number")
        
        conjugate = c.conjugate()
        
        return {
            "result": _complex_to_dict(conjugate),
            "result_string": _format_complex_string(conjugate),
            "operation": "complex_conjugate",
            "input": _complex_to_dict(c),
            "input_string": _format_complex_string(c)
        }
        
    except Exception as e:
        raise ComplexError(f"Error calculating complex conjugate: {e}") from e


# Coordinate Conversions
def rectangular_to_polar(z: Union[complex, str, float, int, Dict[str, float]], 
                        unit: str = "radians") -> Dict[str, Any]:
    """Convert complex number from rectangular to polar form."""
    try:
        c = _parse_complex_input(z)
        _validate_finite_complex(c, "complex number")
        
        magnitude = abs(c)
        
        if c == 0:
            phase = 0.0
        else:
            phase_rad = cmath.phase(c)
            if unit.lower() == "radians":
                phase = phase_rad
            elif unit.lower() == "degrees":
                phase = math.degrees(phase_rad)
            else:
                raise ValidationError(f"Invalid unit: {unit}. Must be 'radians' or 'degrees'")
        
        return {
            "result": {
                "magnitude": float(magnitude),
                "phase": float(phase),
                "unit": unit
            },
            "operation": "rectangular_to_polar",
            "input": _complex_to_dict(c),
            "input_string": _format_complex_string(c)
        }
        
    except Exception as e:
        raise ComplexError(f"Error converting to polar form: {e}") from e


def polar_to_rectangular(magnitude: Union[float, int], 
                        phase: Union[float, int], 
                        unit: str = "radians") -> Dict[str, Any]:
    """Convert complex number from polar to rectangular form."""
    try:
        mag = float(magnitude)
        ph = float(phase)
        
        if mag < 0:
            raise ValidationError("Magnitude must be non-negative")
        
        if not math.isfinite(mag) or not math.isfinite(ph):
            raise ValidationError("Magnitude and phase must be finite")
        
        # Convert phase to radians if necessary
        if unit.lower() == "radians":
            phase_rad = ph
        elif unit.lower() == "degrees":
            phase_rad = math.radians(ph)
        else:
            raise ValidationError(f"Invalid unit: {unit}. Must be 'radians' or 'degrees'")
        
        # Convert to rectangular form
        real_part = mag * math.cos(phase_rad)
        imag_part = mag * math.sin(phase_rad)
        
        result = complex(real_part, imag_part)
        _validate_finite_complex(result, "result")
        
        return {
            "result": _complex_to_dict(result),
            "result_string": _format_complex_string(result),
            "operation": "polar_to_rectangular",
            "input": {
                "magnitude": mag,
                "phase": ph,
                "unit": unit
            }
        }
        
    except Exception as e:
        raise ComplexError(f"Error converting from polar form: {e}") from e


# Complex Mathematical Functions
def complex_exp(z: Union[complex, str, float, int, Dict[str, float]]) -> Dict[str, Any]:
    """Calculate e^z for complex z."""
    try:
        c = _parse_complex_input(z)
        _validate_finite_complex(c, "complex number")
        
        # Check for potential overflow
        if c.real > 700:
            raise ComplexError("Real part too large for exponential calculation")
        
        result = cmath.exp(c)
        _validate_finite_complex(result, "result")
        
        return {
            "result": _complex_to_dict(result),
            "result_string": _format_complex_string(result),
            "operation": "complex_exponential",
            "input": _complex_to_dict(c),
            "input_string": _format_complex_string(c)
        }
        
    except Exception as e:
        raise ComplexError(f"Error calculating complex exponential: {e}") from e


def complex_log(z: Union[complex, str, float, int, Dict[str, float]], 
               base: Union[complex, str, float, int, Dict[str, float]] = None) -> Dict[str, Any]:
    """Calculate logarithm of complex number."""
    try:
        c = _parse_complex_input(z)
        _validate_finite_complex(c, "complex number")
        
        if c == 0:
            raise ComplexError("Logarithm of zero is undefined")
        
        if base is None:
            # Natural logarithm
            result = cmath.log(c)
            base_str = "e"
        else:
            # Logarithm with specified base
            base_c = _parse_complex_input(base)
            _validate_finite_complex(base_c, "base")
            
            if base_c == 0 or base_c == 1:
                raise ComplexError("Invalid logarithm base")
            
            result = cmath.log(c) / cmath.log(base_c)
            base_str = _format_complex_string(base_c)
        
        _validate_finite_complex(result, "result")
        
        return {
            "result": _complex_to_dict(result),
            "result_string": _format_complex_string(result),
            "operation": "complex_logarithm",
            "base": base_str,
            "input": _complex_to_dict(c),
            "input_string": _format_complex_string(c)
        }
        
    except Exception as e:
        raise ComplexError(f"Error calculating complex logarithm: {e}") from e


def complex_sqrt(z: Union[complex, str, float, int, Dict[str, float]]) -> Dict[str, Any]:
    """Calculate square root of complex number."""
    try:
        c = _parse_complex_input(z)
        _validate_finite_complex(c, "complex number")
        
        result = cmath.sqrt(c)
        _validate_finite_complex(result, "result")
        
        return {
            "result": _complex_to_dict(result),
            "result_string": _format_complex_string(result),
            "operation": "complex_square_root",
            "input": _complex_to_dict(c),
            "input_string": _format_complex_string(c)
        }
        
    except Exception as e:
        raise ComplexError(f"Error calculating complex square root: {e}") from e


def complex_sin(z: Union[complex, str, float, int, Dict[str, float]]) -> Dict[str, Any]:
    """Calculate sine of complex number."""
    try:
        c = _parse_complex_input(z)
        _validate_finite_complex(c, "complex number")
        
        result = cmath.sin(c)
        _validate_finite_complex(result, "result")
        
        return {
            "result": _complex_to_dict(result),
            "result_string": _format_complex_string(result),
            "operation": "complex_sine",
            "input": _complex_to_dict(c),
            "input_string": _format_complex_string(c)
        }
        
    except Exception as e:
        raise ComplexError(f"Error calculating complex sine: {e}") from e


def complex_cos(z: Union[complex, str, float, int, Dict[str, float]]) -> Dict[str, Any]:
    """Calculate cosine of complex number."""
    try:
        c = _parse_complex_input(z)
        _validate_finite_complex(c, "complex number")
        
        result = cmath.cos(c)
        _validate_finite_complex(result, "result")
        
        return {
            "result": _complex_to_dict(result),
            "result_string": _format_complex_string(result),
            "operation": "complex_cosine",
            "input": _complex_to_dict(c),
            "input_string": _format_complex_string(c)
        }
        
    except Exception as e:
        raise ComplexError(f"Error calculating complex cosine: {e}") from e


def complex_tan(z: Union[complex, str, float, int, Dict[str, float]]) -> Dict[str, Any]:
    """Calculate tangent of complex number."""
    try:
        c = _parse_complex_input(z)
        _validate_finite_complex(c, "complex number")
        
        result = cmath.tan(c)
        _validate_finite_complex(result, "result")
        
        return {
            "result": _complex_to_dict(result),
            "result_string": _format_complex_string(result),
            "operation": "complex_tangent",
            "input": _complex_to_dict(c),
            "input_string": _format_complex_string(c)
        }
        
    except Exception as e:
        raise ComplexError(f"Error calculating complex tangent: {e}") from e


# Utility Functions
def is_real(z: Union[complex, str, float, int, Dict[str, float]], 
           tolerance: float = 1e-15) -> Dict[str, Any]:
    """Check if a complex number is effectively real."""
    try:
        c = _parse_complex_input(z)
        _validate_finite_complex(c, "complex number")
        
        is_real_number = abs(c.imag) <= tolerance
        
        return {
            "result": bool(is_real_number),
            "tolerance": tolerance,
            "imaginary_part": float(c.imag),
            "operation": "is_real_check",
            "input": _complex_to_dict(c),
            "input_string": _format_complex_string(c)
        }
        
    except Exception as e:
        raise ComplexError(f"Error checking if complex number is real: {e}") from e


def is_imaginary(z: Union[complex, str, float, int, Dict[str, float]], 
                tolerance: float = 1e-15) -> Dict[str, Any]:
    """Check if a complex number is purely imaginary."""
    try:
        c = _parse_complex_input(z)
        _validate_finite_complex(c, "complex number")
        
        is_imaginary_number = abs(c.real) <= tolerance and abs(c.imag) > tolerance
        
        return {
            "result": bool(is_imaginary_number),
            "tolerance": tolerance,
            "real_part": float(c.real),
            "operation": "is_imaginary_check",
            "input": _complex_to_dict(c),
            "input_string": _format_complex_string(c)
        }
        
    except Exception as e:
        raise ComplexError(f"Error checking if complex number is imaginary: {e}") from e


# Function registry for dynamic access
COMPLEX_ARITHMETIC_FUNCTIONS = {
    'add': complex_add,
    'subtract': complex_subtract,
    'multiply': complex_multiply,
    'divide': complex_divide,
    'power': complex_power,
}

COMPLEX_PROPERTY_FUNCTIONS = {
    'magnitude': complex_magnitude,
    'abs': complex_magnitude,
    'phase': complex_phase,
    'arg': complex_phase,
    'argument': complex_phase,
    'conjugate': complex_conjugate,
}

COMPLEX_CONVERSION_FUNCTIONS = {
    'to_polar': rectangular_to_polar,
    'to_rectangular': polar_to_rectangular,
    'rectangular_to_polar': rectangular_to_polar,
    'polar_to_rectangular': polar_to_rectangular,
}

COMPLEX_MATH_FUNCTIONS = {
    'exp': complex_exp,
    'log': complex_log,
    'ln': complex_log,
    'sqrt': complex_sqrt,
    'sin': complex_sin,
    'cos': complex_cos,
    'tan': complex_tan,
}

COMPLEX_UTILITY_FUNCTIONS = {
    'is_real': is_real,
    'is_imaginary': is_imaginary,
}

ALL_COMPLEX_FUNCTIONS = {
    **COMPLEX_ARITHMETIC_FUNCTIONS,
    **COMPLEX_PROPERTY_FUNCTIONS,
    **COMPLEX_CONVERSION_FUNCTIONS,
    **COMPLEX_MATH_FUNCTIONS,
    **COMPLEX_UTILITY_FUNCTIONS,
}


def get_complex_function(function_name: str):
    """Get a complex function by name from the registry."""
    if function_name.lower() not in ALL_COMPLEX_FUNCTIONS:
        available_functions = ', '.join(sorted(ALL_COMPLEX_FUNCTIONS.keys()))
        raise ValidationError(
            f"Unknown complex function: {function_name}. "
            f"Available functions: {available_functions}"
        )
    return ALL_COMPLEX_FUNCTIONS[function_name.lower()]