# Scientific Calculator MCP Server - Usage Examples

## Getting Started

### Installation and Setup

```bash
# Install from PyPI
pip install p6plab-mcp-calculator

# Or run with uvx (recommended)
uvx p6plab-mcp-calculator@latest
```

### MCP Client Configuration

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "calculator": {
      "command": "uvx",
      "args": ["p6plab-mcp-calculator@latest"],
      "env": {
        "CALCULATOR_PRECISION": "15",
        "CALCULATOR_LOG_LEVEL": "INFO",
        "CALCULATOR_ENABLE_CURRENCY_CONVERSION": "false"
      }
    }
  }
}
```

## Basic Arithmetic Examples

### Simple Calculations

```python
# Addition
add(15.5, 24.3)
# Result: 39.8

# Division with high precision
divide(22, 7)
# Result: 3.142857142857143

# Power operations
power(2, 10)
# Result: 1024.0

# Square root
square_root(144)
# Result: 12.0
```

### Expression Evaluation

```python
# Evaluate mathematical expressions
calculate("2*pi + sqrt(16)")
# Result: ~10.283 (2π + 4)

calculate("sin(pi/2) + cos(0)")
# Result: 2.0
```

## Advanced Mathematical Functions

### Trigonometric Functions

```python
# Basic trigonometric functions
trigonometric("sin", 1.5708, "radians")  # sin(π/2)
# Result: 1.0

trigonometric("cos", 90, "degrees")
# Result: 0.0

trigonometric("tan", 45, "degrees")
# Result: 1.0

# Inverse trigonometric functions
trigonometric("arcsin", 0.5, "degrees")
# Result: 30.0 degrees
```

### Logarithmic and Exponential Functions

```python
# Natural logarithm
logarithm(2.718281828, "e")
# Result: ~1.0

# Base-10 logarithm
logarithm(1000, "10")
# Result: 3.0

# Custom base logarithm
logarithm(8, "2")
# Result: 3.0

# Exponential functions
exponential("e", 2)
# Result: ~7.389 (e²)

exponential("2", 10)
# Result: 1024.0
```

### Hyperbolic Functions

```python
# Hyperbolic sine
hyperbolic("sinh", 1)
# Result: ~1.175

# Hyperbolic cosine
hyperbolic("cosh", 0)
# Result: 1.0
```

## Statistical Analysis Examples

### Descriptive Statistics

```python
# Sample data
data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Comprehensive descriptive statistics
descriptive_stats(data, sample=True)
# Result: {
#   "count": 10,
#   "mean": 5.5,
#   "median": 5.5,
#   "std_dev": 3.03,
#   "variance": 9.17,
#   "min": 1,
#   "max": 10,
#   "Q1": 3.25,
#   "Q3": 7.75
# }
```

### Probability Distributions

```python
# Normal distribution
probability_distribution("normal", x=0, mean=0, std_dev=1)
# Result: Standard normal at x=0, PDF≈0.399, CDF=0.5

# Binomial distribution
probability_distribution("binomial", k=7, n=10, p=0.7)
# Result: P(X=7) for Binomial(10, 0.7)

# Poisson distribution
probability_distribution("poisson", k=3, lambda_param=2.5)
# Result: P(X=3) for Poisson(2.5)
```

### Correlation and Regression

```python
# Correlation analysis
x_data = [1, 2, 3, 4, 5]
y_data = [2, 4, 6, 8, 10]  # Perfect positive correlation

correlation_analysis(x_data, y_data)
# Result: correlation = 1.0, p_value ≈ 0

# Linear regression
regression_analysis(x_data, y_data)
# Result: slope = 2.0, intercept = 0.0, r_squared = 1.0
```

### Hypothesis Testing

```python
# One-sample t-test
sample_data = [23, 25, 28, 30, 32, 35, 38, 40]
hypothesis_test("t_test_one_sample", data=sample_data, population_mean=30)

# Two-sample t-test
group1 = [20, 22, 24, 26, 28]
group2 = [25, 27, 29, 31, 33]
hypothesis_test("t_test_two_sample", data1=group1, data2=group2)

# Chi-square test
observed = [10, 15, 20, 25]
expected = [12, 18, 18, 22]
hypothesis_test("chi_square", observed=observed, expected=expected)
```

## Matrix Operations Examples

### Basic Matrix Arithmetic

```python
# Matrix multiplication
matrix_a = [[1, 2], [3, 4]]
matrix_b = [[5, 6], [7, 8]]

matrix_multiply(matrix_a, matrix_b)
# Result: [[19, 22], [43, 50]]

# Matrix addition
matrix_arithmetic("add", matrix_a, matrix_b)
# Result: [[6, 8], [10, 12]]

# Scalar multiplication
matrix_arithmetic("scalar_multiply", matrix_a, scalar=3)
# Result: [[3, 6], [9, 12]]
```

### Advanced Matrix Operations

```python
# Matrix determinant
matrix_determinant([[1, 2], [3, 4]])
# Result: -2.0

# Matrix inverse
matrix_inverse([[1, 2], [3, 4]])
# Result: [[-2.0, 1.0], [1.5, -0.5]]

# Eigenvalues and eigenvectors
matrix_eigenvalues([[2, 1], [1, 2]])
# Result: eigenvalues = [3.0, 1.0], eigenvectors included

# Matrix decompositions
matrix_operations("svd", [[1, 2], [3, 4], [5, 6]])
# Result: U, singular_values, Vt matrices
```

### Linear System Solving

```python
# Solve system: x + y = 3, 2x - y = 0
coefficient_matrix = [[1, 1], [2, -1]]
constants = [3, 0]

solve_linear_system(coefficient_matrix, constants)
# Result: solution = [1.0, 2.0] (x=1, y=2)
```

## Complex Number Examples

### Complex Arithmetic

```python
# Complex number addition
complex_arithmetic("add", "3+4j", "1+2j")
# Result: {"real": 4.0, "imag": 6.0}

# Complex multiplication
complex_arithmetic("multiply", {"real": 2, "imag": 3}, {"real": 1, "imag": 4})
# Result: {"real": -10.0, "imag": 11.0}

# Complex magnitude
complex_magnitude("3+4j")
# Result: 5.0

# Complex phase
complex_phase("1+1j", "degrees")
# Result: 45.0 degrees
```

### Polar Conversions

```python
# Rectangular to polar
polar_conversion("to_polar", z="3+4j", unit="degrees")
# Result: {"magnitude": 5.0, "phase": 53.13}

# Polar to rectangular
polar_conversion("to_rectangular", magnitude=5, phase=53.13, unit="degrees")
# Result: {"real": 3.0, "imag": 4.0}
```

### Complex Functions

```python
# Complex exponential
complex_functions("exp", "1+1j")
# Result: e^(1+i) in complex form

# Complex logarithm
complex_functions("log", "1+1j")
# Result: ln(1+i) in complex form
```

## Unit Conversion Examples

### Length Conversions

```python
# Metric conversions
convert_units(1000, "m", "km", "length")
# Result: 1.0 km

convert_units(100, "cm", "m", "length")
# Result: 1.0 m

# Imperial conversions
convert_units(12, "in", "ft", "length")
# Result: 1.0 ft

convert_units(1, "mi", "ft", "length")
# Result: 5280.0 ft
```

### Temperature Conversions

```python
# Celsius to Fahrenheit
convert_units(0, "celsius", "fahrenheit", "temperature")
# Result: 32.0°F

# Fahrenheit to Celsius
convert_units(212, "fahrenheit", "celsius", "temperature")
# Result: 100.0°C

# Celsius to Kelvin
convert_units(25, "celsius", "kelvin", "temperature")
# Result: 298.15 K
```

### Weight and Volume Conversions

```python
# Weight conversions
convert_units(1, "kg", "lb", "weight")
# Result: ~2.205 lb

convert_units(16, "oz", "lb", "weight")
# Result: 1.0 lb

# Volume conversions
convert_units(1, "gal", "l", "volume")
# Result: ~3.785 L

convert_units(1000, "ml", "l", "volume")
# Result: 1.0 L
```

## Calculus Examples

### Derivatives

```python
# Symbolic derivative
derivative("x^3 + 2*x^2 + x + 1", "x")
# Result: "3*x^2 + 4*x + 1"

# Higher-order derivatives
derivative("sin(x)", "x", order=2)
# Result: "-sin(x)"

# Numerical derivative at a point
numerical_derivative("x^2", "x", point=3)
# Result: 6.0 (derivative of x² at x=3)
```

### Integrals

```python
# Indefinite integral
integral("2*x + 3", "x")
# Result: "x^2 + 3*x"

# Definite integral
integral("x^2", "x", lower_bound=0, upper_bound=2)
# Result: 8/3 ≈ 2.667

# Numerical integration
numerical_integral("sin(x)", "x", 0, 3.14159, method="quad")
# Result: ~2.0 (integral of sin(x) from 0 to π)
```

### Limits and Series

```python
# Limit calculation
calculate_limit("sin(x)/x", "x", "0")
# Result: 1.0

# Taylor series expansion
taylor_series("exp(x)", "x", center=0, order=5)
# Result: "1 + x + x^2/2 + x^3/6 + x^4/24 + x^5/120"

# Critical points
find_critical_points("x^3 - 3*x^2 + 2", "x")
# Result: Critical points with classifications (max/min)
```

## Equation Solving Examples

### Linear and Quadratic Equations

```python
# Linear equation
solve_linear("2*x + 3 = 7", "x")
# Result: x = 2.0

# Quadratic equation
solve_quadratic("x^2 - 5*x + 6 = 0", "x")
# Result: x = 2.0, x = 3.0 with analysis (discriminant, vertex, etc.)

# Polynomial equation
solve_polynomial("x^3 - 6*x^2 + 11*x - 6 = 0", "x")
# Result: x = 1.0, x = 2.0, x = 3.0
```

### Systems of Equations

```python
# System of linear equations
equations = ["x + y = 5", "2*x - y = 1"]
variables = ["x", "y"]

solve_system(equations, variables)
# Result: x = 2.0, y = 3.0
```

### Root Finding

```python
# Find roots of arbitrary functions
find_roots("x^3 - 2*x - 5", "x", initial_guess=2)
# Result: Numerical root ≈ 2.094

# Multiple methods
find_roots("cos(x) - x", "x", method="newton", initial_guess=0.5)
# Result: Root ≈ 0.739 (where cos(x) = x)
```

## Financial Calculations Examples

### Interest and Investment

```python
# Compound interest
compound_interest(principal=1000, rate=0.05, time=10, compounding_frequency=12)
# Result: Future value ≈ $1,643.62

# Simple interest
simple_interest(1000, 0.05, 5)
# Result: Future value = $1,250.00

# Present value
present_value(future_value=1000, rate=0.05, periods=10)
# Result: Present value ≈ $613.91
```

### Loan Calculations

```python
# Monthly mortgage payment
loan_payment(principal=300000, rate=0.04/12, periods=360)  # 30-year mortgage
# Result: Monthly payment ≈ $1,432.25

# Amortization schedule
amortization_schedule(100000, 0.05/12, 360, max_periods_display=12)
# Result: First 12 months of payment breakdown
```

### Investment Analysis

```python
# Net Present Value
cash_flows = [1000, 1500, 2000, 2500, 3000]
net_present_value(cash_flows, discount_rate=0.1, initial_investment=5000)
# Result: NPV calculation with profitability analysis

# Internal Rate of Return
internal_rate_of_return(cash_flows, initial_investment=5000)
# Result: IRR percentage and convergence information
```

## Mathematical Constants Examples

### Accessing Constants

```python
# Mathematical constants
get_constant("pi", precision="high")
# Result: π with high precision (50+ digits)

get_constant("e")
# Result: Euler's number with standard precision

get_constant("phi")
# Result: Golden ratio

# Physical constants
get_constant("c")
# Result: Speed of light (299,792,458 m/s)

get_constant("h")
# Result: Planck constant

get_constant("k")
# Result: Boltzmann constant
```

### Searching and Listing

```python
# Search constants
search_constants("light")
# Result: Constants related to light (speed of light, etc.)

# List by category
list_constants("physical")
# Result: All physical constants

list_constants("mathematical")
# Result: All mathematical constants
```

## Advanced Usage Patterns

### Chaining Operations

```python
# Calculate compound interest with multiple scenarios
scenarios = [
    {"rate": 0.03, "time": 10},
    {"rate": 0.05, "time": 10},
    {"rate": 0.07, "time": 10}
]

for scenario in scenarios:
    result = compound_interest(10000, scenario["rate"], scenario["time"])
    print(f"Rate: {scenario['rate']*100}%, Future Value: ${result['future_value']:.2f}")
```

### Statistical Analysis Pipeline

```python
# Complete statistical analysis
data = [23, 25, 28, 30, 32, 35, 38, 40, 42, 45]

# 1. Descriptive statistics
desc_stats = descriptive_stats(data)

# 2. Test normality assumption
normal_test = probability_distribution("normal", x=desc_stats["mean"], 
                                     mean=desc_stats["mean"], 
                                     std_dev=desc_stats["std_dev"])

# 3. Hypothesis test
t_test = hypothesis_test("t_test_one_sample", data=data, population_mean=35)
```

### Engineering Calculations

```python
# Structural engineering example
# Calculate beam deflection using calculus

# Define load function
load_expression = "w*x*(L-x)/2"  # Distributed load

# Calculate moment (integral of load)
moment = integral(load_expression, "x")

# Calculate deflection (double integral)
deflection = integral(moment, "x")

# Evaluate at specific point
deflection_at_center = evaluate_expression(deflection, {"x": "L/2", "w": 1000, "L": 10})
```

## Error Handling Examples

### Common Error Scenarios

```python
# Division by zero
try:
    divide(10, 0)
except:
    # Returns structured error response
    # {"error": true, "error_type": "CalculationError", "message": "Division by zero"}

# Invalid domain for logarithm
try:
    logarithm(-5, "e")
except:
    # Returns domain error with suggestions

# Incompatible matrix dimensions
try:
    matrix_multiply([[1, 2]], [[1], [2], [3]])
except:
    # Returns matrix dimension error with details
```

### Input Validation

```python
# Invalid unit type
try:
    convert_units(100, "invalid_unit", "m", "length")
except:
    # Returns validation error with available units list

# Invalid equation format
try:
    solve_quadratic("not an equation", "x")
except:
    # Returns parsing error with format suggestions
```

This comprehensive examples document demonstrates the full capabilities of the Scientific Calculator MCP Server across all mathematical domains!