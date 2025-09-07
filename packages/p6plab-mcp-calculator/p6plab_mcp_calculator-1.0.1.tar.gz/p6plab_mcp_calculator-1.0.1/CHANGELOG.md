# Changelog

All notable changes to the Scientific Calculator MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.1/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-09-06

### 🚀 Added
- **68 Mathematical Tools** across 11 categories:
  - **Basic Arithmetic** (8 tools): add, subtract, multiply, divide, power, square_root, calculate, health_check
  - **Advanced Mathematics** (5 tools): trigonometric, logarithm, exponential, hyperbolic, convert_angle
  - **Statistics** (5 tools): descriptive_stats, probability_distribution, correlation_analysis, regression_analysis, hypothesis_test
  - **Matrix Operations** (8 tools): matrix_multiply, matrix_determinant, matrix_inverse, matrix_eigenvalues, solve_linear_system, matrix_operations, matrix_arithmetic, create_matrix
  - **Complex Numbers** (6 tools): complex_arithmetic, complex_magnitude, complex_phase, complex_conjugate, polar_conversion, complex_functions
  - **Unit Conversion** (7 tools): convert_units, get_available_units, validate_unit_compatibility, get_conversion_factor, convert_multiple_units, find_unit_by_name, get_unit_info
  - **Calculus** (9 tools): derivative, integral, numerical_derivative, numerical_integral, calculate_limit, taylor_series, find_critical_points, gradient, evaluate_expression
  - **Equation Solving** (6 tools): solve_linear, solve_quadratic, solve_polynomial, solve_system, find_roots, analyze_equation
  - **Financial Mathematics** (7 tools): compound_interest, loan_payment, net_present_value, internal_rate_of_return, present_value, future_value_annuity, amortization_schedule
  - **Currency Conversion** (4 tools): convert_currency, get_exchange_rate, get_supported_currencies, get_currency_info
  - **Constants & References** (3 tools): get_constant, list_constants, search_constants
- **Tool Group Management System**: Selective enabling/disabling of mathematical tool groups
  - 11 tool groups: basic, advanced, statistics, matrix, complex, units, calculus, solver, financial, currency, constants
  - Environment variable configuration for individual groups (e.g., `CALCULATOR_ENABLE_ADVANCED=true`)
  - Preset combinations: `CALCULATOR_ENABLE_SCIENTIFIC`, `CALCULATOR_ENABLE_BUSINESS`, `CALCULATOR_ENABLE_ENGINEERING`, `CALCULATOR_ENABLE_ALL`
  - Basic arithmetic tools are always enabled (no configuration needed)
- **Enhanced Health Check**: Comprehensive reporting of enabled/disabled tool groups, configuration source, warnings, and recommendations
- **Access Monitoring**: Tracking of disabled tool access attempts with usage recommendations
- **Configuration Validation**: Robust parsing of boolean environment variables with helpful error messages
- **Legacy Support**: Backward compatibility with `CALCULATOR_ENABLE_ALL_TOOLS` (deprecated)
- **Comprehensive Documentation**: 
  - New installation guide with tool group examples
  - Configuration guide with all environment variables and use cases
  - Updated deployment guide with tool group configuration
  - Example prompts section with 100+ natural language examples
- **Extensive Testing**: 216+ test cases covering all tool group scenarios and edge cases

### 🏗️ Architecture
- **FastMCP Framework**: Built on FastMCP v2.0+ for robust MCP protocol support
- **Scientific Computing Stack**: NumPy, SciPy, SymPy for comprehensive mathematical operations
- **Modular Design**: Organized into logical modules for maintainability
- **Error Handling**: Comprehensive error handling with structured responses
- **Validation**: Input validation using Pydantic models
- **Logging**: Structured logging with loguru

### 📦 Distribution
- **PyPI Package**: Available as `p6plab-mcp-calculator` on PyPI
- **uvx Support**: Optimized for uvx execution in isolated environments
- **Multiple Installation Methods**: pip, uvx, and source installation
- **Cross-Platform**: Support for Windows, macOS, and Linux

### 🔧 Configuration & Compatibility
- **Default Behavior**: Only basic arithmetic tools (8 tools) enabled by default for security and performance
- **Server Startup**: Enhanced logging with detailed tool group configuration information
- **Error Messages**: Improved error responses for disabled tools with actionable suggestions
- **Environment Variables**: Configurable precision, logging, timeouts
- **Currency API**: Optional currency conversion with API key support
- **Performance Tuning**: Configurable cache size and memory limits
- **Python Compatibility**: Improved support for Python 3.10+ environments
- **uvx Execution**: Optimized for uvx isolated environment execution

### 🛠️ Fixed
- **uvx Compatibility**: Resolved Python 3.10 type annotation issues that caused only 8 tools to be visible
- **Type Annotations**: Fixed SymPy infinity objects (`sp.oo`) in type hints for Python 3.10 compatibility
- **Tool Registration**: All 68 tools now properly register and function with uvx execution
- **Basic Tools Logic**: Basic arithmetic tools are now always enabled, preventing accidental disabling
- **Configuration Precedence**: Proper handling of preset combinations and individual group settings
- **Environment Variable Parsing**: Robust validation with support for various boolean formats
- **macOS Compatibility**: Updated all scripts to use `gtimeout` instead of `timeout`

### 📚 Documentation
- Comprehensive API documentation
- Installation and deployment guides
- Usage examples and troubleshooting
- Development setup instructions
- Added comprehensive example prompts for all 68 tools across 11 categories
- Configuration-specific examples for different use cases (scientific, business, engineering)
- Pro tips for writing effective prompts and troubleshooting configuration issues
- Migration guide from legacy environment variables
- Updated troubleshooting guide with uvx compatibility information
- Added verification commands to check tool count

### 🧪 Testing
- Extensive test suite with pytest
- Unit tests for all mathematical operations
- Integration tests for MCP functionality
- Performance and edge case testing
- Complete test suite with 216+ test cases
- Configuration matrix testing for all possible combinations
- Integration tests for MCP server with tool filtering

---

## Version History Summary

| Version | Release Date | Key Features | Tools Available |
|---------|--------------|--------------|-----------------|
| **1.0.1** | 2025-09-06 | 🚀 Complete Scientific Calculator MCP Server | 8-68 (configurable) |

## Migration Guide

### Version 1.0.1 - Initial Stable Release
- **Complete Feature Set**: All 68 mathematical tools across 11 categories
- **Tool Group Management**: Selective enabling/disabling of tool groups for security and performance
- **Default Configuration**: Only basic arithmetic tools (8 tools) enabled by default
- **Full Configuration**: Add `CALCULATOR_ENABLE_ALL=true` to enable all 68 tools
- **uvx Compatible**: All tools work properly with uvx execution
- **Update Command**: `uvx p6plab-mcp-calculator@latest` to get the latest version

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on:
- Reporting bugs and requesting features
- Development setup and testing
- Code style and documentation standards
- Pull request process

## Support

- **Documentation**: [README.md](README.md) and [docs/](docs/) directory
- **Issues**: [GitHub Issues](https://github.com/peepeepopapapeepeepo/mcp-calculator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/peepeepopapapeepeepo/mcp-calculator/discussions)

---

**Legend:**
- 🚀 **Added**: New features and capabilities
- 🔧 **Changed**: Changes to existing functionality
- 🛠️ **Fixed**: Bug fixes and corrections
- 📚 **Documentation**: Documentation improvements
- 🧪 **Testing**: Testing enhancements
- ⚠️ **Deprecated**: Features marked for removal
- 🗑️ **Removed**: Removed features
- 🔒 **Security**: Security improvements