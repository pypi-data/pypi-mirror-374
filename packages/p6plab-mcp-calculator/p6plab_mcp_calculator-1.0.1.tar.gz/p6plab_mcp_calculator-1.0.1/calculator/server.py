"""Scientific Calculator MCP Server.

Main FastMCP server implementation providing comprehensive mathematical
computation capabilities through the Model Context Protocol.
"""

import os
from typing import Any, Dict

import sympy as sp
from fastmcp import FastMCP
from loguru import logger

# Import core calculation modules
from calculator.core import basic, advanced, statistics as calc_stats, matrix, complex as calc_complex, units, calculus, solver, financial, currency, constants
from calculator.core.validators import validate_mathematical_expression
from calculator.models.errors import CalculatorError, ErrorResponse

# Import tool group management
from calculator.core.tool_filter import create_tool_filter_from_environment, DisabledToolError

# Configure logging
log_level = os.getenv("CALCULATOR_LOG_LEVEL", "INFO")
logger.remove()  # Remove default handler
logger.add(
    lambda msg: print(msg, end=""),
    level=log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    colorize=True,
)

# Initialize tool group filtering
tool_filter = create_tool_filter_from_environment()
filter_stats = tool_filter.get_filter_stats()

# Initialize FastMCP server
mcp = FastMCP("Scientific Calculator")

# Configuration from environment variables
PRECISION = int(os.getenv("CALCULATOR_PRECISION", "15"))
CACHE_SIZE = int(os.getenv("CALCULATOR_CACHE_SIZE", "1000"))
MAX_COMPUTATION_TIME = int(os.getenv("CALCULATOR_MAX_COMPUTATION_TIME", "30"))
MAX_MEMORY_MB = int(os.getenv("CALCULATOR_MAX_MEMORY_MB", "512"))
ENABLE_CURRENCY = os.getenv("CALCULATOR_ENABLE_CURRENCY_CONVERSION", "false").lower() == "true"

logger.info("Scientific Calculator MCP Server starting...")
logger.info(f"Configuration: precision={PRECISION}, cache_size={CACHE_SIZE}")
logger.info(f"Memory limit: {MAX_MEMORY_MB}MB, computation timeout: {MAX_COMPUTATION_TIME}s")
logger.info(f"Currency conversion: {'enabled' if ENABLE_CURRENCY else 'disabled'}")
logger.info(f"Tool filtering: {filter_stats['enabled_tools']}/{filter_stats['total_tools']} tools enabled ({filter_stats['enabled_percentage']}%)")
logger.info(f"Enabled groups: {list(filter_stats['enabled_by_group'].keys())}")

# Tool registration decorator that respects filtering
def filtered_tool(tool_name: str):
    """Decorator to register tools only if they are enabled by the filter."""
    def decorator(func):
        if tool_filter.is_tool_enabled(tool_name):
            return mcp.tool(func)
        else:
            logger.debug(f"Tool '{tool_name}' filtered out (disabled)")
            return func  # Return undecorated function
    return decorator


@filtered_tool("health_check")
def health_check() -> Dict[str, Any]:
    """Health check tool to verify server functionality.

    Returns:
        Dict containing server status and configuration information.
    """
    # Get tool group configuration info
    config_info = tool_filter.config.get_configuration_info()
    availability_report = tool_filter.get_tool_availability_report()
    
    return {
        "status": "healthy",
        "server": "Scientific Calculator MCP Server",
        "version": "0.1.3",
        "precision": PRECISION,
        "cache_size": CACHE_SIZE,
        "max_computation_time": MAX_COMPUTATION_TIME,
        "max_memory_mb": MAX_MEMORY_MB,
        "currency_enabled": ENABLE_CURRENCY,
        "message": "Server is running and ready to perform calculations",
        
        # Tool group information
        "tool_groups": {
            "enabled_groups": config_info["enabled_groups"],
            "disabled_groups": config_info["disabled_groups"],
            "total_enabled_tools": config_info["total_enabled_tools"],
            "total_available_tools": config_info["total_available_tools"],
            "tool_counts_by_group": config_info["tool_counts_by_group"],
            "configuration_source": config_info["configuration_source"]
        },
        
        # Configuration warnings and recommendations
        "warnings": config_info.get("warnings", []),
        "migration_recommendations": config_info.get("migration_recommendations", []),
        
        # Detailed availability by group
        "group_details": {
            group: {
                "description": info["description"],
                "enabled_tools": len(info["enabled_tools"]),
                "total_tools": info["total_tools"],
                "is_fully_enabled": info["is_fully_enabled"]
            }
            for group, info in availability_report["groups"].items()
        },
        
        # Access monitoring information
        "access_monitoring": availability_report.get("access_monitoring", {
            "total_attempts": 0,
            "unique_tools_attempted": 0,
            "recommendations": []
        })
    }


@filtered_tool("add")
def add(a: float, b: float) -> Dict[str, Any]:
    """Add two numbers with high precision.

    Args:
        a: First number
        b: Second number

    Returns:
        Dict containing the sum and metadata.
    """
    try:
        result = basic.add(a, b)
        logger.debug(f"Addition: {a} + {b} = {result['result']}")
        return result
    except CalculatorError as e:
        logger.error(f"Addition error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected addition error: {e}")
        return ErrorResponse.from_generic_exception(e, "CalculationError").dict()


@filtered_tool("subtract")
def subtract(a: float, b: float) -> Dict[str, Any]:
    """Subtract two numbers with high precision.

    Args:
        a: First number (minuend)
        b: Second number (subtrahend)

    Returns:
        Dict containing the difference and metadata.
    """
    try:
        result = basic.subtract(a, b)
        logger.debug(f"Subtraction: {a} - {b} = {result['result']}")
        return result
    except CalculatorError as e:
        logger.error(f"Subtraction error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected subtraction error: {e}")
        return ErrorResponse.from_generic_exception(e, "CalculationError").dict()


@filtered_tool("multiply")
def multiply(a: float, b: float) -> Dict[str, Any]:
    """Multiply two numbers with high precision.

    Args:
        a: First number
        b: Second number

    Returns:
        Dict containing the product and metadata.
    """
    try:
        result = basic.multiply(a, b)
        logger.debug(f"Multiplication: {a} × {b} = {result['result']}")
        return result
    except CalculatorError as e:
        logger.error(f"Multiplication error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected multiplication error: {e}")
        return ErrorResponse.from_generic_exception(e, "CalculationError").dict()


@filtered_tool("divide")
def divide(a: float, b: float) -> Dict[str, Any]:
    """Divide two numbers with high precision.

    Args:
        a: Dividend
        b: Divisor

    Returns:
        Dict containing the quotient and metadata.
    """
    try:
        result = basic.divide(a, b)
        logger.debug(f"Division: {a} ÷ {b} = {result['result']}")
        return result
    except CalculatorError as e:
        logger.error(f"Division error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected division error: {e}")
        return ErrorResponse.from_generic_exception(e, "CalculationError").dict()


@filtered_tool("power")
def power(base: float, exponent: float) -> Dict[str, Any]:
    """Calculate base raised to the power of exponent.

    Args:
        base: Base number
        exponent: Exponent

    Returns:
        Dict containing the result and metadata.
    """
    try:
        result = basic.power(base, exponent)
        logger.debug(f"Power: {base}^{exponent} = {result['result']}")
        return result
    except CalculatorError as e:
        logger.error(f"Power error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected power error: {e}")
        return ErrorResponse.from_generic_exception(e, "CalculationError").dict()


@filtered_tool("square_root")
def square_root(value: float) -> Dict[str, Any]:
    """Calculate the principal square root of a number.

    Args:
        value: Number to find square root of

    Returns:
        Dict containing the square root and metadata.
    """
    try:
        result = basic.square_root(value)
        logger.debug(f"Square root: √{value} = {result['result']}")
        return result
    except CalculatorError as e:
        logger.error(f"Square root error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected square root error: {e}")
        return ErrorResponse.from_generic_exception(e, "CalculationError").dict()


@filtered_tool("calculate")
def calculate(expression: str) -> Dict[str, Any]:
    """Evaluate mathematical expressions safely.

    Args:
        expression: Mathematical expression to evaluate

    Returns:
        Dict containing the evaluation result and metadata.
    """
    try:
        # Validate and sanitize the expression
        sanitized_expr = validate_mathematical_expression(expression)
        logger.debug(f"Evaluating expression: {sanitized_expr}")

        # Parse and evaluate with SymPy
        parsed_expr = sp.sympify(sanitized_expr)
        result = float(parsed_expr.evalf())

        # Check if result is finite
        if not sp.oo > result > -sp.oo:
            raise ValueError("Expression evaluation resulted in infinity or undefined value")

        return {
            "result": result,
            "operation": "expression_evaluation",
            "expression": expression,
            "sanitized_expression": sanitized_expr,
            "precision": PRECISION,
            "success": True,
        }

    except CalculatorError as e:
        logger.error(f"Expression evaluation error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected expression evaluation error: {e}")
        return ErrorResponse.from_generic_exception(e, "CalculationError").dict()


@filtered_tool("trigonometric")
def trigonometric(function: str, value: float, unit: str = "radians") -> Dict[str, Any]:
    """Calculate trigonometric functions.

    Args:
        function: Trigonometric function name (sin, cos, tan, sec, csc, cot, arcsin, arccos, arctan)
        value: Input value
        unit: Angle unit for input/output ("radians" or "degrees")

    Returns:
        Dict containing the trigonometric result and metadata.
    """
    try:
        # Get the function from the registry
        trig_func = advanced.get_function(function.lower())
        
        # Check if function requires unit parameter
        if function.lower() in ['sin', 'cos', 'tan', 'sec', 'csc', 'cot', 'arcsin', 'arccos', 'arctan']:
            result_value = trig_func(value, unit)
        else:
            result_value = trig_func(value)
        
        logger.debug(f"Trigonometric: {function}({value} {unit}) = {result_value}")
        
        return {
            "result": result_value,
            "operation": "trigonometric",
            "function": function,
            "input_value": value,
            "unit": unit,
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Trigonometric error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected trigonometric error: {e}")
        return ErrorResponse.from_generic_exception(e, "CalculationError").dict()


@filtered_tool("logarithm")
def logarithm(value: float, base: str = "e") -> Dict[str, Any]:
    """Calculate logarithmic functions.

    Args:
        value: Input value (must be positive)
        base: Logarithm base ("e" for natural log, "10" for base-10, or numeric value)

    Returns:
        Dict containing the logarithm result and metadata.
    """
    try:
        if base.lower() == "e" or base == "natural":
            result_value = advanced.natural_log(value)
            base_display = "e"
        elif base == "10":
            result_value = advanced.log10(value)
            base_display = "10"
        else:
            # Try to parse as numeric base
            try:
                base_numeric = float(base)
                result_value = advanced.log_base(value, base_numeric)
                base_display = str(base_numeric)
            except ValueError:
                raise advanced.AdvancedMathError(f"Invalid logarithm base: {base}")
        
        logger.debug(f"Logarithm: log_{base_display}({value}) = {result_value}")
        
        return {
            "result": result_value,
            "operation": "logarithm",
            "input_value": value,
            "base": base_display,
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Logarithm error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected logarithm error: {e}")
        return ErrorResponse.from_generic_exception(e, "CalculationError").dict()


@filtered_tool("exponential")
def exponential(base: str, exponent: float) -> Dict[str, Any]:
    """Calculate exponential functions.

    Args:
        base: Exponential base ("e" for natural exponential, or numeric value)
        exponent: Exponent value

    Returns:
        Dict containing the exponential result and metadata.
    """
    try:
        if base.lower() == "e" or base == "natural":
            result_value = advanced.exp(exponent)
            base_display = "e"
        else:
            # Try to parse as numeric base
            try:
                base_numeric = float(base)
                result_value = advanced.power_base(base_numeric, exponent)
                base_display = str(base_numeric)
            except ValueError:
                raise advanced.AdvancedMathError(f"Invalid exponential base: {base}")
        
        logger.debug(f"Exponential: {base_display}^{exponent} = {result_value}")
        
        return {
            "result": result_value,
            "operation": "exponential",
            "base": base_display,
            "exponent": exponent,
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Exponential error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected exponential error: {e}")
        return ErrorResponse.from_generic_exception(e, "CalculationError").dict()


@filtered_tool("hyperbolic")
def hyperbolic(function: str, value: float) -> Dict[str, Any]:
    """Calculate hyperbolic functions.

    Args:
        function: Hyperbolic function name (sinh, cosh, tanh)
        value: Input value

    Returns:
        Dict containing the hyperbolic result and metadata.
    """
    try:
        # Get the function from the registry
        hyp_func = advanced.get_function(function.lower())
        result_value = hyp_func(value)
        
        logger.debug(f"Hyperbolic: {function}({value}) = {result_value}")
        
        return {
            "result": result_value,
            "operation": "hyperbolic",
            "function": function,
            "input_value": value,
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Hyperbolic error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected hyperbolic error: {e}")
        return ErrorResponse.from_generic_exception(e, "CalculationError").dict()


@filtered_tool("convert_angle")
def convert_angle(value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
    """Convert angles between radians and degrees.

    Args:
        value: Angle value to convert
        from_unit: Source unit ("radians" or "degrees")
        to_unit: Target unit ("radians" or "degrees")

    Returns:
        Dict containing the converted angle and metadata.
    """
    try:
        if from_unit.lower() == to_unit.lower():
            result_value = value
        elif from_unit.lower() == "degrees" and to_unit.lower() == "radians":
            result_value = advanced.degrees_to_radians(value)
        elif from_unit.lower() == "radians" and to_unit.lower() == "degrees":
            result_value = advanced.radians_to_degrees(value)
        else:
            raise advanced.AdvancedMathError(
                f"Invalid angle units: {from_unit} to {to_unit}. "
                "Supported units: 'radians', 'degrees'"
            )
        
        logger.debug(f"Angle conversion: {value} {from_unit} = {result_value} {to_unit}")
        
        return {
            "result": result_value,
            "operation": "angle_conversion",
            "input_value": value,
            "from_unit": from_unit,
            "to_unit": to_unit,
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Angle conversion error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected angle conversion error: {e}")
        return ErrorResponse.from_generic_exception(e, "CalculationError").dict()


@filtered_tool("descriptive_stats")
def descriptive_stats(data: list[float], sample: bool = True) -> Dict[str, Any]:
    """Calculate comprehensive descriptive statistics for a dataset.

    Args:
        data: List of numerical values
        sample: If True, calculate sample statistics (n-1). If False, population statistics (n).

    Returns:
        Dict containing descriptive statistics including mean, median, mode, std dev, variance, etc.
    """
    try:
        result = calc_stats.descriptive_statistics(data, sample)
        
        logger.debug(f"Descriptive stats: {len(data)} data points, mean={result.get('mean', 'N/A')}")
        
        return {
            "result": result,
            "operation": "descriptive_statistics",
            "data_count": len(data),
            "sample_statistics": sample,
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Descriptive statistics error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected descriptive statistics error: {e}")
        return ErrorResponse.from_generic_exception(e, "StatisticsError").dict()


@filtered_tool("probability_distribution")
def probability_distribution(distribution: str, x: float = None, mean: float = 0, std_dev: float = 1, 
                            k: int = None, n: int = None, p: float = None, 
                            lambda_param: float = None, a: float = None, b: float = None) -> Dict[str, Any]:
    """Calculate probability distribution values.

    Args:
        distribution: Distribution type (normal, binomial, poisson, uniform, exponential)
        x: Value to evaluate (for normal, uniform, exponential)
        mean: Distribution mean (for normal)
        std_dev: Distribution standard deviation (for normal)
        k: Number of successes/events (for binomial, poisson)
        n: Number of trials (for binomial)
        p: Probability of success (for binomial)
        lambda_param: Rate parameter (for poisson, exponential)
        a: Lower bound (for uniform)
        b: Upper bound (for uniform)

    Returns:
        Dict containing probability density/mass function and cumulative distribution values.
    """
    try:
        # Get the distribution function
        dist_func = calc_stats.get_distribution_function(distribution)
        
        # Build kwargs based on distribution type and provided parameters
        kwargs = {}
        if distribution.lower() in ['normal', 'gaussian']:
            if x is not None: kwargs['x'] = x
            if mean is not None: kwargs['mean'] = mean
            if std_dev is not None: kwargs['std_dev'] = std_dev
        elif distribution.lower() == 'binomial':
            if k is not None: kwargs['k'] = k
            if n is not None: kwargs['n'] = n
            if p is not None: kwargs['p'] = p
        elif distribution.lower() == 'poisson':
            if k is not None: kwargs['k'] = k
            if lambda_param is not None: kwargs['lambda_param'] = lambda_param
        elif distribution.lower() == 'uniform':
            if x is not None: kwargs['x'] = x
            if a is not None: kwargs['a'] = a
            if b is not None: kwargs['b'] = b
        elif distribution.lower() == 'exponential':
            if x is not None: kwargs['x'] = x
            if lambda_param is not None: kwargs['lambda_param'] = lambda_param
        
        # Call the distribution function with provided parameters
        result = dist_func(**kwargs)
        
        logger.debug(f"Probability distribution: {distribution} with params {kwargs}")
        
        return {
            "result": result,
            "operation": "probability_distribution",
            "distribution": distribution,
            "parameters": kwargs,
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Probability distribution error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected probability distribution error: {e}")
        return ErrorResponse.from_generic_exception(e, "StatisticsError").dict()


@filtered_tool("correlation_analysis")
def correlation_analysis(x_data: list[float], y_data: list[float]) -> Dict[str, Any]:
    """Calculate correlation coefficient between two datasets.

    Args:
        x_data: First dataset
        y_data: Second dataset

    Returns:
        Dict containing Pearson correlation coefficient and p-value.
    """
    try:
        result = calc_stats.correlation_coefficient(x_data, y_data)
        
        logger.debug(f"Correlation analysis: r={result['correlation']:.4f}, p={result['p_value']:.4f}")
        
        return {
            "result": result,
            "operation": "correlation_analysis",
            "data_points": len(x_data),
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Correlation analysis error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected correlation analysis error: {e}")
        return ErrorResponse.from_generic_exception(e, "StatisticsError").dict()


@filtered_tool("regression_analysis")
def regression_analysis(x_data: list[float], y_data: list[float]) -> Dict[str, Any]:
    """Perform linear regression analysis on two datasets.

    Args:
        x_data: Independent variable data
        y_data: Dependent variable data

    Returns:
        Dict containing regression coefficients, R-squared, and equation.
    """
    try:
        result = calc_stats.linear_regression(x_data, y_data)
        
        logger.debug(f"Regression analysis: R²={result['r_squared']:.4f}, equation={result['equation']}")
        
        return {
            "result": result,
            "operation": "regression_analysis",
            "data_points": len(x_data),
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Regression analysis error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected regression analysis error: {e}")
        return ErrorResponse.from_generic_exception(e, "StatisticsError").dict()


@filtered_tool("hypothesis_test")
def hypothesis_test(test_type: str, data: list[float] = None, data1: list[float] = None, 
                   data2: list[float] = None, population_mean: float = None, 
                   equal_var: bool = True, observed: list[float] = None, 
                   expected: list[float] = None) -> Dict[str, Any]:
    """Perform statistical hypothesis tests.

    Args:
        test_type: Type of test (t_test_one_sample, t_test_two_sample, chi_square)
        data: Data for one-sample t-test
        data1: First dataset for two-sample t-test
        data2: Second dataset for two-sample t-test
        population_mean: Population mean for one-sample t-test
        equal_var: Assume equal variances for two-sample t-test
        observed: Observed frequencies for chi-square test
        expected: Expected frequencies for chi-square test

    Returns:
        Dict containing test statistic, p-value, and test results.
    """
    try:
        # Map test types to functions
        test_functions = {
            't_test_one_sample': calc_stats.t_test_one_sample,
            'one_sample_t_test': calc_stats.t_test_one_sample,
            't_test_two_sample': calc_stats.t_test_two_sample,
            'two_sample_t_test': calc_stats.t_test_two_sample,
            'chi_square': calc_stats.chi_square_test,
            'chi_square_test': calc_stats.chi_square_test,
        }
        
        if test_type.lower() not in test_functions:
            available_tests = ', '.join(sorted(test_functions.keys()))
            raise calc_stats.ValidationError(
                f"Unknown test type: {test_type}. Available tests: {available_tests}"
            )
        
        # Build kwargs based on test type and provided parameters
        kwargs = {}
        if test_type.lower() in ['t_test_one_sample', 'one_sample_t_test']:
            if data is not None: kwargs['data'] = data
            if population_mean is not None: kwargs['population_mean'] = population_mean
        elif test_type.lower() in ['t_test_two_sample', 'two_sample_t_test']:
            if data1 is not None: kwargs['data1'] = data1
            if data2 is not None: kwargs['data2'] = data2
            if equal_var is not None: kwargs['equal_var'] = equal_var
        elif test_type.lower() in ['chi_square', 'chi_square_test']:
            if observed is not None: kwargs['observed'] = observed
            if expected is not None: kwargs['expected'] = expected
        
        # Call the test function with provided parameters
        test_func = test_functions[test_type.lower()]
        result = test_func(**kwargs)
        
        logger.debug(f"Hypothesis test: {test_type}, p-value={result.get('p_value', 'N/A')}")
        
        return {
            "result": result,
            "operation": "hypothesis_test",
            "test_type": test_type,
            "parameters": kwargs,
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Hypothesis test error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected hypothesis test error: {e}")
        return ErrorResponse.from_generic_exception(e, "StatisticsError").dict()


@filtered_tool("matrix_multiply")
def matrix_multiply(matrix_a: list[list[float]], matrix_b: list[list[float]]) -> Dict[str, Any]:
    """Multiply two matrices using matrix multiplication.

    Args:
        matrix_a: First matrix (m×n)
        matrix_b: Second matrix (n×p)

    Returns:
        Dict containing the matrix product (m×p) and metadata.
    """
    try:
        result = matrix.matrix_multiply(matrix_a, matrix_b)
        
        logger.debug(f"Matrix multiplication: {result['input_dimensions']['matrix_a']} × {result['input_dimensions']['matrix_b']} = {result['dimensions']}")
        
        return {
            "result": result,
            "operation": "matrix_multiplication",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Matrix multiplication error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected matrix multiplication error: {e}")
        return ErrorResponse.from_generic_exception(e, "MatrixError").dict()


@filtered_tool("matrix_determinant")
def matrix_determinant(matrix_data: list[list[float]]) -> Dict[str, Any]:
    """Calculate the determinant of a square matrix.

    Args:
        matrix_data: Square matrix

    Returns:
        Dict containing the determinant value and metadata.
    """
    try:
        result = matrix.matrix_determinant(matrix_data)
        
        logger.debug(f"Matrix determinant: {result['dimensions']} matrix, det = {result['result']}")
        
        return {
            "result": result,
            "operation": "matrix_determinant",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Matrix determinant error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected matrix determinant error: {e}")
        return ErrorResponse.from_generic_exception(e, "MatrixError").dict()


@filtered_tool("matrix_inverse")
def matrix_inverse(matrix_data: list[list[float]]) -> Dict[str, Any]:
    """Calculate the inverse of a square matrix.

    Args:
        matrix_data: Square invertible matrix

    Returns:
        Dict containing the matrix inverse and metadata.
    """
    try:
        result = matrix.matrix_inverse(matrix_data)
        
        logger.debug(f"Matrix inverse: {result['dimensions']} matrix, det = {result['determinant']}")
        
        return {
            "result": result,
            "operation": "matrix_inverse",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Matrix inverse error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected matrix inverse error: {e}")
        return ErrorResponse.from_generic_exception(e, "MatrixError").dict()


@filtered_tool("matrix_eigenvalues")
def matrix_eigenvalues(matrix_data: list[list[float]]) -> Dict[str, Any]:
    """Calculate eigenvalues and eigenvectors of a square matrix.

    Args:
        matrix_data: Square matrix

    Returns:
        Dict containing eigenvalues, eigenvectors, and metadata.
    """
    try:
        result = matrix.matrix_eigenvalues(matrix_data)
        
        logger.debug(f"Matrix eigenvalues: {result['dimensions']} matrix, complex: {result['has_complex_eigenvalues']}")
        
        return {
            "result": result,
            "operation": "matrix_eigenvalues",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Matrix eigenvalues error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected matrix eigenvalues error: {e}")
        return ErrorResponse.from_generic_exception(e, "MatrixError").dict()


@filtered_tool("solve_linear_system")
def solve_linear_system(coefficient_matrix: list[list[float]], constants: list[float]) -> Dict[str, Any]:
    """Solve a system of linear equations Ax = b.

    Args:
        coefficient_matrix: Coefficient matrix A
        constants: Constants vector b

    Returns:
        Dict containing the solution vector and metadata.
    """
    try:
        result = matrix.solve_linear_system(coefficient_matrix, constants)
        
        logger.debug(f"Linear system: {result['dimensions']} system, type: {result['solution_type']}")
        
        return {
            "result": result,
            "operation": "solve_linear_system",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Linear system error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected linear system error: {e}")
        return ErrorResponse.from_generic_exception(e, "MatrixError").dict()


@filtered_tool("matrix_operations")
def matrix_operations(operation: str, matrix_data: list[list[float]], 
                     norm_type: str = "frobenius") -> Dict[str, Any]:
    """Perform various matrix operations.

    Args:
        operation: Operation type (transpose, trace, rank, norm, svd, qr, etc.)
        matrix_data: Input matrix
        norm_type: Norm type for norm and condition_number operations

    Returns:
        Dict containing the operation result and metadata.
    """
    try:
        # Map operation names to functions
        operation_map = {
            'transpose': matrix.matrix_transpose,
            'trace': matrix.matrix_trace,
            'rank': matrix.matrix_rank,
            'norm': matrix.matrix_norm,
            'svd': matrix.matrix_svd,
            'qr': matrix.matrix_qr_decomposition,
            'lu': matrix.matrix_lu_decomposition,
            'condition_number': matrix.matrix_condition_number,
            'pseudoinverse': matrix.matrix_pseudoinverse,
            'is_symmetric': matrix.is_matrix_symmetric,
            'is_orthogonal': matrix.is_matrix_orthogonal,
        }
        
        if operation.lower() not in operation_map:
            available_ops = ', '.join(sorted(operation_map.keys()))
            raise matrix.ValidationError(
                f"Unknown matrix operation: {operation}. Available operations: {available_ops}"
            )
        
        # Call the operation function
        op_func = operation_map[operation.lower()]
        
        # Handle operations that need additional parameters
        if operation.lower() in ['norm', 'condition_number']:
            result = op_func(matrix_data, norm_type)
        else:
            result = op_func(matrix_data)
        
        logger.debug(f"Matrix operation: {operation} on {result.get('dimensions', 'unknown')} matrix")
        
        return {
            "result": result,
            "operation": f"matrix_{operation}",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Matrix operation error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected matrix operation error: {e}")
        return ErrorResponse.from_generic_exception(e, "MatrixError").dict()


@filtered_tool("matrix_arithmetic")
def matrix_arithmetic(operation: str, matrix_a: list[list[float]], 
                     matrix_b: list[list[float]] = None, scalar: float = None) -> Dict[str, Any]:
    """Perform matrix arithmetic operations.

    Args:
        operation: Arithmetic operation (add, subtract, scalar_multiply)
        matrix_a: First matrix
        matrix_b: Second matrix (for add/subtract operations)
        scalar: Scalar value (for scalar multiplication)

    Returns:
        Dict containing the arithmetic result and metadata.
    """
    try:
        if operation.lower() == 'add':
            if matrix_b is None:
                raise matrix.ValidationError("matrix_b is required for addition")
            result = matrix.matrix_add(matrix_a, matrix_b)
        elif operation.lower() == 'subtract':
            if matrix_b is None:
                raise matrix.ValidationError("matrix_b is required for subtraction")
            result = matrix.matrix_subtract(matrix_a, matrix_b)
        elif operation.lower() == 'scalar_multiply':
            if scalar is None:
                raise matrix.ValidationError("scalar is required for scalar multiplication")
            result = matrix.matrix_scalar_multiply(matrix_a, scalar)
        else:
            raise matrix.ValidationError(
                f"Unknown arithmetic operation: {operation}. "
                "Available operations: add, subtract, scalar_multiply"
            )
        
        logger.debug(f"Matrix arithmetic: {operation} on {result['dimensions']} matrix")
        
        return {
            "result": result,
            "operation": f"matrix_{operation}",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Matrix arithmetic error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected matrix arithmetic error: {e}")
        return ErrorResponse.from_generic_exception(e, "MatrixError").dict()


@filtered_tool("create_matrix")
def create_matrix(matrix_type: str, size: int = None, rows: int = None, cols: int = None) -> Dict[str, Any]:
    """Create special matrices (identity, zero).

    Args:
        matrix_type: Type of matrix to create (identity, zero)
        size: Size for identity matrix (creates size x size matrix)
        rows: Number of rows for zero matrix
        cols: Number of columns for zero matrix

    Returns:
        Dict containing the created matrix and metadata.
    """
    try:
        if matrix_type.lower() == 'identity':
            if size is None:
                raise matrix.ValidationError("size parameter is required for identity matrix")
            result = matrix.create_identity_matrix(size)
        elif matrix_type.lower() == 'zero':
            if rows is None or cols is None:
                raise matrix.ValidationError("rows and cols parameters are required for zero matrix")
            result = matrix.create_zero_matrix(rows, cols)
        else:
            raise matrix.ValidationError(
                f"Unknown matrix type: {matrix_type}. Available types: identity, zero"
            )
        
        logger.debug(f"Created {matrix_type} matrix: {result['dimensions']}")
        
        return {
            "result": result,
            "operation": f"create_{matrix_type}_matrix",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Matrix creation error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected matrix creation error: {e}")
        return ErrorResponse.from_generic_exception(e, "MatrixError").dict()


@filtered_tool("complex_arithmetic")
def complex_arithmetic(operation: str, z1, z2=None) -> Dict[str, Any]:
    """Perform arithmetic operations on complex numbers.

    Args:
        operation: Arithmetic operation (add, subtract, multiply, divide, power)
        z1: First complex number (various formats supported)
        z2: Second complex number (for binary operations)

    Returns:
        Dict containing the complex arithmetic result and metadata.
    """
    try:
        # Get the function from the registry
        if operation.lower() not in calc_complex.COMPLEX_ARITHMETIC_FUNCTIONS:
            available_ops = ', '.join(sorted(calc_complex.COMPLEX_ARITHMETIC_FUNCTIONS.keys()))
            raise calc_complex.ValidationError(
                f"Unknown arithmetic operation: {operation}. Available operations: {available_ops}"
            )
        
        arith_func = calc_complex.COMPLEX_ARITHMETIC_FUNCTIONS[operation.lower()]
        
        # Handle operations that need two operands
        if operation.lower() in ['add', 'subtract', 'multiply', 'divide', 'power']:
            if z2 is None:
                raise calc_complex.ValidationError(f"Operation '{operation}' requires two operands")
            result = arith_func(z1, z2)
        else:
            result = arith_func(z1)
        
        logger.debug(f"Complex arithmetic: {operation} on {result.get('operands', {}).get('z1', 'unknown')}")
        
        return {
            "result": result,
            "operation": f"complex_{operation}",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Complex arithmetic error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected complex arithmetic error: {e}")
        return ErrorResponse.from_generic_exception(e, "ComplexError").dict()


@filtered_tool("complex_magnitude")
def complex_magnitude(z) -> Dict[str, Any]:
    """Calculate the magnitude (absolute value) of a complex number.

    Args:
        z: Complex number (various formats supported)

    Returns:
        Dict containing the magnitude and metadata.
    """
    try:
        result = calc_complex.complex_magnitude(z)
        
        logger.debug(f"Complex magnitude: |{result['input_string']}| = {result['result']}")
        
        return {
            "result": result,
            "operation": "complex_magnitude",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Complex magnitude error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected complex magnitude error: {e}")
        return ErrorResponse.from_generic_exception(e, "ComplexError").dict()


@filtered_tool("complex_phase")
def complex_phase(z, unit: str = "radians") -> Dict[str, Any]:
    """Calculate the phase (argument) of a complex number.

    Args:
        z: Complex number (various formats supported)
        unit: Unit for the phase ("radians" or "degrees")

    Returns:
        Dict containing the phase and metadata.
    """
    try:
        result = calc_complex.complex_phase(z, unit)
        
        logger.debug(f"Complex phase: arg({result['input_string']}) = {result['result']} {unit}")
        
        return {
            "result": result,
            "operation": "complex_phase",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Complex phase error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected complex phase error: {e}")
        return ErrorResponse.from_generic_exception(e, "ComplexError").dict()


@filtered_tool("complex_conjugate")
def complex_conjugate(z) -> Dict[str, Any]:
    """Calculate the complex conjugate of a complex number.

    Args:
        z: Complex number (various formats supported)

    Returns:
        Dict containing the conjugate and metadata.
    """
    try:
        result = calc_complex.complex_conjugate(z)
        
        logger.debug(f"Complex conjugate: {result['input_string']}* = {result['result_string']}")
        
        return {
            "result": result,
            "operation": "complex_conjugate",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Complex conjugate error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected complex conjugate error: {e}")
        return ErrorResponse.from_generic_exception(e, "ComplexError").dict()


@filtered_tool("polar_conversion")
def polar_conversion(operation: str, z=None, magnitude: float = None, 
                    phase: float = None, unit: str = "radians") -> Dict[str, Any]:
    """Convert between rectangular and polar forms of complex numbers.

    Args:
        operation: Conversion type ("to_polar", "to_rectangular")
        z: Complex number for rectangular to polar conversion
        magnitude: Magnitude for polar to rectangular conversion
        phase: Phase for polar to rectangular conversion
        unit: Unit for phase ("radians" or "degrees")

    Returns:
        Dict containing the converted form and metadata.
    """
    try:
        if operation.lower() == "to_polar" or operation.lower() == "rectangular_to_polar":
            if z is None:
                raise calc_complex.ValidationError("'z' parameter is required for polar conversion")
            result = calc_complex.rectangular_to_polar(z, unit)
        elif operation.lower() == "to_rectangular" or operation.lower() == "polar_to_rectangular":
            if magnitude is None or phase is None:
                raise calc_complex.ValidationError("'magnitude' and 'phase' parameters are required for rectangular conversion")
            result = calc_complex.polar_to_rectangular(magnitude, phase, unit)
        else:
            raise calc_complex.ValidationError(
                f"Unknown conversion operation: {operation}. "
                "Available operations: to_polar, to_rectangular"
            )
        
        logger.debug(f"Polar conversion: {operation}")
        
        return {
            "result": result,
            "operation": f"complex_{operation}",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Polar conversion error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected polar conversion error: {e}")
        return ErrorResponse.from_generic_exception(e, "ComplexError").dict()


@filtered_tool("complex_functions")
def complex_functions(function: str, z, base=None) -> Dict[str, Any]:
    """Calculate complex mathematical functions.

    Args:
        function: Function name (exp, log, sqrt, sin, cos, tan)
        z: Complex number input
        base: Base for logarithm functions (optional)

    Returns:
        Dict containing the function result and metadata.
    """
    try:
        # Get the function from the registry
        if function.lower() not in calc_complex.COMPLEX_MATH_FUNCTIONS:
            available_funcs = ', '.join(sorted(calc_complex.COMPLEX_MATH_FUNCTIONS.keys()))
            raise calc_complex.ValidationError(
                f"Unknown complex function: {function}. Available functions: {available_funcs}"
            )
        
        math_func = calc_complex.COMPLEX_MATH_FUNCTIONS[function.lower()]
        
        # Handle functions that need additional parameters
        if function.lower() in ['log', 'ln']:
            result = math_func(z, base)
        else:
            result = math_func(z)
        
        logger.debug(f"Complex function: {function}({result['input_string']}) = {result['result_string']}")
        
        return {
            "result": result,
            "operation": f"complex_{function}",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Complex function error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected complex function error: {e}")
        return ErrorResponse.from_generic_exception(e, "ComplexError").dict()


@filtered_tool("convert_units")
def convert_units(value: float, from_unit: str, to_unit: str, unit_type: str) -> Dict[str, Any]:
    """Convert a value from one unit to another within the same unit type.

    Args:
        value: Numeric value to convert
        from_unit: Source unit name
        to_unit: Target unit name
        unit_type: Unit category (length, weight, temperature, volume, time, energy, pressure, etc.)

    Returns:
        Dict containing the converted value and metadata.
    """
    try:
        result = units.convert_units(value, from_unit, to_unit, unit_type)
        
        logger.debug(f"Unit conversion: {value} {from_unit} = {result['result']} {to_unit} ({unit_type})")
        
        return {
            "result": result,
            "operation": "unit_conversion",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Unit conversion error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected unit conversion error: {e}")
        return ErrorResponse.from_generic_exception(e, "UnitConversionError").dict()


@filtered_tool("get_available_units")
def get_available_units(unit_type: str = None) -> Dict[str, Any]:
    """Get available units for a specific type or all unit types.

    Args:
        unit_type: Optional unit category to filter by

    Returns:
        Dict containing available units and metadata.
    """
    try:
        result = units.get_available_units(unit_type)
        
        if unit_type:
            logger.debug(f"Available units for {unit_type}: {result['unit_count']} units")
        else:
            logger.debug(f"Available unit types: {result['total_types']} types")
        
        return {
            "result": result,
            "operation": "get_available_units",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Get available units error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected get available units error: {e}")
        return ErrorResponse.from_generic_exception(e, "UnitConversionError").dict()


@filtered_tool("validate_unit_compatibility")
def validate_unit_compatibility(from_unit: str, to_unit: str, unit_type: str) -> Dict[str, Any]:
    """Validate that two units are compatible for conversion.

    Args:
        from_unit: Source unit name
        to_unit: Target unit name
        unit_type: Unit category

    Returns:
        Dict containing compatibility information.
    """
    try:
        result = units.validate_unit_compatibility(from_unit, to_unit, unit_type)
        
        logger.debug(f"Unit compatibility: {from_unit} -> {to_unit} ({unit_type}): {result['compatible']}")
        
        return {
            "result": result,
            "operation": "validate_unit_compatibility",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Unit compatibility validation error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected unit compatibility validation error: {e}")
        return ErrorResponse.from_generic_exception(e, "UnitConversionError").dict()


@filtered_tool("get_conversion_factor")
def get_conversion_factor(from_unit: str, to_unit: str, unit_type: str) -> Dict[str, Any]:
    """Get the conversion factor between two units.

    Args:
        from_unit: Source unit name
        to_unit: Target unit name
        unit_type: Unit category

    Returns:
        Dict containing the conversion factor and metadata.
    """
    try:
        result = units.get_conversion_factor(from_unit, to_unit, unit_type)
        
        logger.debug(f"Conversion factor: {from_unit} -> {to_unit} = {result['conversion_factor']}")
        
        return {
            "result": result,
            "operation": "get_conversion_factor",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Get conversion factor error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected get conversion factor error: {e}")
        return ErrorResponse.from_generic_exception(e, "UnitConversionError").dict()


@filtered_tool("convert_multiple_units")
def convert_multiple_units(value: float, from_unit: str, to_units: list[str], unit_type: str) -> Dict[str, Any]:
    """Convert a value to multiple target units.

    Args:
        value: Numeric value to convert
        from_unit: Source unit name
        to_units: List of target unit names
        unit_type: Unit category

    Returns:
        Dict containing multiple conversion results.
    """
    try:
        result = units.convert_multiple_units(value, from_unit, to_units, unit_type)
        
        logger.debug(f"Multiple unit conversion: {value} {from_unit} -> {len(to_units)} units, {result['successful_conversions']} successful")
        
        return {
            "result": result,
            "operation": "convert_multiple_units",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Multiple unit conversion error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected multiple unit conversion error: {e}")
        return ErrorResponse.from_generic_exception(e, "UnitConversionError").dict()


@filtered_tool("find_unit_by_name")
def find_unit_by_name(unit_name: str) -> Dict[str, Any]:
    """Find which unit type(s) contain a specific unit name.

    Args:
        unit_name: Unit name to search for

    Returns:
        Dict containing matching unit types and information.
    """
    try:
        result = units.find_unit_by_name(unit_name)
        
        logger.debug(f"Unit search: '{unit_name}' found in {result['match_count']} unit types")
        
        return {
            "result": result,
            "operation": "find_unit_by_name",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Find unit by name error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected find unit by name error: {e}")
        return ErrorResponse.from_generic_exception(e, "UnitConversionError").dict()


@filtered_tool("get_unit_info")
def get_unit_info(unit_name: str, unit_type: str) -> Dict[str, Any]:
    """Get detailed information about a specific unit.

    Args:
        unit_name: Unit name
        unit_type: Unit category

    Returns:
        Dict containing detailed unit information.
    """
    try:
        result = units.get_unit_info(unit_name, unit_type)
        
        logger.debug(f"Unit info: {unit_name} ({unit_type})")
        
        return {
            "result": result,
            "operation": "get_unit_info",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Get unit info error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected get unit info error: {e}")
        return ErrorResponse.from_generic_exception(e, "UnitConversionError").dict()


@filtered_tool("derivative")
def derivative(expression: str, variable: str, order: int = 1) -> Dict[str, Any]:
    """Calculate symbolic derivative of an expression.

    Args:
        expression: Mathematical expression to differentiate
        variable: Variable to differentiate with respect to
        order: Order of derivative (default: 1)

    Returns:
        Dict containing the derivative and metadata.
    """
    try:
        result = calculus.symbolic_derivative(expression, variable, order)
        
        logger.debug(f"Derivative: d^{order}/d{variable}^{order}({expression}) = {result['simplified']}")
        
        return {
            "result": result,
            "operation": "symbolic_derivative",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Derivative error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected derivative error: {e}")
        return ErrorResponse.from_generic_exception(e, "CalculusError").dict()


@filtered_tool("integral")
def integral(expression: str, variable: str, lower_bound: float = None, upper_bound: float = None) -> Dict[str, Any]:
    """Calculate symbolic integral (definite or indefinite) of an expression.

    Args:
        expression: Mathematical expression to integrate
        variable: Variable to integrate with respect to
        lower_bound: Lower bound for definite integral (optional)
        upper_bound: Upper bound for definite integral (optional)

    Returns:
        Dict containing the integral and metadata.
    """
    try:
        if lower_bound is not None and upper_bound is not None:
            # Definite integral
            result = calculus.definite_integral(expression, variable, lower_bound, upper_bound)
            operation_type = "definite_integral"
        else:
            # Indefinite integral
            result = calculus.symbolic_integral(expression, variable)
            operation_type = "indefinite_integral"
        
        logger.debug(f"Integral: ∫{expression} d{variable} = {result.get('simplified', result.get('result', 'N/A'))}")
        
        return {
            "result": result,
            "operation": operation_type,
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Integral error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected integral error: {e}")
        return ErrorResponse.from_generic_exception(e, "CalculusError").dict()


@filtered_tool("numerical_derivative")
def numerical_derivative(expression: str, variable: str, point: float, order: int = 1, dx: float = 1e-5) -> Dict[str, Any]:
    """Calculate numerical derivative at a specific point.

    Args:
        expression: Mathematical expression to differentiate
        variable: Variable to differentiate with respect to
        point: Point at which to evaluate the derivative
        order: Order of derivative (default: 1)
        dx: Step size for numerical differentiation (default: 1e-5)

    Returns:
        Dict containing the numerical derivative value and metadata.
    """
    try:
        result = calculus.numerical_derivative(expression, variable, point, order, dx)
        
        logger.debug(f"Numerical derivative: f^({order})({point}) = {result.get('derivative_value', 'N/A')}")
        
        return {
            "result": result,
            "operation": "numerical_derivative",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Numerical derivative error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected numerical derivative error: {e}")
        return ErrorResponse.from_generic_exception(e, "CalculusError").dict()


@filtered_tool("numerical_integral")
def numerical_integral(expression: str, variable: str, lower_bound: float, upper_bound: float, method: str = "quad") -> Dict[str, Any]:
    """Calculate numerical integral using scipy integration methods.

    Args:
        expression: Mathematical expression to integrate
        variable: Variable to integrate with respect to
        lower_bound: Lower bound of integration
        upper_bound: Upper bound of integration
        method: Integration method ("quad", "simpson", "trapz")

    Returns:
        Dict containing the numerical integral value and metadata.
    """
    try:
        result = calculus.numerical_integral(expression, variable, lower_bound, upper_bound, method)
        
        logger.debug(f"Numerical integral: ∫[{lower_bound},{upper_bound}]{expression} d{variable} = {result.get('result', 'N/A')} ({method})")
        
        return {
            "result": result,
            "operation": "numerical_integral",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Numerical integral error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected numerical integral error: {e}")
        return ErrorResponse.from_generic_exception(e, "CalculusError").dict()


@filtered_tool("calculate_limit")
def calculate_limit(expression: str, variable: str, approach_value: str, direction: str = "both") -> Dict[str, Any]:
    """Calculate limit of an expression as variable approaches a value.

    Args:
        expression: Mathematical expression
        variable: Variable approaching the limit
        approach_value: Value being approached (number, "inf", "-inf")
        direction: Direction of approach ("both", "left", "right")

    Returns:
        Dict containing the limit and metadata.
    """
    try:
        result = calculus.calculate_limit(expression, variable, approach_value, direction)
        
        logger.debug(f"Limit: lim({variable}->{approach_value}) {expression} = {result.get('limit', 'N/A')}")
        
        return {
            "result": result,
            "operation": "calculate_limit",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Limit calculation error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected limit calculation error: {e}")
        return ErrorResponse.from_generic_exception(e, "CalculusError").dict()


@filtered_tool("taylor_series")
def taylor_series(expression: str, variable: str, center: float = 0, order: int = 5) -> Dict[str, Any]:
    """Calculate Taylor series expansion of an expression.

    Args:
        expression: Mathematical expression to expand
        variable: Variable for the expansion
        center: Center point of expansion (default: 0)
        order: Order of the series expansion (default: 5)

    Returns:
        Dict containing the Taylor series and metadata.
    """
    try:
        result = calculus.taylor_series(expression, variable, center, order)
        
        logger.debug(f"Taylor series: {expression} around {variable}={center}, order {order}")
        
        return {
            "result": result,
            "operation": "taylor_series",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Taylor series error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected Taylor series error: {e}")
        return ErrorResponse.from_generic_exception(e, "CalculusError").dict()


@filtered_tool("find_critical_points")
def find_critical_points(expression: str, variable: str) -> Dict[str, Any]:
    """Find critical points of a single-variable function.

    Args:
        expression: Mathematical expression
        variable: Variable to analyze

    Returns:
        Dict containing critical points and their classifications.
    """
    try:
        result = calculus.find_critical_points(expression, variable)
        
        logger.debug(f"Critical points: {expression}, found {len(result.get('numerical_critical_points', []))} numerical points")
        
        return {
            "result": result,
            "operation": "find_critical_points",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Critical points error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected critical points error: {e}")
        return ErrorResponse.from_generic_exception(e, "CalculusError").dict()


@filtered_tool("gradient")
def gradient(expression: str, variables: list[str]) -> Dict[str, Any]:
    """Calculate gradient (vector of partial derivatives) of a multi-variable function.

    Args:
        expression: Mathematical expression
        variables: List of variables

    Returns:
        Dict containing the gradient vector and metadata.
    """
    try:
        result = calculus.gradient(expression, variables)
        
        logger.debug(f"Gradient: ∇({expression}) with variables {variables}")
        
        return {
            "result": result,
            "operation": "gradient",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Gradient error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected gradient error: {e}")
        return ErrorResponse.from_generic_exception(e, "CalculusError").dict()


@filtered_tool("evaluate_expression")
def evaluate_expression(expression: str, variable_values: dict) -> Dict[str, Any]:
    """Evaluate a mathematical expression at specific variable values.

    Args:
        expression: Mathematical expression
        variable_values: Dictionary mapping variable names to values

    Returns:
        Dict containing the evaluated result and metadata.
    """
    try:
        result = calculus.evaluate_expression(expression, variable_values)
        
        logger.debug(f"Expression evaluation: {expression} at {variable_values} = {result.get('result', 'N/A')}")
        
        return {
            "result": result,
            "operation": "evaluate_expression",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Expression evaluation error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected expression evaluation error: {e}")
        return ErrorResponse.from_generic_exception(e, "CalculusError").dict()


@filtered_tool("solve_linear")
def solve_linear(equation: str, variable: str) -> Dict[str, Any]:
    """Solve a linear equation for a single variable.

    Args:
        equation: Linear equation to solve (e.g., "2*x + 3 = 7")
        variable: Variable to solve for

    Returns:
        Dict containing the solution and metadata.
    """
    try:
        result = solver.solve_linear(equation, variable)
        
        logger.debug(f"Linear equation: {equation}, solutions: {len(result.get('solutions', []))}")
        
        return {
            "result": result,
            "operation": "solve_linear",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Linear equation solving error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected linear equation solving error: {e}")
        return ErrorResponse.from_generic_exception(e, "SolverError").dict()


@filtered_tool("solve_quadratic")
def solve_quadratic(equation: str, variable: str) -> Dict[str, Any]:
    """Solve a quadratic equation and provide detailed analysis.

    Args:
        equation: Quadratic equation to solve (e.g., "x^2 - 5*x + 6 = 0")
        variable: Variable to solve for

    Returns:
        Dict containing solutions, discriminant, vertex, and other analysis.
    """
    try:
        result = solver.solve_quadratic(equation, variable)
        
        logger.debug(f"Quadratic equation: {equation}, type: {result.get('solution_type', 'unknown')}")
        
        return {
            "result": result,
            "operation": "solve_quadratic",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Quadratic equation solving error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected quadratic equation solving error: {e}")
        return ErrorResponse.from_generic_exception(e, "SolverError").dict()


@filtered_tool("solve_polynomial")
def solve_polynomial(equation: str, variable: str) -> Dict[str, Any]:
    """Solve polynomial equations of any degree.

    Args:
        equation: Polynomial equation to solve
        variable: Variable to solve for

    Returns:
        Dict containing all solutions and polynomial analysis.
    """
    try:
        result = solver.solve_polynomial(equation, variable)
        
        logger.debug(f"Polynomial equation: {equation}, degree: {result.get('analysis', {}).get('degree', 'unknown')}")
        
        return {
            "result": result,
            "operation": "solve_polynomial",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Polynomial equation solving error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected polynomial equation solving error: {e}")
        return ErrorResponse.from_generic_exception(e, "SolverError").dict()


@filtered_tool("solve_system")
def solve_system(equations: list[str], variables: list[str]) -> Dict[str, Any]:
    """Solve a system of equations.

    Args:
        equations: List of equations to solve
        variables: List of variables to solve for

    Returns:
        Dict containing the system solution and analysis.
    """
    try:
        result = solver.solve_system(equations, variables)
        
        logger.debug(f"System of equations: {len(equations)} equations, {len(variables)} variables")
        
        return {
            "result": result,
            "operation": "solve_system",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"System solving error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected system solving error: {e}")
        return ErrorResponse.from_generic_exception(e, "SolverError").dict()


@filtered_tool("find_roots")
def find_roots(expression: str, variable: str, initial_guess: float = None, method: str = "auto") -> Dict[str, Any]:
    """Find roots of arbitrary functions using numerical methods.

    Args:
        expression: Mathematical expression to find roots for
        variable: Variable to solve for
        initial_guess: Initial guess for numerical methods (optional)
        method: Root finding method ("auto", "brentq", "newton", "secant", "bisect")

    Returns:
        Dict containing found roots and method information.
    """
    try:
        result = solver.find_roots(expression, variable, initial_guess, method)
        
        logger.debug(f"Root finding: {expression}, method: {method}, found: {len(result.get('roots', []))} roots")
        
        return {
            "result": result,
            "operation": "find_roots",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Root finding error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected root finding error: {e}")
        return ErrorResponse.from_generic_exception(e, "SolverError").dict()


@filtered_tool("analyze_equation")
def analyze_equation(equation: str, variable: str) -> Dict[str, Any]:
    """Analyze an equation to determine its type and properties.

    Args:
        equation: Equation to analyze
        variable: Primary variable of interest

    Returns:
        Dict containing equation analysis including type, degree, and properties.
    """
    try:
        result = solver.analyze_equation(equation, variable)
        
        logger.debug(f"Equation analysis: {equation}, type: {result.get('analysis', {}).get('equation_type', 'unknown')}")
        
        return {
            "result": result,
            "operation": "analyze_equation",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Equation analysis error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected equation analysis error: {e}")
        return ErrorResponse.from_generic_exception(e, "SolverError").dict()


@filtered_tool("compound_interest")
def compound_interest(principal: float, rate: float, time: float, compounding_frequency: int = 1) -> Dict[str, Any]:
    """Calculate compound interest and future value.

    Args:
        principal: Initial principal amount
        rate: Annual interest rate (as decimal, e.g., 0.05 for 5%)
        time: Time period in years
        compounding_frequency: Number of times interest is compounded per year

    Returns:
        Dict containing future value, compound interest, and analysis.
    """
    try:
        result = financial.compound_interest(principal, rate, time, compounding_frequency)
        
        logger.debug(f"Compound interest: ${principal} at {rate*100}% for {time} years = ${result['future_value']:.2f}")
        
        return {
            "result": result,
            "operation": "compound_interest",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Compound interest error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected compound interest error: {e}")
        return ErrorResponse.from_generic_exception(e, "FinancialError").dict()


@filtered_tool("loan_payment")
def loan_payment(principal: float, rate: float, periods: int, payment_type: str = "end") -> Dict[str, Any]:
    """Calculate loan payment amount (PMT).

    Args:
        principal: Loan principal amount
        rate: Interest rate per period (as decimal)
        periods: Number of payment periods
        payment_type: "end" for ordinary annuity, "begin" for annuity due

    Returns:
        Dict containing payment amount and loan analysis.
    """
    try:
        result = financial.loan_payment(principal, rate, periods, payment_type)
        
        logger.debug(f"Loan payment: ${principal} at {rate*100}% for {periods} periods = ${result['payment']:.2f}")
        
        return {
            "result": result,
            "operation": "loan_payment",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Loan payment error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected loan payment error: {e}")
        return ErrorResponse.from_generic_exception(e, "FinancialError").dict()


@filtered_tool("net_present_value")
def net_present_value(cash_flows: list[float], discount_rate: float, initial_investment: float = 0) -> Dict[str, Any]:
    """Calculate Net Present Value (NPV) of cash flows.

    Args:
        cash_flows: List of cash flows for each period
        discount_rate: Discount rate per period (as decimal)
        initial_investment: Initial investment (negative cash flow at t=0)

    Returns:
        Dict containing NPV and profitability analysis.
    """
    try:
        result = financial.net_present_value(cash_flows, discount_rate, initial_investment)
        
        logger.debug(f"NPV: {len(cash_flows)} cash flows at {discount_rate*100}% = ${result['npv']:.2f}")
        
        return {
            "result": result,
            "operation": "net_present_value",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"NPV error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected NPV error: {e}")
        return ErrorResponse.from_generic_exception(e, "FinancialError").dict()


@filtered_tool("internal_rate_of_return")
def internal_rate_of_return(cash_flows: list[float], initial_investment: float) -> Dict[str, Any]:
    """Calculate Internal Rate of Return (IRR).

    Args:
        cash_flows: List of cash flows for each period
        initial_investment: Initial investment amount

    Returns:
        Dict containing IRR and convergence information.
    """
    try:
        result = financial.internal_rate_of_return(cash_flows, initial_investment)
        
        logger.debug(f"IRR: {len(cash_flows)} cash flows = {result['irr_percentage']:.2f}%")
        
        return {
            "result": result,
            "operation": "internal_rate_of_return",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"IRR error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected IRR error: {e}")
        return ErrorResponse.from_generic_exception(e, "FinancialError").dict()


@filtered_tool("present_value")
def present_value(future_value: float, rate: float, periods: int) -> Dict[str, Any]:
    """Calculate present value of a future amount.

    Args:
        future_value: Future value amount
        rate: Discount rate per period (as decimal)
        periods: Number of periods

    Returns:
        Dict containing present value and discount analysis.
    """
    try:
        result = financial.present_value(future_value, rate, periods)
        
        logger.debug(f"Present value: ${future_value} at {rate*100}% for {periods} periods = ${result['present_value']:.2f}")
        
        return {
            "result": result,
            "operation": "present_value",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Present value error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected present value error: {e}")
        return ErrorResponse.from_generic_exception(e, "FinancialError").dict()


@filtered_tool("future_value_annuity")
def future_value_annuity(payment: float, rate: float, periods: int, payment_type: str = "end") -> Dict[str, Any]:
    """Calculate future value of an annuity.

    Args:
        payment: Payment amount per period
        rate: Interest rate per period (as decimal)
        periods: Number of payment periods
        payment_type: "end" for ordinary annuity, "begin" for annuity due

    Returns:
        Dict containing future value of annuity and analysis.
    """
    try:
        result = financial.future_value_annuity(payment, rate, periods, payment_type)
        
        logger.debug(f"FV Annuity: ${payment} payments at {rate*100}% for {periods} periods = ${result['future_value']:.2f}")
        
        return {
            "result": result,
            "operation": "future_value_annuity",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Future value annuity error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected future value annuity error: {e}")
        return ErrorResponse.from_generic_exception(e, "FinancialError").dict()


@filtered_tool("amortization_schedule")
def amortization_schedule(principal: float, rate: float, periods: int, max_periods_display: int = 12) -> Dict[str, Any]:
    """Generate loan amortization schedule.

    Args:
        principal: Loan principal amount
        rate: Interest rate per period (as decimal)
        periods: Number of payment periods
        max_periods_display: Maximum periods to show in detailed schedule

    Returns:
        Dict containing amortization schedule and summary.
    """
    try:
        result = financial.amortization_schedule(principal, rate, periods, max_periods_display)
        
        logger.debug(f"Amortization: ${principal} loan, {periods} periods, showing {len(result['schedule'])} periods")
        
        return {
            "result": result,
            "operation": "amortization_schedule",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Amortization schedule error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected amortization schedule error: {e}")
        return ErrorResponse.from_generic_exception(e, "FinancialError").dict()


@filtered_tool("convert_currency")
def convert_currency(amount: float, from_currency: str, to_currency: str) -> Dict[str, Any]:
    """Convert currency with privacy controls and fallback mechanisms.

    Args:
        amount: Amount to convert
        from_currency: Source currency code (3-letter ISO code)
        to_currency: Target currency code (3-letter ISO code)

    Returns:
        Dict containing converted amount and exchange rate information.
    """
    try:
        result = currency.convert_currency(amount, from_currency, to_currency)
        
        logger.debug(f"Currency conversion: {amount} {from_currency} = {result['converted_amount']} {to_currency}")
        
        return {
            "result": result,
            "operation": "convert_currency",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Currency conversion error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected currency conversion error: {e}")
        return ErrorResponse.from_generic_exception(e, "CurrencyError").dict()


@filtered_tool("get_exchange_rate")
def get_exchange_rate(from_currency: str, to_currency: str) -> Dict[str, Any]:
    """Get exchange rate between two currencies.

    Args:
        from_currency: Source currency code
        to_currency: Target currency code

    Returns:
        Dict containing exchange rate and metadata.
    """
    try:
        result = currency.get_exchange_rate(from_currency, to_currency)
        
        logger.debug(f"Exchange rate: 1 {from_currency} = {result['exchange_rate']} {to_currency}")
        
        return {
            "result": result,
            "operation": "get_exchange_rate",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Exchange rate error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected exchange rate error: {e}")
        return ErrorResponse.from_generic_exception(e, "CurrencyError").dict()


@filtered_tool("get_supported_currencies")
def get_supported_currencies() -> Dict[str, Any]:
    """Get list of supported currencies.

    Returns:
        Dict containing list of supported currency codes.
    """
    try:
        result = currency.get_supported_currencies()
        
        logger.debug(f"Supported currencies: {result['count']} currencies available")
        
        return {
            "result": result,
            "operation": "get_supported_currencies",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Get supported currencies error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected get supported currencies error: {e}")
        return ErrorResponse.from_generic_exception(e, "CurrencyError").dict()


@filtered_tool("get_currency_info")
def get_currency_info() -> Dict[str, Any]:
    """Get information about currency conversion configuration and status.

    Returns:
        Dict containing currency conversion configuration and status.
    """
    try:
        result = currency.get_currency_info()
        
        logger.debug(f"Currency info: enabled={result['currency_enabled']}, cache_size={result['cache_size']}")
        
        return {
            "result": result,
            "operation": "get_currency_info",
            "precision": PRECISION,
            "success": True,
        }
        
    except Exception as e:
        logger.error(f"Unexpected get currency info error: {e}")
        return ErrorResponse.from_generic_exception(e, "CurrencyError").dict()


@filtered_tool("get_constant")
def get_constant(name: str, precision: str = "standard") -> Dict[str, Any]:
    """Get a mathematical or physical constant by name.

    Args:
        name: Name of the constant (e.g., "pi", "e", "c", "h")
        precision: "standard" for float precision, "high" for high precision string

    Returns:
        Dict containing constant value, symbol, description, and metadata.
    """
    try:
        result = constants.get_constant(name, precision)
        
        logger.debug(f"Constant: {name} = {result['requested_value']} ({result['symbol']})")
        
        return {
            "result": result,
            "operation": "get_constant",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Get constant error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected get constant error: {e}")
        return ErrorResponse.from_generic_exception(e, "ConstantsError").dict()


@filtered_tool("list_constants")
def list_constants(category: str = None) -> Dict[str, Any]:
    """List available constants, optionally filtered by category.

    Args:
        category: Optional category filter ("mathematical", "physical", "astronomical")

    Returns:
        Dict containing list of constants with their information.
    """
    try:
        result = constants.list_constants(category)
        
        logger.debug(f"List constants: {result['count']} constants" + (f" in {category}" if category else ""))
        
        return {
            "result": result,
            "operation": "list_constants",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"List constants error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected list constants error: {e}")
        return ErrorResponse.from_generic_exception(e, "ConstantsError").dict()


@filtered_tool("search_constants")
def search_constants(query: str) -> Dict[str, Any]:
    """Search constants by name, symbol, or description.

    Args:
        query: Search query string

    Returns:
        Dict containing matching constants.
    """
    try:
        result = constants.search_constants(query)
        
        logger.debug(f"Search constants: '{query}' found {result['count']} matches")
        
        return {
            "result": result,
            "operation": "search_constants",
            "precision": PRECISION,
            "success": True,
        }
        
    except CalculatorError as e:
        logger.error(f"Search constants error: {e}")
        return ErrorResponse.from_exception(e).dict()
    except Exception as e:
        logger.error(f"Unexpected search constants error: {e}")
        return ErrorResponse.from_generic_exception(e, "ConstantsError").dict()


@mcp.resource("constants://{category}/{name}")
def get_constant_resource(category: str, name: str) -> str:
    """Get mathematical or physical constants as MCP resources.

    Args:
        category: Category of constant ("mathematical", "physical", "astronomical")
        name: Name of the constant

    Returns:
        String containing constant information in markdown format.
    """
    try:
        # Get the constant
        constant_info = constants.get_constant(name)
        
        # Format as markdown
        markdown = f"""# {constant_info['symbol']} - {name.title()}

**Value:** {constant_info['value']}
**High Precision:** {constant_info['high_precision']}
**Symbol:** {constant_info['symbol']}
**Category:** {constant_info['category']}
**Unit:** {constant_info['unit']}

**Description:** {constant_info['description']}

---
*Source: Scientific Calculator MCP Server Constants Database*
"""
        
        return markdown
        
    except Exception as e:
        return f"Error retrieving constant {name}: {e}"


@mcp.resource("formulas://{domain}/{formula}")
def get_formula_resource(domain: str, formula: str) -> str:
    """Get mathematical formulas as MCP resources.

    Args:
        domain: Domain of formula ("algebra", "calculus", "geometry", "physics")
        formula: Name of the formula

    Returns:
        String containing formula information in markdown format.
    """
    try:
        # Basic formula database (could be expanded)
        formulas = {
            "algebra": {
                "quadratic": {
                    "formula": "x = (-b ± √(b² - 4ac)) / (2a)",
                    "description": "Quadratic formula for solving ax² + bx + c = 0",
                    "variables": "a, b, c are coefficients; x is the variable"
                },
                "distance": {
                    "formula": "d = √((x₂ - x₁)² + (y₂ - y₁)²)",
                    "description": "Distance formula between two points",
                    "variables": "(x₁, y₁) and (x₂, y₂) are coordinates of two points"
                }
            },
            "calculus": {
                "derivative_power": {
                    "formula": "d/dx[xⁿ] = n·xⁿ⁻¹",
                    "description": "Power rule for derivatives",
                    "variables": "n is any real number"
                },
                "integral_power": {
                    "formula": "∫xⁿ dx = xⁿ⁺¹/(n+1) + C",
                    "description": "Power rule for integrals",
                    "variables": "n ≠ -1, C is the constant of integration"
                }
            },
            "geometry": {
                "circle_area": {
                    "formula": "A = πr²",
                    "description": "Area of a circle",
                    "variables": "r is the radius"
                },
                "sphere_volume": {
                    "formula": "V = (4/3)πr³",
                    "description": "Volume of a sphere",
                    "variables": "r is the radius"
                }
            },
            "physics": {
                "kinetic_energy": {
                    "formula": "KE = ½mv²",
                    "description": "Kinetic energy formula",
                    "variables": "m is mass, v is velocity"
                },
                "force": {
                    "formula": "F = ma",
                    "description": "Newton's second law of motion",
                    "variables": "F is force, m is mass, a is acceleration"
                }
            }
        }
        
        if domain not in formulas:
            return f"Domain '{domain}' not found. Available domains: {', '.join(formulas.keys())}"
        
        if formula not in formulas[domain]:
            available = ', '.join(formulas[domain].keys())
            return f"Formula '{formula}' not found in {domain}. Available: {available}"
        
        formula_info = formulas[domain][formula]
        
        markdown = f"""# {formula.title()} Formula

**Formula:** {formula_info['formula']}

**Description:** {formula_info['description']}

**Variables:** {formula_info['variables']}

**Domain:** {domain.title()}

---
*Source: Scientific Calculator MCP Server Formula Database*
"""
        
        return markdown
        
    except Exception as e:
        return f"Error retrieving formula {formula}: {e}"


def get_disabled_tool_info(tool_name: str) -> Dict[str, Any]:
    """Get information about a disabled tool for error responses."""
    error_info = tool_filter.get_disabled_tool_error(tool_name)
    return error_info


def log_server_startup_info() -> None:
    """Log comprehensive server startup information."""
    config_info = tool_filter.config.get_configuration_info()
    availability_report = tool_filter.get_tool_availability_report()
    
    logger.info("=" * 60)
    logger.info("Scientific Calculator MCP Server - Tool Configuration")
    logger.info("=" * 60)
    logger.info(f"Configuration Source: {config_info['configuration_source']}")
    logger.info(f"Enabled Groups: {', '.join(config_info['enabled_groups'])}")
    logger.info(f"Disabled Groups: {', '.join(config_info['disabled_groups'])}")
    logger.info(f"Total Tools: {config_info['total_enabled_tools']}/{config_info['total_available_tools']} enabled")
    
    # Log group details
    for group_name, group_info in availability_report["groups"].items():
        status = "✓" if group_info["is_fully_enabled"] else "✗" if group_info["is_fully_disabled"] else "~"
        logger.info(f"  {status} {group_name}: {group_info['enabled_count']}/{group_info['total_tools']} tools")
    
    # Log warnings if any
    if config_info.get("warnings"):
        logger.warning("Configuration Warnings:")
        for warning in config_info["warnings"]:
            logger.warning(f"  - {warning}")
    
    # Log migration recommendations if any
    if config_info.get("migration_recommendations"):
        logger.info("Migration Recommendations:")
        for recommendation in config_info["migration_recommendations"]:
            logger.info(f"  - {recommendation}")
    
    logger.info("=" * 60)


def main() -> None:
    """Main entry point for uvx execution."""
    logger.info("Starting Scientific Calculator MCP Server...")
    
    # Log detailed startup information
    log_server_startup_info()

    try:
        # Run the FastMCP server
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        logger.info("Scientific Calculator MCP Server stopped")


if __name__ == "__main__":
    main()
