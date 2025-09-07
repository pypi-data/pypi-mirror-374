"""Input validation utilities and decorators."""

import math
import re
from functools import wraps
from typing import Any, Callable, List, Optional, Union

import sympy as sp

from calculator.models.errors import ComputationError, ValidationError


def validate_finite_number(value: Union[int, float], name: str = "value") -> None:
    """Validate that a value is a finite number.

    Args:
        value: Value to validate
        name: Name of the parameter for error messages

    Raises:
        ValidationError: If value is not finite
    """
    if not isinstance(value, (int, float)):
        raise ValidationError(
            f"{name} must be a number, got {type(value).__name__}",
            field=name,
            value=value,
            suggestions=["Ensure the value is a numeric type (int or float)"],
        )

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


def validate_positive_number(value: Union[int, float], name: str = "value") -> None:
    """Validate that a value is a positive number.

    Args:
        value: Value to validate
        name: Name of the parameter for error messages

    Raises:
        ValidationError: If value is not positive
    """
    validate_finite_number(value, name)

    if value <= 0:
        raise ValidationError(
            f"{name} must be positive: {value}",
            field=name,
            value=value,
            suggestions=[f"Ensure {name} is greater than zero"],
        )


def validate_non_negative_number(value: Union[int, float], name: str = "value") -> None:
    """Validate that a value is non-negative.

    Args:
        value: Value to validate
        name: Name of the parameter for error messages

    Raises:
        ValidationError: If value is negative
    """
    validate_finite_number(value, name)

    if value < 0:
        raise ValidationError(
            f"{name} must be non-negative: {value}",
            field=name,
            value=value,
            suggestions=[f"Ensure {name} is zero or positive"],
        )


def validate_integer(value: Any, name: str = "value") -> int:
    """Validate and convert value to integer.

    Args:
        value: Value to validate and convert
        name: Name of the parameter for error messages

    Returns:
        Integer value

    Raises:
        ValidationError: If value cannot be converted to integer
    """
    try:
        if isinstance(value, bool):
            raise ValidationError(
                f"{name} cannot be a boolean",
                field=name,
                value=value,
                suggestions=["Use a numeric value instead of boolean"],
            )

        if isinstance(value, float):
            if not value.is_integer():
                raise ValidationError(
                    f"{name} must be an integer, got float with decimal part: {value}",
                    field=name,
                    value=value,
                    suggestions=["Use an integer value or round the float"],
                )
            return int(value)

        return int(value)
    except (ValueError, TypeError):
        raise ValidationError(
            f"{name} must be convertible to integer: {value}",
            field=name,
            value=value,
            suggestions=["Ensure the value is a valid integer"],
        )


def validate_range(
    value: Union[int, float],
    min_val: Optional[Union[int, float]] = None,
    max_val: Optional[Union[int, float]] = None,
    name: str = "value",
) -> None:
    """Validate that a value is within a specified range.

    Args:
        value: Value to validate
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)
        name: Name of the parameter for error messages

    Raises:
        ValidationError: If value is outside the range
    """
    validate_finite_number(value, name)

    if min_val is not None and value < min_val:
        raise ValidationError(
            f"{name} must be >= {min_val}, got {value}",
            field=name,
            value=value,
            suggestions=[f"Ensure {name} is at least {min_val}"],
        )

    if max_val is not None and value > max_val:
        raise ValidationError(
            f"{name} must be <= {max_val}, got {value}",
            field=name,
            value=value,
            suggestions=[f"Ensure {name} is at most {max_val}"],
        )


def validate_matrix(matrix: List[List[float]], name: str = "matrix") -> None:
    """Validate matrix structure and values.

    Args:
        matrix: Matrix to validate
        name: Name of the parameter for error messages

    Raises:
        ValidationError: If matrix is invalid
    """
    if not isinstance(matrix, list):
        raise ValidationError(
            f"{name} must be a list",
            field=name,
            value=type(matrix).__name__,
            suggestions=["Provide a list of lists representing the matrix"],
        )

    if not matrix:
        raise ValidationError(
            f"{name} cannot be empty", field=name, suggestions=["Provide a non-empty matrix"]
        )

    # Check that all rows are lists
    for i, row in enumerate(matrix):
        if not isinstance(row, list):
            raise ValidationError(
                f"{name} row {i} must be a list",
                field=f"{name}[{i}]",
                value=type(row).__name__,
                suggestions=["Ensure all matrix rows are lists"],
            )

    # Check dimensions consistency
    row_length = len(matrix[0])
    if row_length == 0:
        raise ValidationError(
            f"{name} rows cannot be empty",
            field=name,
            suggestions=["Provide non-empty matrix rows"],
        )

    for i, row in enumerate(matrix):
        if len(row) != row_length:
            raise ValidationError(
                f"{name} row {i} has length {len(row)}, expected {row_length}",
                field=f"{name}[{i}]",
                suggestions=["Ensure all matrix rows have the same length"],
            )

        # Check for finite values
        for j, value in enumerate(row):
            try:
                validate_finite_number(value, f"{name}[{i}][{j}]")
            except ValidationError as e:
                e.details[f"{name}_position"] = f"row {i}, column {j}"
                raise


def validate_matrix_dimensions_compatible(
    matrix_a: List[List[float]], matrix_b: List[List[float]], operation: str = "operation"
) -> None:
    """Validate that two matrices have compatible dimensions for the operation.

    Args:
        matrix_a: First matrix
        matrix_b: Second matrix
        operation: Type of operation for error messages

    Raises:
        ValidationError: If matrices are not compatible
    """
    validate_matrix(matrix_a, "matrix_a")
    validate_matrix(matrix_b, "matrix_b")

    rows_a, cols_a = len(matrix_a), len(matrix_a[0])
    rows_b, cols_b = len(matrix_b), len(matrix_b[0])

    if operation == "multiplication":
        if cols_a != rows_b:
            raise ValidationError(
                f"Matrix multiplication requires first matrix columns ({cols_a}) "
                f"to equal second matrix rows ({rows_b})",
                suggestions=[
                    "Check matrix dimensions for multiplication compatibility",
                    "Ensure first matrix columns = second matrix rows",
                ],
            )
    elif operation in ["addition", "subtraction"]:
        if rows_a != rows_b or cols_a != cols_b:
            raise ValidationError(
                f"Matrix {operation} requires same dimensions: "
                f"({rows_a}×{cols_a}) vs ({rows_b}×{cols_b})",
                suggestions=[
                    f"Ensure both matrices have the same dimensions for {operation}",
                    "Check that matrices have same number of rows and columns",
                ],
            )


def validate_square_matrix(matrix: List[List[float]], name: str = "matrix") -> None:
    """Validate that a matrix is square.

    Args:
        matrix: Matrix to validate
        name: Name of the parameter for error messages

    Raises:
        ValidationError: If matrix is not square
    """
    validate_matrix(matrix, name)

    rows, cols = len(matrix), len(matrix[0])
    if rows != cols:
        raise ValidationError(
            f"{name} must be square, got {rows}×{cols}",
            field=name,
            suggestions=[
                "Provide a square matrix (same number of rows and columns)",
                "Check matrix dimensions",
            ],
        )


def validate_mathematical_expression(expression: str, name: str = "expression") -> str:
    """Validate and sanitize a mathematical expression.

    Args:
        expression: Mathematical expression to validate
        name: Name of the parameter for error messages

    Returns:
        Sanitized expression

    Raises:
        ValidationError: If expression is invalid or dangerous
    """
    if not isinstance(expression, str):
        raise ValidationError(
            f"{name} must be a string",
            field=name,
            value=type(expression).__name__,
            suggestions=["Provide a string containing the mathematical expression"],
        )

    expression = expression.strip()
    if not expression:
        raise ValidationError(
            f"{name} cannot be empty",
            field=name,
            suggestions=["Provide a non-empty mathematical expression"],
        )

    # Check for dangerous patterns
    dangerous_patterns = [
        "__",
        "import",
        "exec",
        "eval",
        "open",
        "file",
        "input",
        "raw_input",
        "compile",
        "globals",
        "locals",
        "vars",
        "dir",
        "help",
        "copyright",
        "credits",
        "license",
        "quit",
        "exit",
    ]

    expression_lower = expression.lower()
    for pattern in dangerous_patterns:
        if pattern in expression_lower:
            raise ValidationError(
                f"{name} contains potentially dangerous pattern: {pattern}",
                field=name,
                value=expression,
                suggestions=[
                    "Remove dangerous function calls or keywords",
                    "Use only mathematical expressions and functions",
                ],
            )

    # Try to parse with SymPy to validate syntax
    try:
        # Replace common mathematical functions with SymPy equivalents
        sanitized = expression.replace("^", "**")  # Convert ^ to ** for power
        sp.sympify(sanitized, evaluate=False)
        return sanitized
    except (sp.SympifyError, ValueError, TypeError) as e:
        raise ValidationError(
            f"Invalid mathematical expression: {str(e)}",
            field=name,
            value=expression,
            suggestions=[
                "Check mathematical syntax and function names",
                "Ensure all parentheses are balanced",
                "Use supported mathematical functions and operators",
            ],
        )


def validate_variable_name(variable: str, name: str = "variable") -> str:
    """Validate a variable name for mathematical expressions.

    Args:
        variable: Variable name to validate
        name: Name of the parameter for error messages

    Returns:
        Validated variable name

    Raises:
        ValidationError: If variable name is invalid
    """
    if not isinstance(variable, str):
        raise ValidationError(
            f"{name} must be a string",
            field=name,
            value=type(variable).__name__,
            suggestions=["Provide a string containing the variable name"],
        )

    variable = variable.strip()
    if not variable:
        raise ValidationError(
            f"{name} cannot be empty",
            field=name,
            suggestions=["Provide a non-empty variable name"],
        )

    # Check variable name format (must start with letter, contain only letters, digits, underscore)
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", variable):
        raise ValidationError(
            f"Invalid variable name: {variable}",
            field=name,
            value=variable,
            suggestions=[
                "Variable names must start with a letter",
                "Use only letters, digits, and underscores",
                "Examples: x, y, theta, var_1",
            ],
        )

    # Check for reserved keywords
    reserved = [
        "and",
        "or",
        "not",
        "in",
        "is",
        "if",
        "else",
        "for",
        "while",
        "def",
        "class",
        "import",
        "from",
        "as",
        "try",
        "except",
        "finally",
        "with",
        "lambda",
        "global",
        "nonlocal",
        "True",
        "False",
        "None",
    ]

    if variable in reserved:
        raise ValidationError(
            f"Variable name cannot be a reserved keyword: {variable}",
            field=name,
            value=variable,
            suggestions=["Choose a different variable name", "Avoid Python reserved keywords"],
        )

    return variable


def validate_unit_type(unit_type: str, name: str = "unit_type") -> str:
    """Validate unit type for conversions.

    Args:
        unit_type: Unit type to validate
        name: Name of the parameter for error messages

    Returns:
        Validated unit type

    Raises:
        ValidationError: If unit type is not supported
    """
    if not isinstance(unit_type, str):
        raise ValidationError(
            f"{name} must be a string",
            field=name,
            value=type(unit_type).__name__,
            suggestions=["Provide a string containing the unit type"],
        )

    unit_type = unit_type.strip().lower()
    if not unit_type:
        raise ValidationError(
            f"{name} cannot be empty", field=name, suggestions=["Provide a non-empty unit type"]
        )

    supported_types = [
        "length",
        "weight",
        "mass",
        "temperature",
        "volume",
        "time",
        "energy",
        "pressure",
        "power",
        "frequency",
        "area",
        "speed",
        "velocity",
    ]

    if unit_type not in supported_types:
        raise ValidationError(
            f"Unsupported unit type: {unit_type}",
            field=name,
            value=unit_type,
            suggestions=[
                f"Use one of the supported unit types: {', '.join(supported_types)}",
                "Check spelling and formatting of unit type",
            ],
        )

    return unit_type


def validate_currency_code(currency: str, name: str = "currency") -> str:
    """Validate ISO 4217 currency code.

    Args:
        currency: Currency code to validate
        name: Name of the parameter for error messages

    Returns:
        Validated currency code

    Raises:
        ValidationError: If currency code is invalid
    """
    if not isinstance(currency, str):
        raise ValidationError(
            f"{name} must be a string",
            field=name,
            value=type(currency).__name__,
            suggestions=["Provide a string containing the currency code"],
        )

    currency = currency.strip().upper()
    if not currency:
        raise ValidationError(
            f"{name} cannot be empty",
            field=name,
            suggestions=["Provide a non-empty currency code"],
        )

    if len(currency) != 3:
        raise ValidationError(
            f"Currency code must be 3 characters long: {currency}",
            field=name,
            value=currency,
            suggestions=[
                "Use ISO 4217 currency codes (e.g., USD, EUR, GBP)",
                "Ensure currency code is exactly 3 characters",
            ],
        )

    if not currency.isalpha():
        raise ValidationError(
            f"Currency code must contain only letters: {currency}",
            field=name,
            value=currency,
            suggestions=[
                "Use only alphabetic characters in currency codes",
                "Examples: USD, EUR, GBP, JPY",
            ],
        )

    return currency


def validation_decorator(validator_func: Callable) -> Callable:
    """Decorator to apply validation to function arguments.

    Args:
        validator_func: Function that performs validation

    Returns:
        Decorator function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Apply validation
                validator_func(*args, **kwargs)
                return func(*args, **kwargs)
            except ValidationError:
                raise
            except Exception as e:
                raise ComputationError(f"Validation failed: {str(e)}", operation=func.__name__)

        return wrapper

    return decorator


def validate_data_list(data: List[float], name: str = "data") -> List[float]:
    """Validate a list of numerical data.

    Args:
        data: List of numbers to validate
        name: Name of the parameter for error messages

    Returns:
        Validated data list

    Raises:
        ValidationError: If data is invalid
    """
    if not isinstance(data, list):
        raise ValidationError(
            f"{name} must be a list",
            field=name,
            value=type(data).__name__,
            suggestions=["Provide a list of numbers"],
        )

    if not data:
        raise ValidationError(
            f"{name} cannot be empty",
            field=name,
            suggestions=["Provide a non-empty list of numbers"],
        )

    if len(data) > 10000:
        raise ValidationError(
            f"{name} is too large (maximum 10,000 items): {len(data)}",
            field=name,
            value=len(data),
            suggestions=["Reduce the size of the dataset", "Process data in smaller batches"],
        )

    validated_data = []
    for i, value in enumerate(data):
        try:
            validate_finite_number(value, f"{name}[{i}]")
            validated_data.append(float(value))
        except ValidationError as e:
            e.details[f"{name}_index"] = i
            raise

    return validated_data
