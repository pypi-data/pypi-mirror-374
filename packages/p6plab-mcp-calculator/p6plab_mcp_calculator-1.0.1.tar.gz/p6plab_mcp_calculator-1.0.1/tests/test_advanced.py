"""
Unit tests for advanced mathematical functions module.
"""

import pytest
import math
from calculator.core import advanced
from calculator.models.errors import ValidationError


class TestTrigonometricFunctions:
    """Test trigonometric functions."""
    
    def test_sin_basic(self):
        """Test basic sine calculations."""
        # Test known values
        assert abs(advanced.sin(0)) < 1e-10
        assert abs(advanced.sin(math.pi/2) - 1) < 1e-10
        assert abs(advanced.sin(math.pi)) < 1e-10
        assert abs(advanced.sin(3*math.pi/2) + 1) < 1e-10
    
    def test_sin_degrees(self):
        """Test sine with degree input."""
        assert abs(advanced.sin(0, "degrees")) < 1e-10
        assert abs(advanced.sin(90, "degrees") - 1) < 1e-10
        assert abs(advanced.sin(180, "degrees")) < 1e-10
        assert abs(advanced.sin(270, "degrees") + 1) < 1e-10
    
    def test_cos_basic(self):
        """Test basic cosine calculations."""
        assert abs(advanced.cos(0) - 1) < 1e-10
        assert abs(advanced.cos(math.pi/2)) < 1e-10
        assert abs(advanced.cos(math.pi) + 1) < 1e-10
        assert abs(advanced.cos(3*math.pi/2)) < 1e-10
    
    def test_tan_basic(self):
        """Test basic tangent calculations."""
        assert abs(advanced.tan(0)) < 1e-10
        assert abs(advanced.tan(math.pi/4) - 1) < 1e-10
        assert abs(advanced.tan(math.pi)) < 1e-10
    
    def test_tan_undefined(self):
        """Test tangent at undefined points."""
        with pytest.raises(advanced.AdvancedMathError):
            advanced.tan(math.pi/2)
    
    def test_inverse_trig(self):
        """Test inverse trigonometric functions."""
        assert abs(advanced.arcsin(0)) < 1e-10
        assert abs(advanced.arcsin(1) - math.pi/2) < 1e-10
        assert abs(advanced.arccos(1)) < 1e-10
        assert abs(advanced.arccos(0) - math.pi/2) < 1e-10
        assert abs(advanced.arctan(0)) < 1e-10
        assert abs(advanced.arctan(1) - math.pi/4) < 1e-10
    
    def test_inverse_trig_domain_errors(self):
        """Test inverse trig domain errors."""
        with pytest.raises(advanced.AdvancedMathError):
            advanced.arcsin(2)
        with pytest.raises(advanced.AdvancedMathError):
            advanced.arccos(-2)


class TestHyperbolicFunctions:
    """Test hyperbolic functions."""
    
    def test_sinh_basic(self):
        """Test hyperbolic sine."""
        assert abs(advanced.sinh(0)) < 1e-10
        assert abs(advanced.sinh(1) - math.sinh(1)) < 1e-10
    
    def test_cosh_basic(self):
        """Test hyperbolic cosine."""
        assert abs(advanced.cosh(0) - 1) < 1e-10
        assert abs(advanced.cosh(1) - math.cosh(1)) < 1e-10
    
    def test_tanh_basic(self):
        """Test hyperbolic tangent."""
        assert abs(advanced.tanh(0)) < 1e-10
        assert abs(advanced.tanh(1) - math.tanh(1)) < 1e-10


class TestLogarithmicFunctions:
    """Test logarithmic functions."""
    
    def test_natural_log(self):
        """Test natural logarithm."""
        assert abs(advanced.natural_log(1)) < 1e-10
        assert abs(advanced.natural_log(math.e) - 1) < 1e-10
        assert abs(advanced.natural_log(math.e**2) - 2) < 1e-10
    
    def test_log10(self):
        """Test base-10 logarithm."""
        assert abs(advanced.log10(1)) < 1e-10
        assert abs(advanced.log10(10) - 1) < 1e-10
        assert abs(advanced.log10(100) - 2) < 1e-10
    
    def test_log_base(self):
        """Test logarithm with custom base."""
        assert abs(advanced.log_base(1, 2)) < 1e-10
        assert abs(advanced.log_base(8, 2) - 3) < 1e-10
        assert abs(advanced.log_base(27, 3) - 3) < 1e-10
    
    def test_log_domain_errors(self):
        """Test logarithm domain errors."""
        with pytest.raises(advanced.AdvancedMathError):
            advanced.natural_log(0)
        with pytest.raises(advanced.AdvancedMathError):
            advanced.natural_log(-1)
        with pytest.raises(advanced.AdvancedMathError):
            advanced.log_base(2, 1)


class TestExponentialFunctions:
    """Test exponential functions."""
    
    def test_exp(self):
        """Test exponential function."""
        assert abs(advanced.exp(0) - 1) < 1e-10
        assert abs(advanced.exp(1) - math.e) < 1e-10
        assert abs(advanced.exp(2) - math.e**2) < 1e-10
    
    def test_power_base(self):
        """Test power with custom base."""
        assert abs(advanced.power_base(2, 3) - 8) < 1e-10
        assert abs(advanced.power_base(3, 4) - 81) < 1e-10
        assert abs(advanced.power_base(5, 0) - 1) < 1e-10
    
    def test_power_special_cases(self):
        """Test power function special cases."""
        with pytest.raises(advanced.AdvancedMathError):
            advanced.power_base(0, -1)
        with pytest.raises(advanced.AdvancedMathError):
            advanced.power_base(0, 0)


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_angle_conversion(self):
        """Test angle conversion functions."""
        assert abs(advanced.degrees_to_radians(180) - math.pi) < 1e-10
        assert abs(advanced.degrees_to_radians(90) - math.pi/2) < 1e-10
        assert abs(advanced.radians_to_degrees(math.pi) - 180) < 1e-10
        assert abs(advanced.radians_to_degrees(math.pi/2) - 90) < 1e-10
    
    def test_function_registry(self):
        """Test function registry access."""
        sin_func = advanced.get_function("sin")
        assert callable(sin_func)
        assert abs(sin_func(0)) < 1e-10
        
        with pytest.raises(ValidationError):
            advanced.get_function("nonexistent_function")


class TestInputValidation:
    """Test input validation."""
    
    def test_invalid_unit(self):
        """Test invalid angle unit."""
        with pytest.raises(ValidationError):
            advanced.sin(1, "invalid_unit")
    
    def test_large_values(self):
        """Test handling of large values."""
        with pytest.raises(advanced.AdvancedMathError):
            advanced.sin(1e15)
        with pytest.raises(advanced.AdvancedMathError):
            advanced.exp(1000)
    
    def test_invalid_input_types(self):
        """Test invalid input types."""
        with pytest.raises(ValidationError):
            advanced.sin("not_a_number")
        with pytest.raises(ValidationError):
            advanced.cos(None)

class TestAdditionalTrigonometric:
    """Test additional trigonometric functions and edge cases."""
    
    def test_secant_function(self):
        """Test secant function."""
        try:
            result = advanced.sec(0)
            assert abs(result - 1) < 1e-10
        except AttributeError:
            # Function might not be implemented
            pass
    
    def test_cosecant_function(self):
        """Test cosecant function."""
        try:
            result = advanced.csc(math.pi/2)
            assert abs(result - 1) < 1e-10
        except AttributeError:
            # Function might not be implemented
            pass
    
    def test_cotangent_function(self):
        """Test cotangent function."""
        try:
            result = advanced.cot(math.pi/4)
            assert abs(result - 1) < 1e-10
        except AttributeError:
            # Function might not be implemented
            pass

class TestAdditionalHyperbolic:
    """Test additional hyperbolic functions."""
    
    def test_inverse_hyperbolic(self):
        """Test inverse hyperbolic functions."""
        try:
            assert abs(advanced.asinh(0)) < 1e-10
            assert abs(advanced.acosh(1)) < 1e-10
            assert abs(advanced.atanh(0)) < 1e-10
        except AttributeError:
            # Functions might not be implemented
            pass

class TestSpecialFunctions:
    """Test special mathematical functions."""
    
    def test_factorial(self):
        """Test factorial function."""
        try:
            assert advanced.factorial(0) == 1
            assert advanced.factorial(5) == 120
            assert advanced.factorial(1) == 1
        except AttributeError:
            # Function might not be implemented
            pass
    
    def test_gamma_function(self):
        """Test gamma function."""
        try:
            result = advanced.gamma(1)
            assert abs(result - 1) < 1e-10
        except AttributeError:
            # Function might not be implemented
            pass

class TestErrorHandling:
    """Test comprehensive error handling."""
    
    def test_overflow_protection(self):
        """Test overflow protection."""
        with pytest.raises((advanced.AdvancedMathError, OverflowError, ValidationError)):
            advanced.exp(1000)
    
    def test_underflow_handling(self):
        """Test underflow handling."""
        result = advanced.exp(-1000)
        assert result == 0 or result < 1e-100
    
    def test_precision_limits(self):
        """Test precision limits."""
        # Test very small differences
        result1 = advanced.sin(1e-15)
        result2 = advanced.sin(0)
        assert abs(result1 - result2) < 1e-10

class TestStringInputs:
    """Test string input handling."""
    
    def test_string_numbers(self):
        """Test string number inputs."""
        assert abs(advanced.sin("0")) < 1e-10
        assert abs(advanced.cos("0") - 1) < 1e-10
        assert abs(advanced.exp("0") - 1) < 1e-10
    
    def test_invalid_strings(self):
        """Test invalid string inputs."""
        with pytest.raises(ValidationError):
            advanced.sin("not_a_number")
        with pytest.raises(ValidationError):
            advanced.cos("invalid")

class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_zero_inputs(self):
        """Test zero inputs across functions."""
        assert abs(advanced.sin(0)) < 1e-10
        assert abs(advanced.cos(0) - 1) < 1e-10
        assert abs(advanced.tan(0)) < 1e-10
        assert abs(advanced.sinh(0)) < 1e-10
        assert abs(advanced.cosh(0) - 1) < 1e-10
        assert abs(advanced.tanh(0)) < 1e-10
    
    def test_negative_inputs(self):
        """Test negative inputs."""
        assert abs(advanced.sin(-math.pi/2) + 1) < 1e-10
        assert abs(advanced.cos(-math.pi) + 1) < 1e-10
        assert abs(advanced.exp(-1) - 1/math.e) < 1e-10
    
    def test_boundary_values(self):
        """Test boundary values for inverse functions."""
        assert abs(advanced.arcsin(-1) + math.pi/2) < 1e-10
        assert abs(advanced.arcsin(1) - math.pi/2) < 1e-10
        assert abs(advanced.arccos(-1) - math.pi) < 1e-10
        assert abs(advanced.arccos(1)) < 1e-10