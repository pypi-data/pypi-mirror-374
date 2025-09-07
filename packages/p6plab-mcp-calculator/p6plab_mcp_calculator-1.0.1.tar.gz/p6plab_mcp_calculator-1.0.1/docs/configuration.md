# Configuration Guide

## Overview

The Scientific Calculator MCP Server provides **selective tool enabling** through environment variables, allowing you to control which mathematical capabilities are available. This guide covers all configuration options, use cases, and migration from legacy setups.

## Quick Start

### Default Configuration (8 tools)
```json
{
  "mcpServers": {
    "scientific-calculator": {
      "command": "uvx",
      "args": ["p6plab-mcp-calculator@latest"]
      // No environment variables = basic tools only
    }
  }
}
```

### Enable All Tools (68 tools)
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

## Tool Groups Reference

### Available Tool Groups

| Group | Tools | Description | Key Tools |
|-------|-------|-------------|-----------|
| **basic** | 8 | Basic arithmetic operations | add, subtract, multiply, divide, power, square_root, calculate, health_check |
| **advanced** | 5 | Advanced mathematical functions | trigonometric, logarithm, exponential, hyperbolic, convert_angle |
| **statistics** | 5 | Statistical analysis tools | descriptive_stats, probability_distribution, correlation_analysis, regression_analysis, hypothesis_test |
| **matrix** | 8 | Matrix operations and linear algebra | matrix_multiply, matrix_determinant, matrix_inverse, matrix_eigenvalues, solve_linear_system |
| **complex** | 6 | Complex number operations | complex_arithmetic, complex_magnitude, complex_phase, complex_conjugate, polar_conversion |
| **units** | 7 | Unit conversion tools | convert_units, get_available_units, validate_unit_compatibility, get_conversion_factor |
| **calculus** | 9 | Calculus operations | derivative, integral, numerical_derivative, numerical_integral, calculate_limit, taylor_series |
| **solver** | 6 | Equation solving tools | solve_linear, solve_quadratic, solve_polynomial, solve_system, find_roots, analyze_equation |
| **financial** | 7 | Financial mathematics | compound_interest, loan_payment, net_present_value, internal_rate_of_return, amortization_schedule |
| **currency** | 4 | Currency conversion | convert_currency, get_exchange_rate, get_supported_currencies, get_currency_info |
| **constants** | 3 | Mathematical and physical constants | get_constant, list_constants, search_constants |

### Individual Group Configuration

Enable specific tool groups by setting their environment variables to `true`:

```json
{
  "env": {
    // Basic tools are always enabled - no environment variable needed
    "CALCULATOR_ENABLE_ADVANCED": "true",   // Trigonometric, logarithmic functions
    "CALCULATOR_ENABLE_STATISTICS": "true", // Statistical analysis
    "CALCULATOR_ENABLE_MATRIX": "true",     // Matrix operations
    "CALCULATOR_ENABLE_COMPLEX": "true",    // Complex number math
    "CALCULATOR_ENABLE_UNITS": "true",      // Unit conversions
    "CALCULATOR_ENABLE_CALCULUS": "true",   // Derivatives, integrals
    "CALCULATOR_ENABLE_SOLVER": "true",     // Equation solving
    "CALCULATOR_ENABLE_FINANCIAL": "true",  // Financial calculations
    "CALCULATOR_ENABLE_CURRENCY": "true",   // Currency conversion
    "CALCULATOR_ENABLE_CONSTANTS": "true"   // Constants database
  }
}
```

## Preset Configurations

### Scientific Computing Preset
**Use case**: Research, data analysis, scientific computing
**Tools**: 42+ tools across 6 groups
```json
{
  "env": {
    "CALCULATOR_ENABLE_SCIENTIFIC": "true"
  }
}
```
**Includes**: basic, advanced, statistics, matrix, complex, calculus

### Business Analysis Preset
**Use case**: Financial analysis, business calculations, unit conversions
**Tools**: 22+ tools across 4 groups
```json
{
  "env": {
    "CALCULATOR_ENABLE_BUSINESS": "true"
  }
}
```
**Includes**: basic, financial, currency, units

### Engineering Preset
**Use case**: Engineering calculations, technical analysis
**Tools**: 38+ tools across 7 groups
```json
{
  "env": {
    "CALCULATOR_ENABLE_ENGINEERING": "true"
  }
}
```
**Includes**: basic, advanced, matrix, complex, calculus, units, constants

### All Tools Preset
**Use case**: Complete mathematical suite, development, testing
**Tools**: All 68 tools across 11 groups
```json
{
  "env": {
    "CALCULATOR_ENABLE_ALL": "true"
  }
}
```
**Includes**: All tool groups

## Configuration Examples

### Data Science Configuration
```json
{
  "env": {
    // Basic tools always enabled
    "CALCULATOR_ENABLE_STATISTICS": "true",
    "CALCULATOR_ENABLE_MATRIX": "true",
    "CALCULATOR_ENABLE_CALCULUS": "true"
  }
}
```

### Financial Analysis Configuration
```json
{
  "env": {
    // Basic tools always enabled
    "CALCULATOR_ENABLE_FINANCIAL": "true",
    "CALCULATOR_ENABLE_CURRENCY": "true",
    "CALCULATOR_ENABLE_STATISTICS": "true"
  }
}
```

### Mathematics Education Configuration
```json
{
  "env": {
    // Basic tools always enabled
    "CALCULATOR_ENABLE_ADVANCED": "true",
    "CALCULATOR_ENABLE_CALCULUS": "true",
    "CALCULATOR_ENABLE_CONSTANTS": "true"
  }
}
```

### Minimal Configuration (Default)
```json
{
  // No environment variables
  // Results in basic arithmetic tools only (8 tools)
}
```

## Boolean Value Formats

Environment variables accept various boolean formats (case-insensitive):

### True Values
- `true`, `TRUE`, `True`
- `1`
- `yes`, `YES`, `Yes`
- `on`, `ON`, `On`
- `enable`, `ENABLE`, `Enable`
- `enabled`, `ENABLED`, `Enabled`

### False Values
- `false`, `FALSE`, `False`
- `0`
- `no`, `NO`, `No`
- `off`, `OFF`, `Off`
- `disable`, `DISABLE`, `Disable`
- `disabled`, `DISABLED`, `Disabled`
- `""` (empty string)

### Invalid Values
Any other value is treated as `false` and generates a warning:
```
Invalid value 'maybe' for CALCULATOR_ENABLE_ADVANCED, treating as false
```

## Configuration Precedence

The configuration system follows this precedence order (highest to lowest):

1. **CALCULATOR_ENABLE_ALL** - Overrides everything, enables all 68 tools
2. **Other Presets** - SCIENTIFIC, BUSINESS, ENGINEERING (can be combined)
3. **Individual Groups** - Specific group enable/disable settings
4. **Legacy Variables** - CALCULATOR_ENABLE_ALL_TOOLS (deprecated)
5. **Default** - Basic tools only if no configuration provided

### Precedence Examples

#### All Override
```json
{
  "env": {
    "CALCULATOR_ENABLE_ADVANCED": "false",  // Ignored
    "CALCULATOR_ENABLE_MATRIX": "false",    // Ignored
    "CALCULATOR_ENABLE_ALL": "true"         // Overrides everything
  }
}
// Result: All 68 tools enabled (basic tools always included)
```

#### Preset Combination
```json
{
  "env": {
    "CALCULATOR_ENABLE_SCIENTIFIC": "true",  // 42+ tools
    "CALCULATOR_ENABLE_BUSINESS": "true"     // Additional tools
  }
}
// Result: Union of both presets (no duplicates)
```

#### Individual Override
```json
{
  "env": {
    "CALCULATOR_ENABLE_SCIENTIFIC": "true",  // Would enable calculus
    "CALCULATOR_ENABLE_CALCULUS": "false"    // But this disables it
  }
}
// Result: Scientific preset minus calculus group
```

## Configuration Validation

### Health Check Tool
Use the `health_check` tool to verify your configuration:

```json
{
  "status": "healthy",
  "tool_groups": {
    "enabled_groups": ["basic", "advanced", "statistics"],
    "disabled_groups": ["matrix", "complex", "units", "calculus", "solver", "financial", "currency", "constants"],
    "total_enabled_tools": 18,
    "total_available_tools": 68,
    "configuration_source": "individual"
  },
  "warnings": [],
  "migration_recommendations": []
}
```

### Configuration Sources
- `default` - No environment variables, basic tools only
- `individual` - Individual group settings
- `preset_all` - CALCULATOR_ENABLE_ALL=true
- `preset_scientific` - CALCULATOR_ENABLE_SCIENTIFIC=true
- `preset_business` - CALCULATOR_ENABLE_BUSINESS=true
- `preset_engineering` - CALCULATOR_ENABLE_ENGINEERING=true
- `preset_combined_*` - Multiple presets enabled
- `legacy` - Using deprecated CALCULATOR_ENABLE_ALL_TOOLS

### Warnings and Recommendations
The system provides helpful warnings and migration recommendations:

```json
{
  "warnings": [
    "Invalid value 'maybe' for CALCULATOR_ENABLE_ADVANCED, treating as false",
    "Legacy environment variable CALCULATOR_ENABLE_ALL_TOOLS is deprecated. Use CALCULATOR_ENABLE_ALL instead."
  ],
  "migration_recommendations": [
    "Replace CALCULATOR_ENABLE_ALL_TOOLS=true with CALCULATOR_ENABLE_ALL=true",
    "You have enabled all groups individually. Consider using CALCULATOR_ENABLE_ALL=true for simplicity."
  ]
}
```

## Migration Guide

### From Legacy Configuration

#### Old Configuration (Deprecated)
```json
{
  "env": {
    "CALCULATOR_ENABLE_ALL_TOOLS": "true"
  }
}
```

#### New Configuration (Recommended)
```json
{
  "env": {
    "CALCULATOR_ENABLE_ALL": "true"
  }
}
```

### From Version 0.1.0 to 0.1.1+

**Version 0.1.0 Issues:**
- Only 8 tools visible due to Python type annotation bug
- All 68 tools worked with direct Python execution

**Version 0.1.1+ Improvements:**
- All 68 tools work with uvx
- Tool group management system added
- Default changed to basic tools only (security improvement)

#### Migration Steps

1. **Update package version**:
   ```bash
   uvx p6plab-mcp-calculator@latest
   ```

2. **Add tool group configuration** (if you want more than basic tools):
   ```json
   {
     "env": {
       "CALCULATOR_ENABLE_ALL": "true"  // To maintain previous behavior
     }
   }
   ```

3. **Optimize configuration** for your use case:
   ```json
   {
     "env": {
       "CALCULATOR_ENABLE_SCIENTIFIC": "true"  // If you only need scientific tools
     }
   }
   ```

### From No Configuration

If you're upgrading from a version with no tool group management:

#### Before (All tools always available)
```json
{
  "mcpServers": {
    "scientific-calculator": {
      "command": "uvx",
      "args": ["p6plab-mcp-calculator@0.1.0"]
    }
  }
}
```

#### After (Choose your configuration)
```json
{
  "mcpServers": {
    "scientific-calculator": {
      "command": "uvx",
      "args": ["p6plab-mcp-calculator@latest"],
      "env": {
        "CALCULATOR_ENABLE_ALL": "true"  // To maintain all tools
        // OR choose a specific preset:
        // "CALCULATOR_ENABLE_SCIENTIFIC": "true"
      }
    }
  }
}
```

## Performance Considerations

### Tool Count vs Performance
- **8 tools (basic)**: Fastest startup, minimal memory
- **22+ tools (business)**: Good balance for business use
- **42+ tools (scientific)**: Comprehensive for research
- **68 tools (all)**: Complete suite, highest resource usage

### Recommendations by Use Case

#### Production Environments
- Use minimal configuration needed for your use case
- Avoid `CALCULATOR_ENABLE_ALL` unless necessary
- Consider security implications of enabled tools

#### Development Environments
- Use `CALCULATOR_ENABLE_ALL` for testing
- Enable debug logging: `CALCULATOR_LOG_LEVEL=DEBUG`

#### CI/CD Environments
- Use specific configurations for testing
- Validate tool counts in tests

## Security Considerations

### Principle of Least Privilege
- Only enable tool groups you actually need
- Basic arithmetic is safe for all environments
- Advanced tools may have higher computational costs

### Tool Group Security Levels
- **Low risk**: basic, advanced, statistics, constants
- **Medium risk**: matrix, complex, units, calculus, solver
- **Higher risk**: financial, currency (external API calls)

### Recommended Configurations by Environment

#### Public/Shared Environments
```json
{
  // No environment variables needed
  // Basic arithmetic tools are always available
}
```

#### Internal/Trusted Environments
```json
{
  "env": {
    "CALCULATOR_ENABLE_SCIENTIFIC": "true"
    // Scientific computing without external APIs
  }
}
```

#### Development/Testing Environments
```json
{
  "env": {
    "CALCULATOR_ENABLE_ALL": "true"
    // All tools for comprehensive testing
  }
}
```

## Troubleshooting Configuration

### Common Issues

#### Wrong Tool Count
```bash
# Check current configuration
# Use health_check tool to see:
# - enabled_groups
# - total_enabled_tools
# - configuration_source
# - warnings
```

#### Environment Variables Not Working
1. Check variable names (case-sensitive)
2. Verify boolean values
3. Ensure variables are in "env" section of MCP config
4. Restart MCP client after configuration changes

#### Unexpected Behavior
1. Check for typos in environment variable names
2. Verify precedence rules (ENABLE_ALL overrides everything)
3. Look for warnings in health_check output
4. Enable debug logging: `CALCULATOR_LOG_LEVEL=DEBUG`

### Debug Configuration
```json
{
  "env": {
    "CALCULATOR_LOG_LEVEL": "DEBUG",
    "CALCULATOR_ENABLE_SCIENTIFIC": "true"
  }
}
```

This will show detailed startup information including:
- Which groups are enabled/disabled
- Total tool count
- Configuration source
- Any warnings or recommendations

## Best Practices

### Configuration Management
1. **Document your configuration** - Include comments explaining why specific groups are enabled
2. **Use presets when possible** - They're easier to understand and maintain
3. **Validate configurations** - Use health_check to verify setup
4. **Version control** - Track MCP configuration changes

### Environment-Specific Configurations
1. **Development**: Use `CALCULATOR_ENABLE_ALL` for full testing
2. **Staging**: Match production configuration
3. **Production**: Use minimal required configuration
4. **CI/CD**: Use specific configurations for different test suites

### Monitoring and Maintenance
1. **Monitor tool usage** - Disable unused groups to improve performance
2. **Review configurations regularly** - Remove unnecessary tools
3. **Update configurations** - When upgrading package versions
4. **Test configurations** - Verify expected tool counts after changes