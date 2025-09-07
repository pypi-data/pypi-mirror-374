"""
Calculus operations module for the Scientific Calculator MCP Server.

This module provides symbolic and numerical calculus operations including
differentiation, integration, and multi-variable calculus using SymPy and SciPy.
"""

from typing import Union, Dict, Any, List, Optional, Tuple
import sympy as sp
from sympy import symbols, sympify, diff, integrate, limit, series
from sympy.parsing.sympy_parser import parse_expr
import numpy as np
from scipy import integrate as scipy_integrate
from scipy.optimize import minimize_scalar

from calculator.models.errors import CalculatorError, ValidationError


class CalculusError(CalculatorError):
    """Error for calculus operations."""
    pass


def _validate_expression(expression: str) -> sp.Expr:
    """Validate and parse mathematical expression using SymPy."""
    try:
        # Clean the expression
        cleaned_expr = expression.strip()
        if not cleaned_expr:
            raise ValueError("Expression cannot be empty")
        
        # Parse the expression
        parsed_expr = parse_expr(cleaned_expr, transformations='all')
        
        # Check if the expression is valid
        if parsed_expr is None:
            raise ValueError("Failed to parse expression")
        
        return parsed_expr
        
    except Exception as e:
        raise ValidationError(f"Invalid mathematical expression '{expression}': {e}") from e


def _validate_variable(variable: str) -> sp.Symbol:
    """Validate and create a SymPy symbol for a variable."""
    try:
        if not variable or not isinstance(variable, str):
            raise ValueError("Variable must be a non-empty string")
        
        # Check if variable name is valid
        if not variable.isalpha() or len(variable) > 10:
            raise ValueError("Variable must be alphabetic and at most 10 characters")
        
        return symbols(variable)
        
    except Exception as e:
        raise ValidationError(f"Invalid variable '{variable}': {e}") from e


def _validate_numeric_bounds(lower: Union[float, int, str], 
                           upper: Union[float, int, str]) -> Tuple[Union[float, Any], Union[float, Any]]:
    """Validate and convert integration bounds."""
    try:
        # Handle infinity bounds
        if isinstance(lower, str):
            if lower.lower() in ['inf', 'infinity', '+inf', '+infinity']:
                lower_bound = sp.oo
            elif lower.lower() in ['-inf', '-infinity']:
                lower_bound = -sp.oo
            else:
                lower_bound = float(lower)
        else:
            lower_bound = float(lower)
        
        if isinstance(upper, str):
            if upper.lower() in ['inf', 'infinity', '+inf', '+infinity']:
                upper_bound = sp.oo
            elif upper.lower() in ['-inf', '-infinity']:
                upper_bound = -sp.oo
            else:
                upper_bound = float(upper)
        else:
            upper_bound = float(upper)
        
        # Check bounds order (except for infinite bounds)
        if (isinstance(lower_bound, (int, float)) and isinstance(upper_bound, (int, float)) 
            and lower_bound >= upper_bound):
            raise ValueError("Lower bound must be less than upper bound")
        
        return lower_bound, upper_bound
        
    except Exception as e:
        raise ValidationError(f"Invalid bounds: {e}") from e


# Symbolic Differentiation
def symbolic_derivative(expression: str, variable: str, order: int = 1) -> Dict[str, Any]:
    """Calculate symbolic derivative of an expression."""
    try:
        if order < 1 or order > 10:
            raise ValidationError("Derivative order must be between 1 and 10")
        
        expr = _validate_expression(expression)
        var = _validate_variable(variable)
        
        # Check if variable is in the expression
        if var not in expr.free_symbols:
            # If variable not in expression, derivative is 0
            derivative_expr = sp.Integer(0)
        else:
            # Calculate derivative
            derivative_expr = diff(expr, var, order)
        
        # Convert to string representation
        derivative_str = str(derivative_expr)
        
        # Try to simplify
        try:
            simplified = sp.simplify(derivative_expr)
            simplified_str = str(simplified)
        except:
            simplified = derivative_expr
            simplified_str = derivative_str
        
        # Try to convert to number when possible
        try:
            if simplified.is_number:
                derivative_value = float(simplified)
            else:
                derivative_value = simplified_str
        except:
            derivative_value = simplified_str
        
        return {
            "derivative": derivative_value,  # Number when possible, string otherwise
            "derivative_str": derivative_str,  # String representation
            "simplified": simplified_str,
            "original_expression": expression,
            "variable": variable,
            "order": order,
            "operation": "symbolic_derivative"
        }
        
    except Exception as e:
        raise CalculusError(f"Error calculating symbolic derivative: {e}") from e


def partial_derivative(expression: str, variable: str, order: int = 1) -> Dict[str, Any]:
    """Calculate partial derivative of a multi-variable expression."""
    try:
        if order < 1 or order > 10:
            raise ValidationError("Derivative order must be between 1 and 10")
        
        expr = _validate_expression(expression)
        var = _validate_variable(variable)
        
        # Calculate partial derivative
        if var not in expr.free_symbols:
            partial_expr = sp.Integer(0)
        else:
            partial_expr = diff(expr, var, order)
        
        # Convert to string representation
        partial_str = str(partial_expr)
        
        # Try to simplify
        try:
            simplified = sp.simplify(partial_expr)
            simplified_str = str(simplified)
        except:
            simplified = partial_expr
            simplified_str = partial_str
        
        # Get all variables in the original expression
        all_variables = [str(sym) for sym in expr.free_symbols]
        
        return {
            "partial_derivative": partial_str,
            "derivative": partial_str,  # Alias for test compatibility
            "simplified": simplified_str,
            "original_expression": expression,
            "variable": variable,
            "order": order,
            "all_variables": all_variables,
            "operation": "partial_derivative"
        }
        
    except Exception as e:
        raise CalculusError(f"Error calculating partial derivative: {e}") from e


# Symbolic Integration
def symbolic_integral(expression: str, variable: str, 
                     lower_bound: Optional[Union[float, int, str]] = None,
                     upper_bound: Optional[Union[float, int, str]] = None) -> Dict[str, Any]:
    """Calculate symbolic integral (definite or indefinite) of an expression."""
    try:
        expr = _validate_expression(expression)
        var = _validate_variable(variable)
        
        # Determine if this is definite or indefinite integral
        is_definite = lower_bound is not None and upper_bound is not None
        
        if is_definite:
            # Parse bounds
            try:
                if isinstance(lower_bound, str):
                    if lower_bound.lower() in ['inf', 'infinity', '+inf']:
                        lower = sp.oo
                    elif lower_bound.lower() in ['-inf', '-infinity']:
                        lower = -sp.oo
                    else:
                        lower = sp.sympify(lower_bound)
                else:
                    lower = float(lower_bound)
                
                if isinstance(upper_bound, str):
                    if upper_bound.lower() in ['inf', 'infinity', '+inf']:
                        upper = sp.oo
                    elif upper_bound.lower() in ['-inf', '-infinity']:
                        upper = -sp.oo
                    else:
                        upper = sp.sympify(upper_bound)
                else:
                    upper = float(upper_bound)
                    
            except Exception as e:
                raise ValidationError(f"Invalid bounds: {e}")
            
            # Calculate definite integral
            try:
                integral_expr = integrate(expr, (var, lower, upper))
                integral_str = str(integral_expr)
                
                # Try to get numerical value
                try:
                    if integral_expr.is_real:
                        value = float(integral_expr)
                    else:
                        value = complex(integral_expr)
                except:
                    value = integral_str
                
                success = True
                error_message = None
                
            except sp.IntegrationError as e:
                integral_str = f"Cannot integrate: {e}"
                value = None
                success = False
                error_message = str(e)
            
            return {
                "integral": integral_str,
                "value": value,
                "original_expression": expression,
                "variable": variable,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "type": "definite",
                "success": success,
                "error_message": error_message,
                "operation": "symbolic_integral"
            }
        
        else:
            # Calculate indefinite integral
            try:
                integral_expr = integrate(expr, var)
                integral_str = str(integral_expr)
                
                # Try to simplify
                try:
                    simplified = sp.simplify(integral_expr)
                    simplified_str = str(simplified)
                except:
                    simplified = integral_expr
                    simplified_str = integral_str
                
                success = True
                error_message = None
                
            except sp.IntegrationError as e:
                integral_str = f"Cannot integrate: {e}"
                simplified_str = integral_str
                success = False
                error_message = str(e)
            
            return {
                "integral": integral_str,
                "simplified": simplified_str,
                "original_expression": expression,
                "variable": variable,
                "type": "indefinite",
                "success": success,
                "error_message": error_message,
                "operation": "symbolic_integral"
            }
        
    except Exception as e:
        raise CalculusError(f"Error calculating symbolic integral: {e}") from e


def definite_integral(expression: str, variable: str, 
                     lower_bound: Union[float, int, str], 
                     upper_bound: Union[float, int, str]) -> Dict[str, Any]:
    """Calculate definite integral of an expression over specified bounds."""
    try:
        expr = _validate_expression(expression)
        var = _validate_variable(variable)
        lower, upper = _validate_numeric_bounds(lower_bound, upper_bound)
        
        # Calculate definite integral
        try:
            integral_result = integrate(expr, (var, lower, upper))
            
            # Try to evaluate numerically if result contains unevaluated integrals
            try:
                if integral_result.has(sp.Integral):
                    # Try numerical evaluation
                    numerical_result = float(integral_result.evalf())
                    result_str = str(numerical_result)
                    is_numerical = True
                else:
                    # Exact symbolic result
                    result_str = str(integral_result)
                    is_numerical = False
                    
                    # Try to get numerical value
                    try:
                        numerical_result = float(integral_result.evalf())
                    except:
                        numerical_result = None
                
            except:
                result_str = str(integral_result)
                numerical_result = None
                is_numerical = False
            
            success = True
            error_message = None
            
        except sp.IntegrationError as e:
            result_str = f"Cannot integrate: {e}"
            numerical_result = None
            is_numerical = False
            success = False
            error_message = str(e)
        
        return {
            "result": result_str,
            "numerical_value": numerical_result,
            "is_numerical": is_numerical,
            "original_expression": expression,
            "variable": variable,
            "lower_bound": str(lower),
            "upper_bound": str(upper),
            "type": "definite",
            "success": success,
            "error_message": error_message,
            "operation": "definite_integral"
        }
        
    except Exception as e:
        raise CalculusError(f"Error calculating definite integral: {e}") from e


# Numerical Calculus
def numerical_derivative(expression: str, variable: str, point: Union[float, int], 
                        method: str = "central", step_size: float = 1e-6) -> Dict[str, Any]:
    """Calculate numerical derivative at a specific point."""
    try:
        if method not in ["forward", "backward", "central"]:
            raise ValidationError("Method must be 'forward', 'backward', or 'central'")
        
        if step_size <= 0 or step_size > 0.1:
            raise ValidationError("step_size must be positive and at most 0.1")
        
        expr = _validate_expression(expression)
        var = _validate_variable(variable)
        point_val = float(point)
        
        # Create a numerical function
        def func(x):
            try:
                return float(expr.subs(var, x))
            except:
                raise CalculusError(f"Cannot evaluate expression at x = {x}")
        
        # Calculate numerical derivative using finite differences
        try:
            if method == "forward":
                derivative_value = (func(point_val + step_size) - func(point_val)) / step_size
            elif method == "backward":
                derivative_value = (func(point_val) - func(point_val - step_size)) / step_size
            else:  # central
                derivative_value = (func(point_val + step_size) - func(point_val - step_size)) / (2 * step_size)
            
            # Check if result is finite
            if not np.isfinite(derivative_value):
                raise CalculusError("Derivative evaluation resulted in non-finite value")
            
            success = True
            error_message = None
            
        except Exception as e:
            derivative_value = None
            success = False
            error_message = str(e)
        
        return {
            "derivative": derivative_value,  # Key expected by tests
            "derivative_value": derivative_value,  # Alternative key
            "original_expression": expression,
            "variable": variable,
            "point": point_val,
            "method": method,
            "step_size": step_size,
            "success": success,
            "error_message": error_message,
            "operation": "numerical_derivative"
        }
        
    except Exception as e:
        raise CalculusError(f"Error calculating numerical derivative: {e}") from e


def numerical_integral(expression: str, variable: str, 
                      lower_bound: Union[float, int], 
                      upper_bound: Union[float, int],
                      method: str = "trapezoid", 
                      intervals: int = 10000) -> Dict[str, Any]:
    """Calculate numerical integral using scipy integration methods."""
    try:
        expr = _validate_expression(expression)
        var = _validate_variable(variable)
        
        lower = float(lower_bound)
        upper = float(upper_bound)
        
        if lower >= upper:
            raise ValidationError("Lower bound must be less than upper bound")
        
        # Validate method
        valid_methods = ["trapezoid", "simpson", "romberg"]
        if method not in valid_methods:
            raise ValidationError(f"Invalid method: {method}. Valid methods: {valid_methods}")
        
        if intervals < 1:
            raise ValidationError("Number of intervals must be positive")
        
        # Create a numerical function
        def func(x):
            try:
                return float(expr.subs(var, x))
            except:
                raise CalculusError(f"Cannot evaluate expression at x = {x}")
        
        # Calculate numerical integral
        try:
            if method == "trapezoid":
                # Trapezoidal rule
                x_vals = np.linspace(lower, upper, intervals + 1)
                y_vals = [func(x) for x in x_vals]
                h = (upper - lower) / intervals
                result = h * (0.5 * y_vals[0] + sum(y_vals[1:-1]) + 0.5 * y_vals[-1])
                integration_info = {"intervals": intervals}
            elif method == "simpson":
                # Simpson's rule (requires even number of intervals)
                if intervals % 2 != 0:
                    intervals += 1
                x_vals = np.linspace(lower, upper, intervals + 1)
                y_vals = [func(x) for x in x_vals]
                h = (upper - lower) / intervals
                result = h / 3 * (y_vals[0] + 4 * sum(y_vals[1::2]) + 2 * sum(y_vals[2:-1:2]) + y_vals[-1])
                integration_info = {"intervals": intervals}
            else:  # romberg - fallback to scipy quad
                try:
                    result, error = scipy_integrate.quad(func, lower, upper)
                    integration_info = {"estimated_error": error}
                except ImportError:
                    # Fallback to trapezoidal if scipy not available
                    x_vals = np.linspace(lower, upper, intervals + 1)
                    y_vals = [func(x) for x in x_vals]
                    h = (upper - lower) / intervals
                    result = h * (0.5 * y_vals[0] + sum(y_vals[1:-1]) + 0.5 * y_vals[-1])
                    integration_info = {"intervals": intervals}
            
            # Check if result is finite
            if not np.isfinite(result):
                raise CalculusError("Integration resulted in non-finite value")
            
            success = True
            error_message = None
            
        except Exception as e:
            result = None
            integration_info = {}
            success = False
            error_message = str(e)
        
        return {
            "value": result,  # Key expected by tests
            "result": result,  # Alternative key
            "original_expression": expression,
            "variable": variable,
            "lower_bound": lower,
            "upper_bound": upper,
            "method": method,
            "intervals": intervals,
            "integration_info": integration_info,
            "success": success,
            "error_message": error_message,
            "operation": "numerical_integral"
        }
        
    except Exception as e:
        raise CalculusError(f"Error calculating numerical integral: {e}") from e


# Limits
def calculate_limit(expression: str, variable: str, 
                   approach_value: Union[float, int, str],
                   direction: str = "both") -> Dict[str, Any]:
    """Calculate limit of an expression as variable approaches a value."""
    try:
        expr = _validate_expression(expression)
        var = _validate_variable(variable)
        
        # Parse approach value
        if isinstance(approach_value, str):
            if approach_value.lower() in ['inf', 'infinity', '+inf', '+infinity']:
                approach = sp.oo
            elif approach_value.lower() in ['-inf', '-infinity']:
                approach = -sp.oo
            else:
                approach = float(approach_value)
        else:
            approach = float(approach_value)
        
        # Validate direction
        valid_directions = ["both", "left", "right", "+", "-"]
        if direction not in valid_directions:
            raise ValidationError(f"Invalid direction: {direction}. Valid directions: {valid_directions}")
        
        # Calculate limit
        try:
            if direction == "both":
                limit_result = limit(expr, var, approach)
            elif direction in ["left", "-"]:
                limit_result = limit(expr, var, approach, '-')
            elif direction in ["right", "+"]:
                limit_result = limit(expr, var, approach, '+')
            
            # Convert result to appropriate format
            result_str = str(limit_result)
            
            # Try to get numerical value
            try:
                if limit_result == sp.oo:
                    limit_value = float('inf')
                elif limit_result == -sp.oo:
                    limit_value = float('-inf')
                elif limit_result.is_number:
                    limit_value = float(limit_result.evalf())
                else:
                    limit_value = result_str
            except:
                limit_value = result_str
            
            success = True
            error_message = None
            
        except Exception as e:
            result_str = f"Limit does not exist or cannot be calculated: {e}"
            limit_value = None
            success = False
            error_message = str(e)
        
        return {
            "limit": limit_value,  # Numerical value expected by tests
            "limit_str": result_str,  # String representation
            "original_expression": expression,
            "variable": variable,
            "approach_value": str(approach),
            "direction": direction,
            "success": success,
            "error_message": error_message,
            "operation": "calculate_limit"
        }
        
    except Exception as e:
        raise CalculusError(f"Error calculating limit: {e}") from e


# Series Expansion
def taylor_series(expression: str, variable: str, 
                 center: Union[float, int] = 0, 
                 order: int = 5) -> Dict[str, Any]:
    """Calculate Taylor series expansion of an expression."""
    try:
        if order < 1 or order > 20:
            raise ValidationError("Series order must be between 1 and 20")
        
        expr = _validate_expression(expression)
        var = _validate_variable(variable)
        center_val = float(center)
        
        # Calculate Taylor series
        try:
            series_expr = series(expr, var, center_val, n=order+1).removeO()
            series_str = str(series_expr)
            
            # Try to simplify
            try:
                simplified = sp.simplify(series_expr)
                simplified_str = str(simplified)
            except:
                simplified = series_expr
                simplified_str = series_str
            
            # Get coefficients
            coefficients = []
            for i in range(order + 1):
                try:
                    coeff = series_expr.coeff(var - center_val, i)
                    if coeff is None:
                        coeff = 0
                    coefficients.append(float(coeff))
                except:
                    coefficients.append(0.0)
            
            success = True
            error_message = None
            
        except Exception as e:
            series_str = f"Cannot calculate series: {e}"
            simplified_str = series_str
            coefficients = []
            success = False
            error_message = str(e)
        
        return {
            "series": series_str,
            "simplified": simplified_str,
            "coefficients": coefficients,
            "original_expression": expression,
            "variable": variable,
            "center": center_val,
            "order": order,
            "success": success,
            "error_message": error_message,
            "operation": "taylor_series"
        }
        
    except Exception as e:
        raise CalculusError(f"Error calculating Taylor series: {e}") from e


# Multi-variable Calculus
def gradient(expression: str, variables: List[str]) -> Dict[str, Any]:
    """Calculate gradient (vector of partial derivatives) of a multi-variable function."""
    try:
        if len(variables) < 2 or len(variables) > 10:
            raise ValidationError("Number of variables must be between 2 and 10")
        
        expr = _validate_expression(expression)
        var_symbols = [_validate_variable(var) for var in variables]
        
        # Calculate partial derivatives for each variable
        gradient_components = []
        gradient_dict = {}
        
        for i, var_sym in enumerate(var_symbols):
            var_name = variables[i]
            try:
                if var_sym in expr.free_symbols:
                    partial = diff(expr, var_sym)
                else:
                    partial = sp.Integer(0)
                
                partial_str = str(partial)
                gradient_components.append(partial_str)
                gradient_dict[var_name] = partial_str
                
            except Exception as e:
                gradient_components.append(f"Error: {e}")
                gradient_dict[var_name] = f"Error: {e}"
        
        return {
            "gradient": gradient_dict,  # Dictionary expected by tests
            "gradient_components": gradient_components,  # List for alternative use
            "original_expression": expression,
            "variables": variables,
            "operation": "gradient"
        }
        
    except Exception as e:
        raise CalculusError(f"Error calculating gradient: {e}") from e


def divergence(vector_field: List[str], variables: List[str]) -> Dict[str, Any]:
    """Calculate divergence of a vector field."""
    try:
        if len(vector_field) != len(variables):
            raise ValidationError("Number of vector components must equal number of variables")
        
        if len(variables) < 2 or len(variables) > 3:
            raise ValidationError("Divergence is defined for 2D or 3D vector fields")
        
        # Parse vector field components
        field_exprs = [_validate_expression(component) for component in vector_field]
        var_symbols = [_validate_variable(var) for var in variables]
        
        # Calculate divergence: sum of partial derivatives
        divergence_terms = []
        total_divergence = sp.Integer(0)
        
        for i, (field_expr, var_sym) in enumerate(zip(field_exprs, var_symbols)):
            try:
                if var_sym in field_expr.free_symbols:
                    partial = diff(field_expr, var_sym)
                else:
                    partial = sp.Integer(0)
                
                partial_str = str(partial)
                divergence_terms.append(partial_str)
                total_divergence += partial
                
            except Exception as e:
                divergence_terms.append(f"Error: {e}")
        
        # Simplify total divergence
        try:
            simplified_div = sp.simplify(total_divergence)
            divergence_str = str(simplified_div)
            
            # Try to convert to number if possible
            try:
                if simplified_div.is_number:
                    divergence_value = float(simplified_div)
                else:
                    divergence_value = divergence_str
            except:
                divergence_value = divergence_str
        except:
            divergence_str = str(total_divergence)
            divergence_value = divergence_str
        
        return {
            "divergence": divergence_value,  # Number when possible, string otherwise
            "divergence_str": divergence_str,  # String representation
            "divergence_terms": divergence_terms,
            "vector_field": vector_field,
            "variables": variables,
            "operation": "divergence"
        }
        
    except Exception as e:
        raise CalculusError(f"Error calculating divergence: {e}") from e


def curl_2d(vector_field: List[str], variables: List[str]) -> Dict[str, Any]:
    """Calculate curl of a 2D vector field (returns scalar)."""
    try:
        if len(vector_field) != 2 or len(variables) != 2:
            raise ValidationError("2D curl requires exactly 2 vector components and 2 variables")
        
        # Parse vector field components [P, Q]
        P = _validate_expression(vector_field[0])
        Q = _validate_expression(vector_field[1])
        
        # Variables [x, y]
        x = _validate_variable(variables[0])
        y = _validate_variable(variables[1])
        
        # Calculate curl: ∂Q/∂x - ∂P/∂y
        try:
            dQ_dx = diff(Q, x) if x in Q.free_symbols else sp.Integer(0)
            dP_dy = diff(P, y) if y in P.free_symbols else sp.Integer(0)
            
            curl_expr = dQ_dx - dP_dy
            
            # Simplify
            try:
                simplified_curl = sp.simplify(curl_expr)
                curl_str = str(simplified_curl)
            except:
                curl_str = str(curl_expr)
            
            success = True
            error_message = None
            
        except Exception as e:
            curl_str = f"Error calculating curl: {e}"
            success = False
            error_message = str(e)
        
        return {
            "curl": curl_str,
            "vector_field": vector_field,
            "variables": variables,
            "dimension": "2D",
            "success": success,
            "error_message": error_message,
            "operation": "curl_2d"
        }
        
    except Exception as e:
        raise CalculusError(f"Error calculating 2D curl: {e}") from e


# Utility Functions
def evaluate_expression(expression: str, variable_values: Dict[str, Union[float, int]]) -> Dict[str, Any]:
    """Evaluate a mathematical expression at specific variable values."""
    try:
        expr = _validate_expression(expression)
        
        # Validate variable values
        substitutions = {}
        for var_name, value in variable_values.items():
            var_sym = _validate_variable(var_name)
            substitutions[var_sym] = float(value)
        
        # Check if all variables in expression are provided
        expr_vars = expr.free_symbols
        provided_vars = set(substitutions.keys())
        
        missing_vars = expr_vars - provided_vars
        if missing_vars:
            missing_names = [str(var) for var in missing_vars]
            raise ValidationError(f"Missing values for variables: {missing_names}")
        
        # Evaluate expression
        try:
            result = expr.subs(substitutions)
            numerical_result = float(result.evalf())
            
            # Check if result is finite
            if not np.isfinite(numerical_result):
                raise CalculusError("Expression evaluation resulted in non-finite value")
            
            success = True
            error_message = None
            
        except Exception as e:
            numerical_result = None
            success = False
            error_message = str(e)
        
        return {
            "result": numerical_result,
            "original_expression": expression,
            "variable_values": variable_values,
            "success": success,
            "error_message": error_message,
            "operation": "evaluate_expression"
        }
        
    except Exception as e:
        raise CalculusError(f"Error evaluating expression: {e}") from e


def find_critical_points(expression: str, variable: str) -> Dict[str, Any]:
    """Find critical points of a single-variable function."""
    try:
        expr = _validate_expression(expression)
        var = _validate_variable(variable)
        
        # Calculate first derivative
        try:
            first_derivative = diff(expr, var)
            
            # Solve for critical points (where derivative = 0)
            critical_points = sp.solve(first_derivative, var)
            
            # Convert to numerical values where possible
            numerical_points = []
            symbolic_points = []
            
            for point in critical_points:
                try:
                    numerical_val = float(point.evalf())
                    if np.isfinite(numerical_val):
                        numerical_points.append(numerical_val)
                    else:
                        symbolic_points.append(str(point))
                except:
                    symbolic_points.append(str(point))
            
            # Calculate second derivative for classification
            second_derivative = diff(first_derivative, var)
            second_deriv_str = str(second_derivative)
            
            # Classify critical points
            point_classifications = []
            for point in numerical_points:
                try:
                    second_deriv_val = float(second_derivative.subs(var, point))
                    if second_deriv_val > 0:
                        classification = "local minimum"
                    elif second_deriv_val < 0:
                        classification = "local maximum"
                    else:
                        classification = "inconclusive (second derivative test)"
                    
                    point_classifications.append({
                        "point": point,
                        "classification": classification,
                        "second_derivative": second_deriv_val
                    })
                except:
                    point_classifications.append({
                        "point": point,
                        "classification": "error evaluating second derivative",
                        "second_derivative": None
                    })
            
            success = True
            error_message = None
            
        except Exception as e:
            numerical_points = []
            symbolic_points = []
            point_classifications = []
            second_deriv_str = f"Error: {e}"
            success = False
            error_message = str(e)
        
        return {
            "numerical_critical_points": numerical_points,
            "symbolic_critical_points": symbolic_points,
            "point_classifications": point_classifications,
            "first_derivative": str(first_derivative) if 'first_derivative' in locals() else "Error",
            "second_derivative": second_deriv_str,
            "original_expression": expression,
            "variable": variable,
            "success": success,
            "error_message": error_message,
            "operation": "find_critical_points"
        }
        
    except Exception as e:
        raise CalculusError(f"Error finding critical points: {e}") from e
# Function aliases for backward compatibility with tests
derivative = symbolic_derivative
integral = symbolic_integral
def curl(vector_field: List[str], variables: List[str]) -> Dict[str, Any]:
    """Calculate curl of a 3D vector field."""
    try:
        if len(vector_field) != 3 or len(variables) != 3:
            raise ValidationError("3D curl requires exactly 3 vector components and 3 variables")
        
        # Parse vector field components [Fx, Fy, Fz]
        Fx = _validate_expression(vector_field[0])
        Fy = _validate_expression(vector_field[1])
        Fz = _validate_expression(vector_field[2])
        
        # Variables [x, y, z]
        x, y, z = [_validate_variable(var) for var in variables]
        
        # Calculate curl components: curl = (∂Fz/∂y - ∂Fy/∂z, ∂Fx/∂z - ∂Fz/∂x, ∂Fy/∂x - ∂Fx/∂y)
        try:
            curl_x = diff(Fz, y) - diff(Fy, z) if (y in Fz.free_symbols or z in Fy.free_symbols) else sp.Integer(0)
            curl_y = diff(Fx, z) - diff(Fz, x) if (z in Fx.free_symbols or x in Fz.free_symbols) else sp.Integer(0)
            curl_z = diff(Fy, x) - diff(Fx, y) if (x in Fy.free_symbols or y in Fx.free_symbols) else sp.Integer(0)
            
            # Convert to appropriate format (numbers when possible)
            curl_components = []
            for component in [curl_x, curl_y, curl_z]:
                try:
                    if component.is_number:
                        curl_components.append(float(component))
                    else:
                        curl_components.append(str(component))
                except:
                    curl_components.append(str(component))
            
            success = True
            error_message = None
            
        except Exception as e:
            curl_components = [f"Error: {e}", f"Error: {e}", f"Error: {e}"]
            success = False
            error_message = str(e)
        
        return {
            "curl": curl_components,
            "vector_field": vector_field,
            "variables": variables,
            "success": success,
            "error_message": error_message,
            "operation": "curl"
        }
        
    except Exception as e:
        raise CalculusError(f"Error calculating curl: {e}") from e


def laplacian(expression: str, variables: List[str]) -> Dict[str, Any]:
    """Calculate Laplacian (sum of second partial derivatives) of a function."""
    try:
        if len(variables) < 2 or len(variables) > 3:
            raise ValidationError("Laplacian is defined for 2D or 3D functions")
        
        expr = _validate_expression(expression)
        var_symbols = [_validate_variable(var) for var in variables]
        
        # Calculate Laplacian: sum of second partial derivatives
        laplacian_sum = sp.Integer(0)
        second_derivatives = []
        
        for var_sym in var_symbols:
            try:
                if var_sym in expr.free_symbols:
                    second_partial = diff(expr, var_sym, 2)
                else:
                    second_partial = sp.Integer(0)
                
                second_derivatives.append(str(second_partial))
                laplacian_sum += second_partial
                
            except Exception as e:
                second_derivatives.append(f"Error: {e}")
        
        # Simplify and convert to appropriate format
        try:
            simplified_laplacian = sp.simplify(laplacian_sum)
            
            # Try to convert to number if possible
            try:
                if simplified_laplacian.is_number:
                    laplacian_value = float(simplified_laplacian)
                else:
                    laplacian_value = str(simplified_laplacian)
            except:
                laplacian_value = str(simplified_laplacian)
                
            success = True
            error_message = None
            
        except Exception as e:
            laplacian_value = f"Error: {e}"
            success = False
            error_message = str(e)
        
        return {
            "laplacian": laplacian_value,  # Number when possible, string otherwise
            "second_derivatives": second_derivatives,
            "original_expression": expression,
            "variables": variables,
            "success": success,
            "error_message": error_message,
            "operation": "laplacian"
        }
        
    except Exception as e:
        raise CalculusError(f"Error calculating Laplacian: {e}") from e
# Utility Functions
def simplify_expression(expression: str) -> Dict[str, Any]:
    """Simplify a mathematical expression."""
    try:
        expr = _validate_expression(expression)
        
        # Simplify the expression
        try:
            simplified_expr = sp.simplify(expr)
            simplified_str = str(simplified_expr)
            success = True
            error_message = None
        except Exception as e:
            simplified_expr = expr
            simplified_str = str(expr)
            success = False
            error_message = str(e)
        
        return {
            "simplified": simplified_str,
            "original_expression": expression,
            "success": success,
            "error_message": error_message,
            "operation": "simplify_expression"
        }
        
    except Exception as e:
        raise CalculusError(f"Error simplifying expression: {e}") from e


def expand_expression(expression: str) -> Dict[str, Any]:
    """Expand a mathematical expression."""
    try:
        expr = _validate_expression(expression)
        
        # Expand the expression
        try:
            expanded_expr = sp.expand(expr)
            expanded_str = str(expanded_expr)
            success = True
            error_message = None
        except Exception as e:
            expanded_expr = expr
            expanded_str = str(expr)
            success = False
            error_message = str(e)
        
        return {
            "expanded": expanded_str,
            "original_expression": expression,
            "success": success,
            "error_message": error_message,
            "operation": "expand_expression"
        }
        
    except Exception as e:
        raise CalculusError(f"Error expanding expression: {e}") from e


def factor_expression(expression: str) -> Dict[str, Any]:
    """Factor a mathematical expression."""
    try:
        expr = _validate_expression(expression)
        
        # Factor the expression
        try:
            factored_expr = sp.factor(expr)
            factored_str = str(factored_expr)
            success = True
            error_message = None
        except Exception as e:
            factored_expr = expr
            factored_str = str(expr)
            success = False
            error_message = str(e)
        
        return {
            "factored": factored_str,
            "original_expression": expression,
            "success": success,
            "error_message": error_message,
            "operation": "factor_expression"
        }
        
    except Exception as e:
        raise CalculusError(f"Error factoring expression: {e}") from e