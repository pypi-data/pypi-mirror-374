"""Unit tests for basic arithmetic operations."""

import pytest
from calculator.core.basic import add, subtract, multiply, divide, power, square_root
from calculator.models.errors import ValidationError, ComputationError


class TestBasicOperations:
    """Test basic arithmetic operations."""

    def test_add_positive_numbers(self):
        """Test addition of positive numbers."""
        result = add(2.5, 3.7)
        assert result["result"] == 6.2
        assert result["operation"] == "addition"
        assert result["success"] is True

    def test_add_negative_numbers(self):
        """Test addition with negative numbers."""
        result = add(-2.5, 3.7)
        assert result["result"] == 1.2
        assert result["success"] is True

    def test_subtract_numbers(self):
        """Test subtraction of numbers."""
        result = subtract(10.0, 3.0)
        assert result["result"] == 7.0
        assert result["operation"] == "subtraction"
        assert result["success"] is True

    def test_multiply_numbers(self):
        """Test multiplication of numbers."""
        result = multiply(4.0, 2.5)
        assert result["result"] == 10.0
        assert result["operation"] == "multiplication"
        assert result["success"] is True

    def test_divide_numbers(self):
        """Test division of numbers."""
        result = divide(10.0, 2.0)
        assert result["result"] == 5.0
        assert result["operation"] == "division"
        assert result["success"] is True

    def test_divide_by_zero(self):
        """Test division by zero raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            divide(10.0, 0.0)
        assert "Division by zero" in str(exc_info.value)

    def test_power_operation(self):
        """Test power operation."""
        result = power(2.0, 3.0)
        assert result["result"] == 8.0
        assert result["operation"] == "exponentiation"
        assert result["success"] is True

    def test_square_root(self):
        """Test square root operation."""
        result = square_root(16.0)
        assert result["result"] == 4.0
        assert result["operation"] == "square_root"
        assert result["success"] is True

    def test_square_root_negative(self):
        """Test square root of negative number raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            square_root(-4.0)
        assert "negative number" in str(exc_info.value)

    def test_precision_handling(self):
        """Test high precision calculations."""
        result = add(0.1, 0.2)
        # Should handle floating point precision issues
        assert abs(result["result"] - 0.3) < 1e-10
        assert result["precision"] == 15

    def test_large_numbers(self):
        """Test operations with large numbers."""
        result = multiply(1e10, 1e10)
        assert result["result"] == 1e20
        assert result["success"] is True

    def test_small_numbers(self):
        """Test operations with very small numbers."""
        result = add(1e-10, 1e-10)
        assert result["result"] == 2e-10
        assert result["success"] is True

    def test_add_with_strings(self):
        """Test addition with string inputs."""
        result = add("2.5", "3.7")
        assert result["result"] == 6.2
        assert result["success"] is True

    def test_add_with_invalid_input(self):
        """Test addition with invalid input."""
        with pytest.raises(ValidationError):
            add("invalid", 3.7)

    def test_subtract_with_strings(self):
        """Test subtraction with string inputs."""
        result = subtract("10.0", "3.0")
        assert result["result"] == 7.0
        assert result["success"] is True

    def test_multiply_with_zero(self):
        """Test multiplication with zero."""
        result = multiply(5.0, 0.0)
        assert result["result"] == 0.0
        assert result["success"] is True

    def test_multiply_with_strings(self):
        """Test multiplication with string inputs."""
        result = multiply("4.0", "2.5")
        assert result["result"] == 10.0
        assert result["success"] is True

    def test_divide_with_strings(self):
        """Test division with string inputs."""
        result = divide("10.0", "2.0")
        assert result["result"] == 5.0
        assert result["success"] is True

    def test_power_with_strings(self):
        """Test power operation with string inputs."""
        result = power("2.0", "3.0")
        assert result["result"] == 8.0
        assert result["success"] is True

    def test_power_with_zero_exponent(self):
        """Test power operation with zero exponent."""
        result = power(5.0, 0.0)
        assert result["result"] == 1.0
        assert result["success"] is True

    def test_power_with_negative_exponent(self):
        """Test power operation with negative exponent."""
        result = power(2.0, -2.0)
        assert result["result"] == 0.25
        assert result["success"] is True

    def test_square_root_with_string(self):
        """Test square root with string input."""
        result = square_root("9.0")
        assert result["result"] == 3.0
        assert result["success"] is True

    def test_square_root_of_zero(self):
        """Test square root of zero."""
        result = square_root(0.0)
        assert result["result"] == 0.0
        assert result["success"] is True

    def test_operations_with_infinity(self):
        """Test operations with infinity values."""
        with pytest.raises(ValidationError):
            add(float('inf'), 1.0)

    def test_operations_with_nan(self):
        """Test operations with NaN values."""
        with pytest.raises(ValidationError):
            add(float('nan'), 1.0)

    def test_very_large_numbers(self):
        """Test operations with very large numbers."""
        result = add(1e100, 1e100)
        assert result["result"] == 2e100
        assert result["success"] is True

    def test_very_small_numbers(self):
        """Test operations with very small numbers."""
        result = add(1e-100, 1e-100)
        assert result["result"] == 2e-100
        assert result["success"] is True

    def test_decimal_precision(self):
        """Test decimal precision handling."""
        result = add(0.1, 0.2)
        # Should handle floating point precision issues
        assert abs(result["result"] - 0.3) < 1e-10
        assert result["success"] is True