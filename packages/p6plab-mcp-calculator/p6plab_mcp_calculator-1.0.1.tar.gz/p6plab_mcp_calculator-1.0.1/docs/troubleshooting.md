# Scientific Calculator MCP Server - Troubleshooting Guide

## Common Issues and Solutions

### Tool Group Configuration Issues

#### Issue: Only seeing 8 basic tools instead of expected count

**Cause:** This is the default behavior. Only basic arithmetic tools are enabled by default for security and performance.

**Expected Tool Counts by Configuration:**
- **Default (no configuration)**: 8 tools (basic arithmetic only)
- **CALCULATOR_ENABLE_SCIENTIFIC=true**: 42+ tools
- **CALCULATOR_ENABLE_BUSINESS=true**: 22+ tools  
- **CALCULATOR_ENABLE_ENGINEERING=true**: 38+ tools
- **CALCULATOR_ENABLE_ALL=true**: 68 tools

**Solution:**
```json
{
  "mcpServers": {
    "scientific-calculator": {
      "command": "uvx",
      "args": ["p6plab-mcp-calculator@latest"],
      "env": {
        "CALCULATOR_ENABLE_SCIENTIFIC": "true"  // Enable scientific tools
        // or
        "CALCULATOR_ENABLE_ALL": "true"         // Enable all 68 tools
      }
    }
  }
}
```

#### Issue: Tool group environment variables not working

**Cause:** Incorrect variable names, values, or MCP client configuration.

**Solution:**
1. **Check variable names** (must be exact):
   ```bash
   CALCULATOR_ENABLE_BASIC=true
   CALCULATOR_ENABLE_ADVANCED=true
   CALCULATOR_ENABLE_STATISTICS=true
   # etc.
   ```

2. **Check boolean values** (case-insensitive):
   - **Valid true**: `true`, `TRUE`, `1`, `yes`, `on`, `enable`, `enabled`
   - **Valid false**: `false`, `FALSE`, `0`, `no`, `off`, `disable`, `disabled`, `""` (empty)

3. **Verify MCP configuration**:
   ```json
   {
     "env": {
       "CALCULATOR_ENABLE_SCIENTIFIC": "true"  // Must be in "env" section
     }
   }
   ```

#### Issue: Configuration warnings in logs

**Cause:** Invalid environment variable values or deprecated variables.

**Common warnings:**
- `Invalid value 'maybe' for CALCULATOR_ENABLE_ADVANCED, treating as false`
- `Legacy environment variable CALCULATOR_ENABLE_ALL_TOOLS is deprecated`

**Solution:**
1. **Fix invalid values**: Use only valid boolean values
2. **Update legacy variables**: Replace `CALCULATOR_ENABLE_ALL_TOOLS` with `CALCULATOR_ENABLE_ALL`
3. **Check health_check tool**: It reports configuration warnings and recommendations

#### Issue: Unexpected tool count with preset combinations

**Cause:** Multiple presets enabled simultaneously or individual overrides.

**Behavior:**
- Multiple presets combine (union of all enabled groups)
- Individual group settings take precedence over presets
- `CALCULATOR_ENABLE_ALL` overrides everything

**Example:**
```json
{
  "env": {
    "CALCULATOR_ENABLE_SCIENTIFIC": "true",  // 42+ tools
    "CALCULATOR_ENABLE_BUSINESS": "true"     // Additional tools
    // Result: Union of both presets
  }
}
```

### Installation Issues

#### Issue: `uvx p6plab-mcp-calculator` fails with "command not found"

**Cause:** uvx is not installed or not in PATH.

**Solution:**
```bash
# Install uv and uvx
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv

# Or using homebrew (macOS)
brew install uv

# Verify installation
uvx --version
```

#### Issue: Package installation fails with dependency conflicts

**Cause:** Conflicting package versions in environment.

**Solution:**
```bash
# Use uvx for isolated execution (recommended)
uvx p6plab-mcp-calculator@latest

# Or create clean virtual environment
python -m venv clean_env
source clean_env/bin/activate  # On Windows: clean_env\Scripts\activate
pip install p6plab-mcp-calculator
```

#### Issue: Import errors when running the server

**Cause:** Missing dependencies or incorrect Python version.

**Solution:**
```bash
# Check Python version (requires 3.8+)
python --version

# Install with all dependencies
pip install p6plab-mcp-calculator[all]

# Or install specific dependencies
pip install numpy scipy sympy fastmcp pydantic loguru
```

### Server Configuration Issues

#### Issue: Server fails to start with configuration errors

**Cause:** Invalid environment variable values.

**Solution:**
```bash
# Check current configuration
export CALCULATOR_LOG_LEVEL=DEBUG
uvx p6plab-mcp-calculator@latest

# Reset to defaults
unset CALCULATOR_PRECISION
unset CALCULATOR_LOG_LEVEL
unset CALCULATOR_CACHE_SIZE
```

#### Issue: Currency conversion not working

**Cause:** Currency conversion is disabled by default for privacy.

**Solution:**
```bash
# Enable currency conversion (optional)
export CALCULATOR_ENABLE_CURRENCY_CONVERSION=true

# Optionally provide API key for real-time rates
export CALCULATOR_CURRENCY_API_KEY=your_api_key_here

# Without API key, fallback rates are used
```

#### Issue: Precision errors in calculations

**Cause:** Default precision may be insufficient for specific use cases.

**Solution:**
```bash
# Increase precision (default: 15)
export CALCULATOR_PRECISION=25

# Or configure in MCP client
{
  "env": {
    "CALCULATOR_PRECISION": "25"
  }
}
```

### MCP Client Integration Issues

#### Issue: MCP client cannot connect to calculator server

**Cause:** Incorrect server configuration or path issues.

**Solution:**
```json
{
  "mcpServers": {
    "calculator": {
      "command": "uvx",
      "args": ["p6plab-mcp-calculator@latest"],
      "env": {
        "CALCULATOR_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

#### Issue: Tools not appearing in MCP client

**Cause:** Server startup failure or tool registration issues.

**Solution:**
1. Check server logs for errors
2. Verify server starts independently:
   ```bash
   uvx p6plab-mcp-calculator@latest
   ```
3. Test with minimal configuration:
   ```json
   {
     "mcpServers": {
       "calculator": {
         "command": "uvx",
         "args": ["p6plab-mcp-calculator@latest"]
       }
     }
   }
   ```

#### Issue: Server timeout or performance issues

**Cause:** Complex calculations exceeding time limits.

**Solution:**
```bash
# Increase timeout limits
export CALCULATOR_MAX_COMPUTATION_TIME=60
export CALCULATOR_MAX_MEMORY_MB=1024

# Or reduce calculation complexity
# Use numerical methods instead of symbolic for complex expressions
```

### Mathematical Operation Issues

#### Issue: "Division by zero" errors

**Cause:** Attempting to divide by zero or very small numbers.

**Solution:**
```python
# Check for zero before division
if denominator != 0:
    result = divide(numerator, denominator)

# Use epsilon for near-zero checks
epsilon = 1e-10
if abs(denominator) > epsilon:
    result = divide(numerator, denominator)
```

#### Issue: Domain errors in mathematical functions

**Cause:** Invalid input values for function domains.

**Solution:**
```python
# Check domain before calling functions
# For logarithms: value must be positive
if value > 0:
    result = logarithm(value, "e")

# For inverse trig: value must be in [-1, 1]
if -1 <= value <= 1:
    result = trigonometric("arcsin", value)

# For square root: value must be non-negative
if value >= 0:
    result = square_root(value)
```

#### Issue: Matrix operation failures

**Cause:** Incompatible matrix dimensions or singular matrices.

**Solution:**
```python
# Check matrix dimensions before operations
def safe_matrix_multiply(a, b):
    if len(a[0]) == len(b):  # columns of a == rows of b
        return matrix_multiply(a, b)
    else:
        return {"error": "Incompatible dimensions"}

# Check for singular matrices before inversion
det_result = matrix_determinant(matrix)
if abs(det_result["result"]) > 1e-10:
    inverse = matrix_inverse(matrix)
else:
    # Use pseudoinverse for singular matrices
    inverse = matrix_operations("pseudoinverse", matrix)
```

#### Issue: Complex number format errors

**Cause:** Invalid complex number input formats.

**Solution:**
```python
# Valid complex number formats:
complex_arithmetic("add", "3+4j", "1+2j")           # String format
complex_arithmetic("add", {"real": 3, "imag": 4}, {"real": 1, "imag": 2})  # Dict format
complex_arithmetic("add", 3, 4)                     # Real numbers

# Invalid formats to avoid:
# complex_arithmetic("add", "3+4i", "1+2i")        # Use 'j' not 'i'
# complex_arithmetic("add", [3, 4], [1, 2])        # Use dict not list
```

### Unit Conversion Issues

#### Issue: "Unknown unit" errors

**Cause:** Typos in unit names or unsupported units.

**Solution:**
```python
# Get available units first
available = get_available_units("length")
print(available["units"])

# Use exact unit names from the list
convert_units(100, "cm", "m", "length")  # Correct
# convert_units(100, "centimeter", "meter", "length")  # May fail

# Search for units if unsure
search_result = get_available_units()
```

#### Issue: Temperature conversion giving unexpected results

**Cause:** Temperature conversions use different formulas than linear conversions.

**Solution:**
```python
# Temperature conversions are handled specially
convert_units(0, "celsius", "fahrenheit", "temperature")    # Returns 32.0
convert_units(100, "celsius", "kelvin", "temperature")      # Returns 373.15

# Verify conversion with known values
# 0°C = 32°F = 273.15K
# 100°C = 212°F = 373.15K
```

### Statistical Analysis Issues

#### Issue: "Insufficient data" errors in statistical functions

**Cause:** Not enough data points for the requested analysis.

**Solution:**
```python
# Check data size before analysis
data = [1, 2, 3]

if len(data) >= 2:
    std_dev = standard_deviation(data, sample=True)
else:
    print("Need at least 2 data points for sample standard deviation")

if len(data) >= 4:
    quartiles_result = quartiles(data)
else:
    print("Need at least 4 data points for quartile calculation")
```

#### Issue: Correlation analysis fails with mismatched data

**Cause:** X and Y datasets have different lengths.

**Solution:**
```python
# Ensure data arrays have same length
x_data = [1, 2, 3, 4, 5]
y_data = [2, 4, 6, 8]  # Missing one value

# Fix by ensuring equal lengths
if len(x_data) == len(y_data):
    correlation = correlation_analysis(x_data, y_data)
else:
    min_length = min(len(x_data), len(y_data))
    correlation = correlation_analysis(x_data[:min_length], y_data[:min_length])
```

### Calculus and Equation Solving Issues

#### Issue: Symbolic operations fail with complex expressions

**Cause:** SymPy cannot parse or solve the expression.

**Solution:**
```python
# Simplify expressions before processing
# Instead of: "sin(x)^2 + cos(x)^2"
# Use: "sin(x)**2 + cos(x)**2"

# Use numerical methods for complex expressions
numerical_derivative("complex_expression", "x", point=1.0)
# Instead of symbolic_derivative for unsolvable expressions

# Break complex expressions into simpler parts
# Solve step by step rather than all at once
```

#### Issue: Equation solving returns no solutions

**Cause:** Equation has no real solutions or is incorrectly formatted.

**Solution:**
```python
# Check equation format
solve_quadratic("x^2 + 1 = 0", "x")  # Has complex solutions
solve_quadratic("x^2 - 4 = 0", "x")  # Has real solutions: x = ±2

# Use equation analysis first
analysis = analyze_equation("x^2 + 1 = 0", "x")
print(analysis["equation_type"])  # Shows if equation is solvable

# For no real solutions, check if complex solutions exist
# Or use numerical root finding with different initial guesses
```

### Performance Issues

#### Issue: Slow response times for large calculations

**Cause:** Complex operations or large datasets.

**Solution:**
```bash
# Increase resource limits
export CALCULATOR_MAX_COMPUTATION_TIME=120
export CALCULATOR_MAX_MEMORY_MB=2048

# Enable caching for repeated operations
export CALCULATOR_CACHE_SIZE=5000
```

```python
# Optimize operations:
# 1. Use numerical methods for large datasets
numerical_integral("f(x)", "x", 0, 100, method="quad")

# 2. Break large matrices into smaller blocks
# 3. Use appropriate precision (don't use excessive precision)
# 4. Cache expensive constant calculations
```

#### Issue: Memory errors with large matrices

**Cause:** Matrix operations on very large matrices exceed memory limits.

**Solution:**
```python
# Check matrix size before operations
def safe_matrix_operation(matrix):
    rows, cols = len(matrix), len(matrix[0])
    if rows * cols > 1000000:  # 1M elements
        return {"error": "Matrix too large"}
    return matrix_determinant(matrix)

# Use sparse matrix representations for large sparse matrices
# Consider iterative methods for large linear systems
```

### Debugging Tips

#### Enable Debug Logging

```bash
export CALCULATOR_LOG_LEVEL=DEBUG
uvx p6plab-mcp-calculator@latest
```

#### Test Individual Components

```python
# Test basic operations first
add(1, 2)
multiply(3, 4)

# Then test advanced features
trigonometric("sin", 0)
matrix_determinant([[1, 2], [3, 4]])
```

#### Validate Input Data

```python
# Always validate inputs before complex operations
def validate_matrix(matrix):
    if not matrix or not matrix[0]:
        return False
    row_length = len(matrix[0])
    return all(len(row) == row_length for row in matrix)

if validate_matrix(my_matrix):
    result = matrix_determinant(my_matrix)
```

#### Check Environment Configuration

```bash
# Print current configuration
python -c "
import os
print('Precision:', os.getenv('CALCULATOR_PRECISION', '15'))
print('Log Level:', os.getenv('CALCULATOR_LOG_LEVEL', 'INFO'))
print('Currency Enabled:', os.getenv('CALCULATOR_ENABLE_CURRENCY_CONVERSION', 'false'))
"
```

## Getting Help

### Log Analysis

When reporting issues, include:
1. Full error messages
2. Input data that caused the error
3. Environment configuration
4. Server logs with DEBUG level enabled

### Common Error Patterns

| Error Type | Common Cause | Quick Fix |
|------------|--------------|-----------|
| `ValidationError` | Invalid input format | Check input types and ranges |
| `CalculationError` | Mathematical domain error | Validate inputs before calculation |
| `MatrixError` | Dimension mismatch | Check matrix dimensions |
| `PrecisionError` | Precision overflow | Reduce precision or use different method |
| `SolverError` | Unsolvable equation | Try numerical methods or simplify |
| `StatisticsError` | Insufficient data | Check data size requirements |

### Performance Optimization

1. **Use appropriate precision**: Don't use 50-digit precision for simple calculations
2. **Cache expensive operations**: Store results of repeated calculations
3. **Choose right method**: Numerical vs symbolic based on requirements
4. **Validate early**: Check inputs before expensive operations
5. **Monitor resources**: Set appropriate timeout and memory limits

### Best Practices

1. **Always validate inputs** before calling mathematical functions
2. **Handle edge cases** like division by zero, negative square roots
3. **Use appropriate data types** for your precision requirements
4. **Test with known values** to verify calculations
5. **Monitor performance** for large-scale operations
6. **Enable logging** during development and debugging

This troubleshooting guide should help resolve most common issues with the Scientific Calculator MCP Server. For additional support, check the API documentation and examples.