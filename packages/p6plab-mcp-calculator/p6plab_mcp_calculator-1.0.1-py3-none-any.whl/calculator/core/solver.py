"""
Equation solving module for the Scientific Calculator MCP Server.

This module provides comprehensive equation solving capabilities including
linear equations, quadratic equations, polynomial equations, systems of equations,
and root finding for arbitrary functions.
"""

from typing import Union, Dict, Any, List, Optional, Tuple
import sympy as sp
from sympy import symbols, Eq, solve, nsolve, solveset
from sympy.parsing.sympy_parser import parse_expr
import numpy as np
from scipy.optimize import fsolve, root_scalar, root
import cmath

from calculator.models.errors import CalculatorError, ValidationError


class SolverError(CalculatorError):
    """Error for equation solving operations."""
    pass


def _validate_equation(equation: str) -> sp.Eq:
    """Validate and parse equation string into SymPy equation."""
    try:
        equation = equation.strip()
        if not equation:
            raise ValueError("Equation cannot be empty")
        
        # Handle different equation formats
        if '=' in equation:
            # Split on equals sign
            left, right = equation.split('=', 1)
            left_expr = parse_expr(left.strip(), transformations='all')
            right_expr = parse_expr(right.strip(), transformations='all')
            return Eq(left_expr, right_expr)
        else:
            # Assume equation equals zero
            expr = parse_expr(equation, transformations='all')
            return Eq(expr, 0)
            
    except Exception as e:
        raise ValidationError(f"Invalid equation '{equation}': {e}") from e


def _validate_variable(variable: str) -> sp.Symbol:
    """Validate and create a SymPy symbol for a variable."""
    try:
        if not variable or not isinstance(variable, str):
            raise ValueError("Variable must be a non-empty string")
        
        if not variable.isalpha() or len(variable) > 10:
            raise ValueError("Variable must be alphabetic and at most 10 characters")
        
        return symbols(variable)
        
    except Exception as e:
        raise ValidationError(f"Invalid variable '{variable}': {e}") from e


def _convert_solutions_to_dict(solutions: List, variable: str) -> List[Dict[str, Any]]:
    """Convert SymPy solutions to dictionary format with type information."""
    result = []
    
    for sol in solutions:
        try:
            # Try to convert to float (real solution)
            if sol.is_real:
                numerical_value = float(sol.evalf())
                result.append({
                    "value": numerical_value,
                    "symbolic": str(sol),
                    "type": "real",
                    "variable": variable
                })
            else:
                # Complex solution
                complex_val = complex(sol.evalf())
                result.append({
                    "value": {
                        "real": float(complex_val.real),
                        "imag": float(complex_val.imag)
                    },
                    "symbolic": str(sol),
                    "type": "complex",
                    "variable": variable
                })
        except:
            # Symbolic solution that can't be evaluated numerically
            result.append({
                "value": None,
                "symbolic": str(sol),
                "type": "symbolic",
                "variable": variable
            })
    
    return result


# Linear Equations
def solve_linear(equation: str, variable: str) -> Dict[str, Any]:
    """Solve a linear equation for a single variable."""
    try:
        eq = _validate_equation(equation)
        var = _validate_variable(variable)
        
        # Check if variable is in the equation
        if var not in eq.free_symbols:
            raise SolverError(f"Variable '{variable}' not found in equation")
        
        # Solve the equation
        try:
            solutions = solve(eq, var)
            
            if not solutions:
                solution_type = "no_solution"
                solutions_dict = []
            elif len(solutions) == 1:
                solution_type = "unique_solution"
                solutions_dict = _convert_solutions_to_dict(solutions, variable)
            else:
                solution_type = "multiple_solutions"
                solutions_dict = _convert_solutions_to_dict(solutions, variable)
            
            # Check if the equation is actually linear
            expanded_eq = sp.expand(eq.lhs - eq.rhs)
            degree = sp.degree(expanded_eq, var)
            
            if degree > 1:
                is_linear = False
                actual_degree = degree
            else:
                is_linear = True
                actual_degree = degree
            
            success = True
            error_message = None
            
        except Exception as e:
            solutions_dict = []
            solution_type = "error"
            is_linear = None
            actual_degree = None
            success = False
            error_message = str(e)
        
        return {
            "solutions": solutions_dict,
            "solution_type": solution_type,
            "is_linear": is_linear,
            "degree": actual_degree,
            "original_equation": equation,
            "variable": variable,
            "success": success,
            "error_message": error_message,
            "operation": "solve_linear"
        }
        
    except Exception as e:
        raise SolverError(f"Error solving linear equation: {e}") from e


# Quadratic Equations
def solve_quadratic(equation: str, variable: str) -> Dict[str, Any]:
    """Solve a quadratic equation and provide detailed analysis."""
    try:
        eq = _validate_equation(equation)
        var = _validate_variable(variable)
        
        # Check if variable is in the equation
        if var not in eq.free_symbols:
            raise SolverError(f"Variable '{variable}' not found in equation")
        
        # Expand and get coefficients
        try:
            expanded_eq = sp.expand(eq.lhs - eq.rhs)
            degree = sp.degree(expanded_eq, var)
            
            if degree != 2:
                raise SolverError(f"Equation is not quadratic (degree = {degree})")
            
            # Extract coefficients a, b, c from ax^2 + bx + c = 0
            coeffs = sp.Poly(expanded_eq, var).all_coeffs()
            
            if len(coeffs) == 3:
                a, b, c = [float(coeff) for coeff in coeffs]
            elif len(coeffs) == 2:
                a, b, c = float(coeffs[0]), float(coeffs[1]), 0.0
            else:
                a, b, c = float(coeffs[0]), 0.0, 0.0
            
            # Calculate discriminant
            discriminant = b**2 - 4*a*c
            
            # Solve using quadratic formula
            if discriminant > 0:
                # Two real solutions
                x1 = (-b + np.sqrt(discriminant)) / (2*a)
                x2 = (-b - np.sqrt(discriminant)) / (2*a)
                solutions_dict = [
                    {"value": x1, "symbolic": str(x1), "type": "real", "variable": variable},
                    {"value": x2, "symbolic": str(x2), "type": "real", "variable": variable}
                ]
                solution_type = "two_real_solutions"
            elif discriminant == 0:
                # One real solution (repeated root)
                x = -b / (2*a)
                solutions_dict = [
                    {"value": x, "symbolic": str(x), "type": "real", "variable": variable}
                ]
                solution_type = "one_real_solution"
            else:
                # Two complex solutions
                real_part = -b / (2*a)
                imag_part = np.sqrt(-discriminant) / (2*a)
                
                x1 = complex(real_part, imag_part)
                x2 = complex(real_part, -imag_part)
                
                solutions_dict = [
                    {
                        "value": {"real": real_part, "imag": imag_part},
                        "symbolic": f"{real_part} + {imag_part}*I",
                        "type": "complex",
                        "variable": variable
                    },
                    {
                        "value": {"real": real_part, "imag": -imag_part},
                        "symbolic": f"{real_part} - {imag_part}*I",
                        "type": "complex",
                        "variable": variable
                    }
                ]
                solution_type = "two_complex_solutions"
            
            # Additional quadratic analysis
            vertex_x = -b / (2*a)
            vertex_y = float(expanded_eq.subs(var, vertex_x))
            
            analysis = {
                "coefficients": {"a": a, "b": b, "c": c},
                "discriminant": discriminant,
                "vertex": {"x": vertex_x, "y": vertex_y},
                "axis_of_symmetry": vertex_x,
                "opens_upward": a > 0
            }
            
            success = True
            error_message = None
            
        except Exception as e:
            solutions_dict = []
            solution_type = "error"
            analysis = {}
            success = False
            error_message = str(e)
        
        return {
            "solutions": solutions_dict,
            "solution_type": solution_type,
            "analysis": analysis,
            "original_equation": equation,
            "variable": variable,
            "success": success,
            "error_message": error_message,
            "operation": "solve_quadratic"
        }
        
    except Exception as e:
        raise SolverError(f"Error solving quadratic equation: {e}") from e


# Polynomial Equations
def solve_polynomial(equation: str, variable: str) -> Dict[str, Any]:
    """Solve polynomial equations of any degree."""
    try:
        eq = _validate_equation(equation)
        var = _validate_variable(variable)
        
        # Check if variable is in the equation
        if var not in eq.free_symbols:
            raise SolverError(f"Variable '{variable}' not found in equation")
        
        try:
            # Get polynomial information
            expanded_eq = sp.expand(eq.lhs - eq.rhs)
            degree = sp.degree(expanded_eq, var)
            
            if degree > 20:
                raise SolverError(f"Polynomial degree too high ({degree}). Maximum supported degree is 20.")
            
            # Get coefficients
            poly = sp.Poly(expanded_eq, var)
            coefficients = [float(c) for c in poly.all_coeffs()]
            
            # Solve the polynomial
            solutions = solve(eq, var)
            
            if not solutions:
                solution_type = "no_solution"
                solutions_dict = []
            else:
                solutions_dict = _convert_solutions_to_dict(solutions, variable)
                
                # Classify solution types
                real_count = sum(1 for sol in solutions_dict if sol["type"] == "real")
                complex_count = sum(1 for sol in solutions_dict if sol["type"] == "complex")
                symbolic_count = sum(1 for sol in solutions_dict if sol["type"] == "symbolic")
                
                if complex_count == 0 and symbolic_count == 0:
                    solution_type = f"{real_count}_real_solutions"
                elif real_count == 0 and symbolic_count == 0:
                    solution_type = f"{complex_count}_complex_solutions"
                else:
                    solution_type = "mixed_solutions"
            
            # Additional polynomial analysis
            analysis = {
                "degree": degree,
                "coefficients": coefficients,
                "leading_coefficient": coefficients[0] if coefficients else 0,
                "constant_term": coefficients[-1] if coefficients else 0,
                "number_of_solutions": len(solutions_dict)
            }
            
            success = True
            error_message = None
            
        except Exception as e:
            solutions_dict = []
            solution_type = "error"
            analysis = {}
            success = False
            error_message = str(e)
        
        return {
            "solutions": solutions_dict,
            "solution_type": solution_type,
            "analysis": analysis,
            "original_equation": equation,
            "variable": variable,
            "success": success,
            "error_message": error_message,
            "operation": "solve_polynomial"
        }
        
    except Exception as e:
        raise SolverError(f"Error solving polynomial equation: {e}") from e


# System of Linear Equations
def solve_system(equations: List[str], variables: List[str]) -> Dict[str, Any]:
    """Solve a system of linear equations."""
    try:
        if len(equations) == 0 or len(variables) == 0:
            raise ValidationError("Must provide at least one equation and one variable")
        
        if len(equations) > 20 or len(variables) > 20:
            raise ValidationError("System too large (maximum 20 equations and 20 variables)")
        
        # Parse equations and variables
        eq_objects = [_validate_equation(eq) for eq in equations]
        var_symbols = [_validate_variable(var) for var in variables]
        
        # Check if all variables appear in at least one equation
        all_eq_vars = set()
        for eq in eq_objects:
            all_eq_vars.update(eq.free_symbols)
        
        missing_vars = set(var_symbols) - all_eq_vars
        if missing_vars:
            missing_names = [str(var) for var in missing_vars]
            raise SolverError(f"Variables not found in equations: {missing_names}")
        
        try:
            # Solve the system
            solutions = solve(eq_objects, var_symbols)
            
            if not solutions:
                solution_type = "no_solution"
                solutions_dict = {}
            elif isinstance(solutions, dict):
                # Unique solution
                solution_type = "unique_solution"
                solutions_dict = {}
                for var_sym, sol in solutions.items():
                    var_name = str(var_sym)
                    try:
                        if sol.is_real:
                            numerical_value = float(sol.evalf())
                            solutions_dict[var_name] = {
                                "value": numerical_value,
                                "symbolic": str(sol),
                                "type": "real"
                            }
                        else:
                            complex_val = complex(sol.evalf())
                            solutions_dict[var_name] = {
                                "value": {
                                    "real": float(complex_val.real),
                                    "imag": float(complex_val.imag)
                                },
                                "symbolic": str(sol),
                                "type": "complex"
                            }
                    except:
                        solutions_dict[var_name] = {
                            "value": None,
                            "symbolic": str(sol),
                            "type": "symbolic"
                        }
            elif isinstance(solutions, list):
                # Multiple solutions
                solution_type = "multiple_solutions"
                solutions_dict = []
                for sol_set in solutions:
                    if isinstance(sol_set, dict):
                        sol_dict = {}
                        for var_sym, sol in sol_set.items():
                            var_name = str(var_sym)
                            try:
                                if sol.is_real:
                                    numerical_value = float(sol.evalf())
                                    sol_dict[var_name] = {
                                        "value": numerical_value,
                                        "symbolic": str(sol),
                                        "type": "real"
                                    }
                                else:
                                    complex_val = complex(sol.evalf())
                                    sol_dict[var_name] = {
                                        "value": {
                                            "real": float(complex_val.real),
                                            "imag": float(complex_val.imag)
                                        },
                                        "symbolic": str(sol),
                                        "type": "complex"
                                    }
                            except:
                                sol_dict[var_name] = {
                                    "value": None,
                                    "symbolic": str(sol),
                                    "type": "symbolic"
                                }
                        solutions_dict.append(sol_dict)
            else:
                solution_type = "parametric_solution"
                solutions_dict = {"parametric": str(solutions)}
            
            # System analysis
            analysis = {
                "number_of_equations": len(equations),
                "number_of_variables": len(variables),
                "system_type": "linear" if all("**" not in eq and "^" not in eq for eq in equations) else "nonlinear"
            }
            
            success = True
            error_message = None
            
        except Exception as e:
            solutions_dict = {}
            solution_type = "error"
            analysis = {}
            success = False
            error_message = str(e)
        
        return {
            "solutions": solutions_dict,
            "solution_type": solution_type,
            "analysis": analysis,
            "original_equations": equations,
            "variables": variables,
            "success": success,
            "error_message": error_message,
            "operation": "solve_system"
        }
        
    except Exception as e:
        raise SolverError(f"Error solving system of equations: {e}") from e


# Root Finding for Arbitrary Functions
def find_roots(expression: str, variable: str, 
               initial_guess: Union[float, List[float]] = None,
               method: str = "auto") -> Dict[str, Any]:
    """Find roots of arbitrary functions using numerical methods."""
    try:
        # Parse expression
        expr = parse_expr(expression, transformations='all')
        var = _validate_variable(variable)
        
        # Check if variable is in the expression
        if var not in expr.free_symbols:
            raise SolverError(f"Variable '{variable}' not found in expression")
        
        # Validate method
        valid_methods = ["auto", "brentq", "newton", "secant", "bisect"]
        if method not in valid_methods:
            raise ValidationError(f"Invalid method: {method}. Valid methods: {valid_methods}")
        
        # Create numerical function
        def func(x):
            try:
                return float(expr.subs(var, x))
            except:
                return float('inf')
        
        # Create derivative function for Newton's method
        def func_derivative(x):
            try:
                derivative = sp.diff(expr, var)
                return float(derivative.subs(var, x))
            except:
                return 0.0
        
        roots_found = []
        
        try:
            if method == "auto":
                # Try symbolic solution first
                try:
                    symbolic_roots = solve(expr, var)
                    for root in symbolic_roots:
                        try:
                            if root.is_real:
                                numerical_root = float(root.evalf())
                                if np.isfinite(numerical_root):
                                    roots_found.append({
                                        "root": numerical_root,
                                        "method": "symbolic",
                                        "symbolic": str(root),
                                        "type": "real"
                                    })
                        except:
                            pass
                except:
                    pass
                
                # If no symbolic roots found, try numerical methods
                if not roots_found:
                    # Try to find roots in a reasonable range
                    search_range = [-10, 10]
                    if initial_guess is not None:
                        if isinstance(initial_guess, list):
                            search_points = initial_guess
                        else:
                            search_points = [initial_guess]
                    else:
                        search_points = [-5, -1, 0, 1, 5]
                    
                    for guess in search_points:
                        try:
                            # Try Brent's method first
                            result = root_scalar(func, method='brentq', bracket=[guess-1, guess+1])
                            if result.converged:
                                root_val = result.root
                                if not any(abs(root_val - r["root"]) < 1e-10 for r in roots_found):
                                    roots_found.append({
                                        "root": root_val,
                                        "method": "brentq",
                                        "symbolic": str(root_val),
                                        "type": "real",
                                        "iterations": result.iterations
                                    })
                        except:
                            try:
                                # Try Newton's method
                                result = root_scalar(func, method='newton', x0=guess, fprime=func_derivative)
                                if result.converged:
                                    root_val = result.root
                                    if not any(abs(root_val - r["root"]) < 1e-10 for r in roots_found):
                                        roots_found.append({
                                            "root": root_val,
                                            "method": "newton",
                                            "symbolic": str(root_val),
                                            "type": "real",
                                            "iterations": result.iterations
                                        })
                            except:
                                pass
            
            else:
                # Use specific numerical method
                if initial_guess is None:
                    initial_guess = 0.0
                
                if isinstance(initial_guess, list):
                    guesses = initial_guess
                else:
                    guesses = [initial_guess]
                
                for guess in guesses:
                    try:
                        if method == "newton":
                            result = root_scalar(func, method='newton', x0=guess, fprime=func_derivative)
                        elif method == "secant":
                            result = root_scalar(func, method='secant', x0=guess, x1=guess+0.1)
                        elif method == "brentq":
                            result = root_scalar(func, method='brentq', bracket=[guess-1, guess+1])
                        elif method == "bisect":
                            result = root_scalar(func, method='bisect', bracket=[guess-1, guess+1])
                        
                        if result.converged:
                            root_val = result.root
                            if not any(abs(root_val - r["root"]) < 1e-10 for r in roots_found):
                                roots_found.append({
                                    "root": root_val,
                                    "method": method,
                                    "symbolic": str(root_val),
                                    "type": "real",
                                    "iterations": getattr(result, 'iterations', None)
                                })
                    except Exception as e:
                        pass
            
            if roots_found:
                solution_type = f"found_{len(roots_found)}_roots"
            else:
                solution_type = "no_roots_found"
            
            success = True
            error_message = None
            
        except Exception as e:
            solution_type = "error"
            success = False
            error_message = str(e)
        
        return {
            "roots": roots_found,
            "solution_type": solution_type,
            "original_expression": expression,
            "variable": variable,
            "method": method,
            "initial_guess": initial_guess,
            "success": success,
            "error_message": error_message,
            "operation": "find_roots"
        }
        
    except Exception as e:
        raise SolverError(f"Error finding roots: {e}") from e


# Equation Analysis
def analyze_equation(equation: str, variable: str) -> Dict[str, Any]:
    """Analyze an equation to determine its type and properties."""
    try:
        eq = _validate_equation(equation)
        var = _validate_variable(variable)
        
        # Check if variable is in the equation
        if var not in eq.free_symbols:
            raise SolverError(f"Variable '{variable}' not found in equation")
        
        try:
            # Expand and analyze
            expanded_eq = sp.expand(eq.lhs - eq.rhs)
            
            # Get degree
            degree = sp.degree(expanded_eq, var)
            
            # Determine equation type
            if degree == 1:
                equation_type = "linear"
            elif degree == 2:
                equation_type = "quadratic"
            elif degree > 2:
                equation_type = f"polynomial_degree_{degree}"
            else:
                equation_type = "constant"
            
            # Check for special functions
            has_trig = any(func in str(expanded_eq) for func in ['sin', 'cos', 'tan', 'sec', 'csc', 'cot'])
            has_exp = any(func in str(expanded_eq) for func in ['exp', 'log', 'ln'])
            has_sqrt = 'sqrt' in str(expanded_eq)
            has_abs = 'Abs' in str(expanded_eq)
            
            if has_trig:
                equation_type += "_trigonometric"
            if has_exp:
                equation_type += "_exponential"
            if has_sqrt:
                equation_type += "_radical"
            if has_abs:
                equation_type += "_absolute_value"
            
            # Get all variables
            all_variables = [str(sym) for sym in expanded_eq.free_symbols]
            
            # Get coefficients if polynomial
            coefficients = []
            if degree > 0 and not (has_trig or has_exp or has_sqrt or has_abs):
                try:
                    poly = sp.Poly(expanded_eq, var)
                    coefficients = [float(c) for c in poly.all_coeffs()]
                except:
                    pass
            
            analysis = {
                "equation_type": equation_type,
                "degree": degree,
                "all_variables": all_variables,
                "coefficients": coefficients,
                "has_trigonometric": has_trig,
                "has_exponential": has_exp,
                "has_radical": has_sqrt,
                "has_absolute_value": has_abs,
                "is_polynomial": not (has_trig or has_exp or has_sqrt or has_abs),
                "expanded_form": str(expanded_eq)
            }
            
            success = True
            error_message = None
            
        except Exception as e:
            analysis = {}
            success = False
            error_message = str(e)
        
        return {
            "analysis": analysis,
            "original_equation": equation,
            "variable": variable,
            "success": success,
            "error_message": error_message,
            "operation": "analyze_equation"
        }
        
    except Exception as e:
        raise SolverError(f"Error analyzing equation: {e}") from e