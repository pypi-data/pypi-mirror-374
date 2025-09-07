# Scientific Calculator MCP Server - API Documentation

## Overview

The Scientific Calculator MCP Server provides **68 comprehensive mathematical tools** through the Model Context Protocol (MCP). This document describes all available tools and their usage.

## Tool Categories

The server provides tools across 10 major categories:
- **Basic Arithmetic** (8 tools): Core mathematical operations
- **Advanced Mathematics** (5 tools): Trigonometric, logarithmic, exponential functions
- **Statistics** (5 tools): Descriptive statistics, probability, regression, hypothesis testing
- **Matrix Operations** (8 tools): Linear algebra, eigenvalues, system solving
- **Complex Numbers** (6 tools): Complex arithmetic and conversions
- **Unit Conversion** (7 tools): Physical unit conversions across multiple types
- **Calculus** (9 tools): Symbolic and numerical calculus operations
- **Equation Solving** (6 tools): Linear, quadratic, polynomial, and system solving
- **Financial Mathematics** (7 tools): Interest, NPV, IRR, loan calculations
- **Currency Conversion** (4 tools): Exchange rates and currency conversion
- **Constants & References** (3 tools): Mathematical and physical constants database

## Server Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CALCULATOR_PRECISION` | `15` | Number of decimal places for calculations |
| `CALCULATOR_LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `CALCULATOR_CACHE_SIZE` | `1000` | Cache size for expensive operations |
| `CALCULATOR_MAX_COMPUTATION_TIME` | `30` | Maximum computation time in seconds |
| `CALCULATOR_MAX_MEMORY_MB` | `512` | Maximum memory usage in MB |
| `CALCULATOR_ENABLE_CURRENCY_CONVERSION` | `false` | Enable currency conversion (privacy-controlled) |
| `CALCULATOR_CURRENCY_API_KEY` | `""` | API key for currency conversion |

## Tools Reference

### Basic Arithmetic Operations

#### `add(a: float, b: float)`
Add two numbers with high precision.

**Parameters:**
- `a`: First number
- `b`: Second number

**Returns:** Sum with metadata

**Example:**
```json
{
  "result": {
    "result": 8.0,
    "operation": "addition",
    "precision": 15,
    "success": true
  }
}
```

#### `subtract(a: float, b: float)`
Subtract two numbers with high precision.

#### `multiply(a: float, b: float)`
Multiply two numbers with high precision.

#### `divide(a: float, b: float)`
Divide two numbers with high precision. Returns error for division by zero.

#### `power(base: float, exponent: float)`
Calculate base raised to the power of exponent.

#### `square_root(value: float)`
Calculate the principal square root of a number.

#### `calculate(expression: str)`
Evaluate mathematical expressions safely using SymPy.

**Parameters:**
- `expression`: Mathematical expression (e.g., "2*x + 3" where x is a number)

### Advanced Mathematical Functions

#### `trigonometric(function: str, value: float, unit: str = "radians")`
Calculate trigonometric functions.

**Parameters:**
- `function`: Function name (sin, cos, tan, sec, csc, cot, arcsin, arccos, arctan)
- `value`: Input value
- `unit`: "radians" or "degrees"

**Example:**
```json
{
  "function": "sin",
  "value": 1.5708,
  "unit": "radians"
}
```

#### `logarithm(value: float, base: str = "e")`
Calculate logarithmic functions.

**Parameters:**
- `value`: Input value (must be positive)
- `base`: "e" for natural log, "10" for base-10, or numeric value

#### `exponential(base: str, exponent: float)`
Calculate exponential functions.

#### `hyperbolic(function: str, value: float)`
Calculate hyperbolic functions (sinh, cosh, tanh).

#### `convert_angle(value: float, from_unit: str, to_unit: str)`
Convert angles between radians and degrees.

### Statistical Operations

#### `descriptive_stats(data: list[float], sample: bool = True)`
Calculate comprehensive descriptive statistics.

**Parameters:**
- `data`: List of numerical values
- `sample`: If True, calculate sample statistics (n-1). If False, population statistics (n)

**Returns:** Mean, median, mode, standard deviation, variance, quartiles, etc.

#### `probability_distribution(distribution: str, ...)`
Calculate probability distribution values.

**Supported Distributions:**
- `normal`: Parameters: x, mean, std_dev
- `binomial`: Parameters: k, n, p
- `poisson`: Parameters: k, lambda_param
- `uniform`: Parameters: x, a, b
- `exponential`: Parameters: x, lambda_param

#### `correlation_analysis(x_data: list[float], y_data: list[float])`
Calculate Pearson correlation coefficient between two datasets.

#### `regression_analysis(x_data: list[float], y_data: list[float])`
Perform linear regression analysis.

#### `hypothesis_test(test_type: str, ...)`
Perform statistical hypothesis tests.

**Supported Tests:**
- `t_test_one_sample`: Parameters: data, population_mean
- `t_test_two_sample`: Parameters: data1, data2, equal_var
- `chi_square`: Parameters: observed, expected

### Matrix Operations

#### `matrix_multiply(matrix_a: list[list[float]], matrix_b: list[list[float]])`
Multiply two matrices using matrix multiplication.

#### `matrix_determinant(matrix_data: list[list[float]])`
Calculate the determinant of a square matrix.

#### `matrix_inverse(matrix_data: list[list[float]])`
Calculate the inverse of a square matrix.

#### `matrix_eigenvalues(matrix_data: list[list[float]])`
Calculate eigenvalues and eigenvectors of a square matrix.

#### `solve_linear_system(coefficient_matrix: list[list[float]], constants: list[float])`
Solve a system of linear equations Ax = b.

#### `matrix_operations(operation: str, matrix_data: list[list[float]], norm_type: str = "frobenius")`
Perform various matrix operations.

**Supported Operations:**
- `transpose`, `trace`, `rank`, `norm`, `svd`, `qr`, `lu`
- `condition_number`, `pseudoinverse`, `is_symmetric`, `is_orthogonal`

#### `matrix_arithmetic(operation: str, matrix_a: list[list[float]], matrix_b: list[list[float]] = None, scalar: float = None)`
Perform matrix arithmetic operations (add, subtract, scalar_multiply).

#### `create_matrix(matrix_type: str, size: int = None, rows: int = None, cols: int = None)`
Create special matrices (identity, zero).

### Complex Number Operations

#### `complex_arithmetic(operation: str, z1, z2=None)`
Perform arithmetic operations on complex numbers.

**Supported Operations:** add, subtract, multiply, divide, power

**Complex Number Formats:**
- String: "3+4j", "5-2j", "7j", "3"
- Dictionary: {"real": 3, "imag": 4}
- Float/Int: 5 (treated as 5+0j)

#### `complex_magnitude(z)`
Calculate the magnitude (absolute value) of a complex number.

#### `complex_phase(z, unit: str = "radians")`
Calculate the phase (argument) of a complex number.

#### `complex_conjugate(z)`
Calculate the complex conjugate of a complex number.

#### `polar_conversion(operation: str, ...)`
Convert between rectangular and polar forms.

**Operations:**
- `to_polar`: Parameters: z, unit
- `to_rectangular`: Parameters: magnitude, phase, unit

#### `complex_functions(function: str, z, base=None)`
Calculate complex mathematical functions (exp, log, sqrt, sin, cos, tan).

### Unit Conversions

#### `convert_units(value: float, from_unit: str, to_unit: str, unit_type: str)`
Convert a value from one unit to another.

**Supported Unit Types:**
- `length`: m, km, cm, mm, in, ft, yd, mi, etc.
- `weight`: kg, g, lb, oz, ton, etc.
- `temperature`: celsius, fahrenheit, kelvin, rankine
- `volume`: m³, l, ml, gal, qt, pt, cup, etc.
- `time`: s, min, h, day, week, month, year
- `energy`: J, kJ, cal, kcal, btu, kwh, etc.
- `pressure`: Pa, bar, atm, psi, mmhg, etc.
- `power`: W, kW, hp, btu/h
- `frequency`: Hz, kHz, MHz, GHz, rpm
- `area`: m², km², cm², in², ft², acre, etc.
- `speed`: m/s, km/h, mph, knot, etc.

#### `get_available_units(unit_type: str = None)`
Get available units for a specific type or all unit types.

#### `validate_unit_compatibility(from_unit: str, to_unit: str, unit_type: str)`
Validate that two units are compatible for conversion.

### Calculus Operations

#### `derivative(expression: str, variable: str, order: int = 1)`
Calculate symbolic derivative of an expression.

#### `integral(expression: str, variable: str, lower_bound: float = None, upper_bound: float = None)`
Calculate symbolic integral (definite or indefinite).

#### `numerical_derivative(expression: str, variable: str, point: float, order: int = 1, dx: float = 1e-5)`
Calculate numerical derivative at a specific point.

#### `numerical_integral(expression: str, variable: str, lower_bound: float, upper_bound: float, method: str = "quad")`
Calculate numerical integral using scipy integration methods.

#### `calculate_limit(expression: str, variable: str, approach_value: str, direction: str = "both")`
Calculate limit of an expression.

#### `taylor_series(expression: str, variable: str, center: float = 0, order: int = 5)`
Calculate Taylor series expansion.

#### `find_critical_points(expression: str, variable: str)`
Find critical points of a single-variable function.

#### `gradient(expression: str, variables: list[str])`
Calculate gradient (vector of partial derivatives).

#### `evaluate_expression(expression: str, variable_values: dict)`
Evaluate a mathematical expression at specific variable values.

### Equation Solving

#### `solve_linear(equation: str, variable: str)`
Solve a linear equation for a single variable.

#### `solve_quadratic(equation: str, variable: str)`
Solve a quadratic equation with detailed analysis.

#### `solve_polynomial(equation: str, variable: str)`
Solve polynomial equations of any degree.

#### `solve_system(equations: list[str], variables: list[str])`
Solve a system of equations.

#### `find_roots(expression: str, variable: str, initial_guess: float = None, method: str = "auto")`
Find roots of arbitrary functions using numerical methods.

#### `analyze_equation(equation: str, variable: str)`
Analyze an equation to determine its type and properties.

### Financial Calculations

#### `compound_interest(principal: float, rate: float, time: float, compounding_frequency: int = 1)`
Calculate compound interest and future value.

#### `loan_payment(principal: float, rate: float, periods: int, payment_type: str = "end")`
Calculate loan payment amount (PMT).

#### `net_present_value(cash_flows: list[float], discount_rate: float, initial_investment: float = 0)`
Calculate Net Present Value (NPV) of cash flows.

#### `internal_rate_of_return(cash_flows: list[float], initial_investment: float)`
Calculate Internal Rate of Return (IRR).

#### `present_value(future_value: float, rate: float, periods: int)`
Calculate present value of a future amount.

#### `future_value_annuity(payment: float, rate: float, periods: int, payment_type: str = "end")`
Calculate future value of an annuity.

#### `amortization_schedule(principal: float, rate: float, periods: int, max_periods_display: int = 12)`
Generate loan amortization schedule.

### Currency Conversion (Optional)

**Note:** Currency conversion is disabled by default for privacy. Enable with `CALCULATOR_ENABLE_CURRENCY_CONVERSION=true`.

#### `convert_currency(amount: float, from_currency: str, to_currency: str)`
Convert currency with privacy controls and fallback mechanisms.

#### `get_exchange_rate(from_currency: str, to_currency: str)`
Get exchange rate between two currencies.

#### `get_supported_currencies()`
Get list of supported currencies.

#### `get_currency_info()`
Get information about currency conversion configuration.

### Mathematical Constants

#### `get_constant(name: str, precision: str = "standard")`
Get a mathematical or physical constant by name.

**Available Constants:**
- Mathematical: pi, e, phi, sqrt2, euler_gamma, catalan, etc.
- Physical: c, h, k, Na, R, G, etc.
- Astronomical: au, ly, pc, M_sun, R_earth, etc.

#### `list_constants(category: str = None)`
List available constants, optionally filtered by category.

#### `search_constants(query: str)`
Search constants by name, symbol, or description.

## Resources

### Constants Resource
Access mathematical constants as MCP resources:

```
constants://{category}/{name}
```

Examples:
- `constants://mathematical/pi`
- `constants://physical/c`
- `constants://astronomical/au`

### Formulas Resource
Access mathematical formulas as MCP resources:

```
formulas://{domain}/{formula}
```

Examples:
- `formulas://algebra/quadratic`
- `formulas://calculus/derivative_power`
- `formulas://physics/kinetic_energy`

## Error Handling

All tools return structured error responses with:
- Error type classification
- Clear, actionable error messages
- Input validation details
- Suggested corrections
- Context information for debugging

## Performance Considerations

- Basic operations: < 10ms response time
- Advanced functions: < 100ms response time
- Statistical operations: < 500ms response time
- Matrix operations: < 1 second response time
- Configurable computation timeouts and memory limits
- Caching for expensive operations

## Security Features

- Input sanitization and validation
- No code injection through eval()
- Resource limits (computation time, memory)
- Privacy controls for external API access
- Structured error responses without sensitive information