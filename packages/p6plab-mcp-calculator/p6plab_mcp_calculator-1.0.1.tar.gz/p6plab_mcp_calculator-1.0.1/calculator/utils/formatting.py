"""
Output formatting utilities for the Scientific Calculator MCP Server.

This module provides consistent formatting for mathematical results, error messages,
and various output types across all calculator tools.
"""

import math
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union
import numpy as np


def format_number(
    value: Union[float, int, Decimal, complex],
    precision: int = 15,
    scientific_threshold: float = 1e6,
    use_scientific: bool = False
) -> str:
    """
    Format a number with appropriate precision and notation.
    
    Args:
        value: The number to format
        precision: Number of significant digits
        scientific_threshold: Threshold for automatic scientific notation
        use_scientific: Force scientific notation
        
    Returns:
        Formatted number string
    """
    if isinstance(value, complex):
        return format_complex_number(value, precision)
    
    if value == 0:
        return "0"
    
    # Convert to float for processing
    if isinstance(value, Decimal):
        float_val = float(value)
    else:
        float_val = float(value)
    
    # Check for infinity and NaN
    if math.isinf(float_val):
        return "∞" if float_val > 0 else "-∞"
    if math.isnan(float_val):
        return "NaN"
    
    # Determine if scientific notation should be used
    abs_val = abs(float_val)
    should_use_scientific = (
        use_scientific or 
        abs_val >= scientific_threshold or 
        (abs_val != 0 and abs_val < 1e-4)
    )
    
    if should_use_scientific:
        return f"{float_val:.{precision-1}e}"
    else:
        # Format with appropriate decimal places
        if abs_val >= 1:
            decimal_places = max(0, precision - len(str(int(abs_val))))
        else:
            # For numbers less than 1, count leading zeros
            decimal_places = precision + abs(math.floor(math.log10(abs_val))) - 1
        
        formatted = f"{float_val:.{decimal_places}f}"
        # Remove trailing zeros
        if '.' in formatted:
            formatted = formatted.rstrip('0').rstrip('.')
        
        return formatted


def format_complex_number(
    value: complex,
    precision: int = 15
) -> str:
    """
    Format a complex number in standard mathematical notation.
    
    Args:
        value: Complex number to format
        precision: Number of significant digits
        
    Returns:
        Formatted complex number string
    """
    real_part = format_number(value.real, precision)
    imag_part = format_number(abs(value.imag), precision)
    
    if value.imag == 0:
        return real_part
    elif value.real == 0:
        if value.imag == 1:
            return "i"
        elif value.imag == -1:
            return "-i"
        else:
            sign = "-" if value.imag < 0 else ""
            return f"{sign}{imag_part}i"
    else:
        if value.imag == 1:
            return f"{real_part} + i"
        elif value.imag == -1:
            return f"{real_part} - i"
        else:
            sign = "+" if value.imag >= 0 else "-"
            return f"{real_part} {sign} {imag_part}i"


def format_matrix(
    matrix: Union[List[List[float]], np.ndarray],
    precision: int = 6,
    max_width: int = 80
) -> str:
    """
    Format a matrix for display.
    
    Args:
        matrix: Matrix to format
        precision: Number of decimal places
        max_width: Maximum display width
        
    Returns:
        Formatted matrix string
    """
    if isinstance(matrix, np.ndarray):
        matrix = matrix.tolist()
    
    if not matrix or not matrix[0]:
        return "[]"
    
    rows, cols = len(matrix), len(matrix[0])
    
    # Format all elements
    formatted_elements = []
    max_element_width = 0
    
    for row in matrix:
        formatted_row = []
        for element in row:
            formatted = format_number(element, precision)
            formatted_row.append(formatted)
            max_element_width = max(max_element_width, len(formatted))
        formatted_elements.append(formatted_row)
    
    # Check if matrix fits in one line
    total_width = cols * (max_element_width + 2) + 2  # +2 for brackets
    
    if total_width <= max_width and rows <= 3:
        # Single line format for small matrices
        lines = []
        for row in formatted_elements:
            padded_row = [elem.rjust(max_element_width) for elem in row]
            lines.append("[" + ", ".join(padded_row) + "]")
        return "[" + ", ".join(lines) + "]"
    else:
        # Multi-line format
        lines = []
        for i, row in enumerate(formatted_elements):
            padded_row = [elem.rjust(max_element_width) for elem in row]
            if i == 0:
                lines.append("⎡" + " ".join(padded_row) + "⎤")
            elif i == rows - 1:
                lines.append("⎣" + " ".join(padded_row) + "⎦")
            else:
                lines.append("⎢" + " ".join(padded_row) + "⎥")
        return "\n".join(lines)


def format_vector(
    vector: Union[List[float], np.ndarray],
    precision: int = 6,
    orientation: str = "column"
) -> str:
    """
    Format a vector for display.
    
    Args:
        vector: Vector to format
        precision: Number of decimal places
        orientation: "column" or "row"
        
    Returns:
        Formatted vector string
    """
    if isinstance(vector, np.ndarray):
        vector = vector.tolist()
    
    formatted_elements = [format_number(elem, precision) for elem in vector]
    
    if orientation == "row":
        return "[" + ", ".join(formatted_elements) + "]"
    else:
        max_width = max(len(elem) for elem in formatted_elements)
        lines = []
        for i, elem in enumerate(formatted_elements):
            padded = elem.rjust(max_width)
            if i == 0:
                lines.append("⎡" + padded + "⎤")
            elif i == len(formatted_elements) - 1:
                lines.append("⎣" + padded + "⎦")
            else:
                lines.append("⎢" + padded + "⎥")
        return "\n".join(lines)


def format_statistical_summary(
    stats: Dict[str, float],
    precision: int = 6
) -> str:
    """
    Format statistical summary for display.
    
    Args:
        stats: Dictionary of statistical measures
        precision: Number of decimal places
        
    Returns:
        Formatted statistical summary
    """
    lines = []
    
    # Define order and labels for common statistics
    stat_order = [
        ("count", "Count"),
        ("mean", "Mean"),
        ("median", "Median"),
        ("mode", "Mode"),
        ("std_dev", "Standard Deviation"),
        ("variance", "Variance"),
        ("min", "Minimum"),
        ("max", "Maximum"),
        ("range", "Range"),
        ("q1", "Q1 (25th percentile)"),
        ("q3", "Q3 (75th percentile)"),
        ("iqr", "Interquartile Range"),
        ("skewness", "Skewness"),
        ("kurtosis", "Kurtosis")
    ]
    
    # Find maximum label width for alignment
    max_label_width = max(len(label) for _, label in stat_order if _ in stats)
    
    for key, label in stat_order:
        if key in stats:
            value = stats[key]
            if isinstance(value, (int, float)):
                formatted_value = format_number(value, precision)
            else:
                formatted_value = str(value)
            
            lines.append(f"{label:<{max_label_width}}: {formatted_value}")
    
    # Add any additional statistics not in the standard order
    for key, value in stats.items():
        if key not in [k for k, _ in stat_order]:
            if isinstance(value, (int, float)):
                formatted_value = format_number(value, precision)
            else:
                formatted_value = str(value)
            
            label = key.replace('_', ' ').title()
            lines.append(f"{label:<{max_label_width}}: {formatted_value}")
    
    return "\n".join(lines)


def format_equation_solution(
    solutions: List[Union[float, complex]],
    equation: str = "",
    precision: int = 10
) -> str:
    """
    Format equation solutions for display.
    
    Args:
        solutions: List of solutions
        equation: Original equation (optional)
        precision: Number of decimal places
        
    Returns:
        Formatted solution string
    """
    lines = []
    
    if equation:
        lines.append(f"Solutions for: {equation}")
        lines.append("-" * (len(equation) + 15))
    
    if not solutions:
        lines.append("No solutions found")
    elif len(solutions) == 1:
        solution = format_number(solutions[0], precision)
        lines.append(f"Solution: {solution}")
    else:
        for i, sol in enumerate(solutions, 1):
            formatted_sol = format_number(sol, precision)
            lines.append(f"Solution {i}: {formatted_sol}")
    
    return "\n".join(lines)


def format_unit_conversion(
    value: float,
    from_unit: str,
    to_unit: str,
    result: float,
    precision: int = 10
) -> str:
    """
    Format unit conversion result.
    
    Args:
        value: Original value
        from_unit: Source unit
        to_unit: Target unit
        result: Converted value
        precision: Number of decimal places
        
    Returns:
        Formatted conversion string
    """
    formatted_value = format_number(value, precision)
    formatted_result = format_number(result, precision)
    
    return f"{formatted_value} {from_unit} = {formatted_result} {to_unit}"


def format_error_message(
    error_type: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    suggestions: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Format error message with consistent structure.
    
    Args:
        error_type: Type of error
        message: Error message
        details: Additional error details
        suggestions: Suggested solutions
        
    Returns:
        Formatted error dictionary
    """
    error_dict = {
        "error": {
            "type": error_type,
            "message": message
        }
    }
    
    if details:
        error_dict["error"]["details"] = details
    
    if suggestions:
        error_dict["error"]["suggestions"] = suggestions
    
    return error_dict


def format_calculation_result(
    result: Any,
    operation: str,
    operands: Optional[Dict[str, Any]] = None,
    precision: int = 15,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Format calculation result with metadata.
    
    Args:
        result: Calculation result
        operation: Operation performed
        operands: Input operands
        precision: Number precision
        metadata: Additional metadata
        
    Returns:
        Formatted result dictionary
    """
    # Format the result based on its type
    if isinstance(result, (list, np.ndarray)):
        if isinstance(result, np.ndarray) and result.ndim == 2:
            formatted_result = result.tolist()
            display_result = format_matrix(result, precision)
        else:
            formatted_result = result.tolist() if isinstance(result, np.ndarray) else result
            display_result = format_vector(formatted_result, precision)
    elif isinstance(result, complex):
        formatted_result = {"real": result.real, "imag": result.imag}
        display_result = format_complex_number(result, precision)
    elif isinstance(result, dict):
        formatted_result = result
        display_result = str(result)
    else:
        formatted_result = float(result) if isinstance(result, Decimal) else result
        display_result = format_number(result, precision)
    
    result_dict = {
        "result": formatted_result,
        "display": display_result,
        "operation": operation,
        "precision": precision
    }
    
    if operands:
        result_dict["operands"] = operands
    
    if metadata:
        result_dict["metadata"] = metadata
    
    return result_dict


def format_percentage(value: float, precision: int = 2) -> str:
    """
    Format a value as a percentage.
    
    Args:
        value: Value to format (0.1 = 10%)
        precision: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    percentage = value * 100
    return f"{percentage:.{precision}f}%"


def format_currency(
    amount: float,
    currency: str = "USD",
    precision: int = 2
) -> str:
    """
    Format a monetary amount.
    
    Args:
        amount: Amount to format
        currency: Currency code
        precision: Number of decimal places
        
    Returns:
        Formatted currency string
    """
    formatted_amount = f"{amount:,.{precision}f}"
    
    # Common currency symbols
    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "CNY": "¥",
        "INR": "₹"
    }
    
    symbol = symbols.get(currency, currency)
    
    if currency in ["USD", "EUR", "GBP"]:
        return f"{symbol}{formatted_amount}"
    else:
        return f"{formatted_amount} {symbol}"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 1e-6:
        return f"{seconds * 1e9:.1f} ns"
    elif seconds < 1e-3:
        return f"{seconds * 1e6:.1f} μs"
    elif seconds < 1:
        return f"{seconds * 1e3:.1f} ms"
    elif seconds < 60:
        return f"{seconds:.2f} s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}h {minutes}m {secs:.1f}s"