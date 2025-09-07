# Deployment Guide

## Overview

The Scientific Calculator MCP Server provides **68 mathematical tools** and can be deployed in multiple ways. This guide covers all deployment options and troubleshooting.

## Deployment Methods

### 1. uvx (Recommended for MCP Clients)

**For Production:**
```json
{
  "mcpServers": {
    "scientific-calculator": {
      "command": "uvx",
      "args": ["p6plab-mcp-calculator@latest"],
      "env": {
        "CALCULATOR_LOG_LEVEL": "INFO"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

**For Development (Local Wheel):**
```json
{
  "mcpServers": {
    "scientific-calculator": {
      "command": "uvx",
      "args": [
        "--from",
        "/absolute/path/to/dist/mcp_calculator-0.1.2-py3-none-any.whl",
        "p6plab-mcp-calculator"
      ],
      "env": {
        "CALCULATOR_LOG_LEVEL": "DEBUG"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### 2. Direct Python Execution

**For Development:**
```json
{
  "mcpServers": {
    "scientific-calculator": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "calculator.server"],
      "cwd": "/path/to/calculator/project",
      "env": {
        "CALCULATOR_LOG_LEVEL": "DEBUG"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### 3. pip Installation

```bash
# Install from PyPI
pip install p6plab-mcp-calculator

# Run directly
p6plab-mcp-calculator

# Or use in MCP client
{
  "command": "p6plab-mcp-calculator"
}
```

## Tool Group Configuration

The Scientific Calculator MCP Server supports **selective tool enabling** through environment variables. This allows you to control which mathematical capabilities are available based on your needs.

### Default Configuration
By default, only **basic arithmetic tools** (8 tools) are enabled:
```json
{
  "mcpServers": {
    "scientific-calculator": {
      "command": "uvx",
      "args": ["p6plab-mcp-calculator@latest"]
      // No tool group environment variables = basic tools only
    }
  }
}
```

### Preset Configurations

#### Scientific Computing (42+ tools)
```json
{
  "mcpServers": {
    "scientific-calculator": {
      "command": "uvx",
      "args": ["p6plab-mcp-calculator@latest"],
      "env": {
        "CALCULATOR_ENABLE_SCIENTIFIC": "true"
      }
    }
  }
}
```

#### Business Analysis (22+ tools)
```json
{
  "mcpServers": {
    "scientific-calculator": {
      "command": "uvx",
      "args": ["p6plab-mcp-calculator@latest"],
      "env": {
        "CALCULATOR_ENABLE_BUSINESS": "true"
      }
    }
  }
}
```

#### Engineering Work (38+ tools)
```json
{
  "mcpServers": {
    "scientific-calculator": {
      "command": "uvx",
      "args": ["p6plab-mcp-calculator@latest"],
      "env": {
        "CALCULATOR_ENABLE_ENGINEERING": "true"
      }
    }
  }
}
```

#### All Tools (68 tools)
```json
{
  "mcpServers": {
    "scientific-calculator": {
      "command": "uvx",
      "args": ["p6plab-mcp-calculator@latest"],
      "env": {
        "CALCULATOR_ENABLE_ALL": "true"
      }
    }
  }
}
```

### Custom Configuration
Enable specific tool groups as needed:
```json
{
  "mcpServers": {
    "scientific-calculator": {
      "command": "uvx",
      "args": ["p6plab-mcp-calculator@latest"],
      "env": {
        "CALCULATOR_ENABLE_ADVANCED": "true",
        "CALCULATOR_ENABLE_MATRIX": "true",
        "CALCULATOR_ENABLE_CALCULUS": "true"
      }
    }
  }
}
```

### Environment Variables Reference

#### Core Configuration
| Variable | Default | Description |
|----------|---------|-------------|
| `CALCULATOR_LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `CALCULATOR_PRECISION` | `15` | Decimal precision for calculations |
| `CALCULATOR_TIMEOUT` | `30` | Computation timeout in seconds |

#### Tool Group Controls
| Variable | Default | Tools | Description |
|----------|---------|-------|-------------|
| ~~`CALCULATOR_ENABLE_BASIC`~~ | Always enabled | 8 | Basic arithmetic operations (always available) |
| `CALCULATOR_ENABLE_ADVANCED` | `false` | 5 | Advanced mathematical functions |
| `CALCULATOR_ENABLE_STATISTICS` | `false` | 5 | Statistical analysis tools |
| `CALCULATOR_ENABLE_MATRIX` | `false` | 8 | Matrix operations and linear algebra |
| `CALCULATOR_ENABLE_COMPLEX` | `false` | 6 | Complex number operations |
| `CALCULATOR_ENABLE_UNITS` | `false` | 7 | Unit conversion tools |
| `CALCULATOR_ENABLE_CALCULUS` | `false` | 9 | Calculus operations |
| `CALCULATOR_ENABLE_SOLVER` | `false` | 6 | Equation solving tools |
| `CALCULATOR_ENABLE_FINANCIAL` | `false` | 7 | Financial mathematics |
| `CALCULATOR_ENABLE_CURRENCY` | `false` | 4 | Currency conversion |
| `CALCULATOR_ENABLE_CONSTANTS` | `false` | 3 | Mathematical and physical constants |

#### Preset Combinations
| Variable | Description | Includes | Total Tools |
|----------|-------------|----------|-------------|
| `CALCULATOR_ENABLE_ALL` | All mathematical tools | All 11 groups | 68 tools |
| `CALCULATOR_ENABLE_SCIENTIFIC` | Scientific computing | basic, advanced, statistics, matrix, complex, calculus | 42+ tools |
| `CALCULATOR_ENABLE_BUSINESS` | Business analysis | basic, financial, currency, units | 22+ tools |
| `CALCULATOR_ENABLE_ENGINEERING` | Engineering work | basic, advanced, matrix, complex, calculus, units, constants | 38+ tools |

## Verification

### Tool Count Verification

The number of available tools depends on your configuration:

1. **Basic Arithmetic** (8): health_check, add, subtract, multiply, divide, power, square_root, calculate
2. **Advanced Mathematics** (5): trigonometric, logarithm, exponential, hyperbolic, convert_angle
3. **Statistics** (5): descriptive_stats, probability_distribution, correlation_analysis, regression_analysis, hypothesis_test
4. **Matrix Operations** (8): matrix_multiply, matrix_determinant, matrix_inverse, matrix_eigenvalues, solve_linear_system, matrix_operations, matrix_arithmetic, create_matrix
5. **Complex Numbers** (6): complex_arithmetic, complex_magnitude, complex_phase, complex_conjugate, polar_conversion, complex_functions
6. **Unit Conversion** (7): convert_units, get_available_units, validate_unit_compatibility, get_conversion_factor, convert_multiple_units, find_unit_by_name, get_unit_info
7. **Calculus** (9): derivative, integral, numerical_derivative, numerical_integral, calculate_limit, taylor_series, find_critical_points, gradient, evaluate_expression
8. **Equation Solving** (6): solve_linear, solve_quadratic, solve_polynomial, solve_system, find_roots, analyze_equation
9. **Financial Mathematics** (7): compound_interest, loan_payment, net_present_value, internal_rate_of_return, present_value, future_value_annuity, amortization_schedule
10. **Currency Conversion** (4): convert_currency, get_exchange_rate, get_supported_currencies, get_currency_info
11. **Constants & References** (3): get_constant, list_constants, search_constants

### Quick Test

Test the server with a simple calculation:
```bash
# Test basic functionality
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "add", "arguments": {"a": 5, "b": 3}}}' | p6plab-mcp-calculator
```

## Troubleshooting

### Common Issues

#### Only 8 Tools Visible

**Problem:** MCP client shows only basic arithmetic tools instead of all 68 tools.

**Causes & Solutions:**

1. **Python Version Compatibility**
   - **Issue**: uvx uses Python 3.10 which has stricter type checking
   - **Solution**: Use version 0.1.2+ which fixes type annotation issues

2. **Relative Path Issues**
   - **Issue**: `./dist/package.whl` path not resolving correctly
   - **Solution**: Use absolute paths in MCP configuration

3. **Import Failures**
   - **Issue**: Some modules fail to import, causing server to register only basic tools
   - **Solution**: Check logs with `CALCULATOR_LOG_LEVEL=DEBUG`

4. **Cached Packages**
   - **Issue**: uvx using cached version of package
   - **Solution**: Update version number or clear uvx cache

#### Server Won't Start

**Problem:** `spawn python ENOENT` or similar errors.

**Solutions:**
1. Use full path to Python executable
2. Ensure virtual environment is activated
3. Check that all dependencies are installed

#### Missing Dependencies

**Problem:** Import errors for numpy, scipy, sympy, etc.

**Solutions:**
1. Install with all dependencies: `pip install p6plab-mcp-calculator[all]`
2. Use virtual environment with proper dependency isolation
3. Check Python version compatibility (requires Python 3.8+)

### Debug Configuration

For troubleshooting, use this enhanced configuration:

```json
{
  "mcpServers": {
    "scientific-calculator-debug": {
      "command": "uvx",
      "args": [
        "--from",
        "/absolute/path/to/mcp_calculator-0.1.2-py3-none-any.whl",
        "p6plab-mcp-calculator"
      ],
      "env": {
        "CALCULATOR_LOG_LEVEL": "DEBUG",
        "FASTMCP_LOG_LEVEL": "DEBUG",
        "CALCULATOR_PRECISION": "15"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### Performance Tuning

For production environments:

```json
{
  "env": {
    "CALCULATOR_LOG_LEVEL": "WARNING",
    "CALCULATOR_PRECISION": "15",
    "CALCULATOR_CACHE_SIZE": "2000",
    "CALCULATOR_MAX_COMPUTATION_TIME": "60",
    "CALCULATOR_MAX_MEMORY_MB": "1024"
  }
}
```

## Version History

### v0.1.2 (Current)
- ✅ **Fixed uvx compatibility**: Resolved Python 3.10 type annotation issues
- ✅ **All 68 tools working**: Complete tool set available via uvx
- ✅ **Production ready**: Ready for PyPI distribution

### v0.1.0
- ❌ **uvx compatibility issue**: Only 8/68 tools visible due to type annotation bug
- ✅ **Direct Python execution**: All 68 tools working when run directly

## Support

If you encounter issues:

1. **Check tool count**: Should see exactly 68 tools
2. **Enable debug logging**: Set `CALCULATOR_LOG_LEVEL=DEBUG`
3. **Verify Python version**: Requires Python 3.8+ (uvx uses 3.10)
4. **Use absolute paths**: Avoid relative paths in MCP configuration
5. **Test direct execution**: Try running `p6plab-mcp-calculator` directly first

For additional support, see [troubleshooting.md](troubleshooting.md).