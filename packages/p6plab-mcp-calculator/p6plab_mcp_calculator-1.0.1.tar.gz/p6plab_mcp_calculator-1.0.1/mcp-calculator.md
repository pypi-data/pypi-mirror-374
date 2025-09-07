# Scientific Calculator MCP Server

## Overview
The Scientific Calculator MCP Server provides comprehensive mathematical computation capabilities to AI assistants through the Model Context Protocol (MCP). It enables advanced mathematical operations, statistical analysis, unit conversions, and scientific calculations while maintaining precision and proper error handling.

## Core Features

### Basic Operations
- Arithmetic operations (add, subtract, multiply, divide)
- Power and root operations
- Modular arithmetic
- Absolute value and sign functions

### Advanced Mathematical Functions
- Trigonometric functions (sin, cos, tan, sec, csc, cot)
- Inverse trigonometric functions (arcsin, arccos, arctan)
- Hyperbolic functions (sinh, cosh, tanh)
- Logarithmic functions (natural log, log base 10, custom base)
- Exponential functions

### Statistical Operations
- Descriptive statistics (mean, median, mode, standard deviation, variance)
- Probability distributions (normal, binomial, poisson)
- Correlation and regression analysis
- Hypothesis testing functions

### Advanced Calculations
- Matrix operations (multiplication, determinant, inverse, eigenvalues)
- Complex number arithmetic
- Calculus operations (derivatives, integrals)
- Equation solving (linear, quadratic, polynomial)

### Unit Conversions
- Length, weight, temperature, volume conversions
- Time zone conversions
- Scientific unit conversions (energy, pressure, etc.)

### Currency Conversion (Optional)
- Real-time currency exchange rates
- Multi-currency financial calculations
- Disabled by default for privacy/security

### Specialized Functions
- Financial calculations (compound interest, NPV, IRR)
- Engineering calculations
- Physics formulas and constants
- Chemistry calculations (molecular weight, stoichiometry)

## Technical Architecture

### Project Structure
```
p6plab-mcp-calculator/
├── pyproject.toml              # PyPI packaging configuration with uvx entry points
├── README.md                   # Installation and usage documentation
├── LICENSE                     # MIT License for PyPI distribution
├── .gitignore                  # Python gitignore
├── MANIFEST.in                 # PyPI package manifest
├── calculator/
│   ├── __init__.py
│   ├── server.py              # Main MCP server implementation
│   ├── core/
│   │   ├── __init__.py
│   │   ├── basic.py           # Basic arithmetic operations
│   │   ├── advanced.py        # Advanced mathematical functions
│   │   ├── statistics.py      # Statistical operations
│   │   ├── matrix.py          # Matrix operations
│   │   ├── complex.py         # Complex number operations
│   │   ├── calculus.py        # Calculus operations
│   │   ├── solver.py          # Equation solving
│   │   ├── units.py           # Unit conversions
│   │   ├── currency.py        # Currency conversion (optional)
│   │   ├── financial.py       # Financial calculations
│   │   ├── constants.py       # Mathematical and physical constants
│   │   └── validators.py      # Input validation and error handling
│   ├── models/
│   │   ├── __init__.py
│   │   ├── request.py         # Request models
│   │   ├── response.py        # Response models
│   │   └── errors.py          # Error models
│   └── utils/
│       ├── __init__.py
│       ├── precision.py       # Precision handling
│       ├── formatting.py      # Output formatting
│       └── helpers.py         # Utility functions
├── tests/
│   ├── __init__.py
│   ├── test_server.py
│   ├── test_basic.py
│   ├── test_advanced.py
│   ├── test_statistics.py
│   ├── test_matrix.py
│   ├── test_units.py
│   └── fixtures/
└── docs/
    ├── api.md
    ├── examples.md
    └── troubleshooting.md
```

### Dependencies
- **mcp**: Model Context Protocol framework
- **numpy**: Numerical computing
- **scipy**: Scientific computing
- **sympy**: Symbolic mathematics
- **pandas**: Data analysis (for statistical operations)
- **pydantic**: Data validation
- **decimal**: High-precision arithmetic
- **requests**: For currency conversion APIs (optional)
- **loguru**: Logging

### uvx Execution Requirements
- **Entry Points:** Package must define proper console scripts in pyproject.toml for uvx execution
- **Dependency Management:** uvx must automatically handle all package dependencies
- **Transport Support:** uvx execution must support all MCP transport protocols (stdio, HTTP, SSE)
- **Configuration:** uvx execution must support environment variable configuration
- **Error Handling:** uvx execution must provide clear startup and error messages
- **Performance:** uvx execution must meet all performance requirements without degradation

### PyPI Packaging Requirements
- **Build System:** Use modern Python packaging with pyproject.toml (PEP 518)
- **Metadata:** Complete package metadata including description, author, license, keywords, classifiers
- **Version Management:** Semantic versioning with automated version bumping
- **Distribution:** Support for both source distributions (sdist) and wheel distributions
- **Testing:** Automated testing on Test PyPI before production PyPI release
- **Documentation:** Complete PyPI-compatible README with installation and usage instructions

## Development Phases

### Phase 1: Foundation Setup (Week 1)
**Objectives:**
- Set up project structure and development environment
- Implement basic MCP server framework
- Create core models and error handling
- Implement basic arithmetic operations

**Tasks:**
1. Create project structure with proper directories
2. Set up pyproject.toml with dependencies
3. Implement FastMCP server setup in server.py
4. Create Pydantic models for requests/responses/errors
5. Implement basic arithmetic tools (add, subtract, multiply, divide, power, sqrt)
6. Add comprehensive error handling and validation
7. Create unit tests for basic operations
8. Set up logging with loguru

**Deliverables:**
- Working MCP server with basic arithmetic
- Complete project scaffolding
- Basic test suite
- Error handling framework

### Phase 2: Advanced Mathematical Functions (Week 2)
**Objectives:**
- Implement trigonometric and logarithmic functions
- Add support for complex numbers
- Implement mathematical constants
- Add precision handling

**Tasks:**
1. Implement trigonometric functions (sin, cos, tan, etc.)
2. Add logarithmic and exponential functions
3. Create complex number arithmetic module
4. Add mathematical constants (π, e, φ, etc.)
5. Implement precision control with decimal module
6. Create advanced function tests
7. Add input validation for advanced functions

**Deliverables:**
- Advanced mathematical functions
- Complex number support
- Mathematical constants library
- Precision handling system

### Phase 3: Statistical Operations (Week 3)
**Objectives:**
- Implement descriptive statistics
- Add probability distributions
- Create data analysis tools
- Implement correlation and regression

**Tasks:**
1. Implement descriptive statistics (mean, median, mode, std dev, variance)
2. Add probability distributions (normal, binomial, poisson)
3. Create correlation analysis functions
4. Implement linear and polynomial regression
5. Add hypothesis testing functions
6. Create statistical test suite
7. Add data validation for statistical operations

**Deliverables:**
- Complete statistical analysis toolkit
- Probability distribution functions
- Regression analysis capabilities
- Statistical test suite

### Phase 4: Matrix Operations and Linear Algebra (Week 4)
**Objectives:**
- Implement matrix operations
- Add linear algebra functions
- Create system of equations solver
- Implement eigenvalue/eigenvector calculations

**Tasks:**
1. Implement matrix arithmetic (addition, multiplication, transpose)
2. Add determinant and inverse calculations
3. Create eigenvalue and eigenvector computation
4. Implement system of linear equations solver
5. Add matrix decomposition functions
6. Create matrix operation tests
7. Add matrix validation and error handling

**Deliverables:**
- Complete matrix operations library
- Linear algebra functions
- Equation solver
- Matrix test suite

### Phase 5: Calculus and Equation Solving (Week 5)
**Objectives:**
- Implement symbolic differentiation and integration
- Add numerical methods for calculus
- Create equation solving capabilities
- Implement optimization functions

**Tasks:**
1. Implement symbolic derivatives using SymPy
2. Add definite and indefinite integrals
3. Create polynomial equation solver
4. Implement root finding algorithms
5. Add optimization functions (minimize, maximize)
6. Create calculus test suite
7. Add symbolic math validation

**Deliverables:**
- Calculus operations (derivatives, integrals)
- Equation solving capabilities
- Optimization functions
- Symbolic math support

### Phase 6: Unit Conversions and Currency (Week 6)
**Objectives:**
- Implement comprehensive unit conversion system
- Add optional currency conversion with external API
- Create physics and chemistry calculators
- Implement financial calculation tools

**Tasks:**
1. Create unit conversion system (length, weight, temperature, etc.)
2. Implement currency conversion with ExchangeRate-API
3. Add environment variable controls for currency feature
4. Create financial calculators (compound interest, NPV, IRR)
5. Add physics formulas and calculations
6. Implement chemistry calculations
7. Create conversion test suites

**Deliverables:**
- Unit conversion system
- Optional currency conversion
- Financial calculation tools
- Physics/chemistry calculators

### Phase 7: Performance Optimization and Advanced Features (Week 7)
**Objectives:**
- Optimize performance for large calculations
- Add caching for expensive operations
- Implement batch processing
- Add configuration management

**Tasks:**
1. Implement caching system for expensive operations
2. Add batch operation support
3. Optimize memory usage for large calculations
4. Create performance benchmarks
5. Add configuration management
6. Implement rate limiting
7. Add performance tests

**Deliverables:**
- Performance optimizations
- Caching system
- Batch processing capabilities
- Configuration management

### Phase 8: Documentation, Testing, and Deployment (Week 8)
**Objectives:**
- Complete comprehensive documentation
- Achieve high test coverage
- Create usage examples and tutorials
- Prepare for deployment

**Tasks:**
1. Write complete API documentation
2. Create comprehensive test suite
3. Write usage examples and tutorials
4. Create deployment guides
5. Add security audit
6. Create performance benchmarks
7. Prepare PyPI package

**Deliverables:**
- Complete documentation
- High test coverage
- Usage examples
- Deployment-ready package

## MCP Tools Specification

### Basic Operations
```python
@server.tool(name="calculate")
async def calculate(expression: str) -> dict:
    """Evaluate mathematical expressions with proper order of operations."""

@server.tool(name="add")
async def add(a: float, b: float) -> dict:
    """Add two numbers with high precision."""

@server.tool(name="power")
async def power(base: float, exponent: float) -> dict:
    """Calculate base raised to the power of exponent."""
```

### Advanced Functions
```python
@server.tool(name="trigonometric")
async def trigonometric(function: str, value: float, unit: str = "radians") -> dict:
    """Calculate trigonometric functions (sin, cos, tan, etc.)."""

@server.tool(name="logarithm")
async def logarithm(value: float, base: float = None) -> dict:
    """Calculate logarithm with specified base (natural log if base not provided)."""
```

### Statistical Operations
```python
@server.tool(name="descriptive_stats")
async def descriptive_stats(data: list[float]) -> dict:
    """Calculate descriptive statistics for a dataset."""

@server.tool(name="probability_distribution")
async def probability_distribution(distribution: str, parameters: dict, x: float) -> dict:
    """Calculate probability density/mass function values."""
```

### Matrix Operations
```python
@server.tool(name="matrix_multiply")
async def matrix_multiply(matrix_a: list[list[float]], matrix_b: list[list[float]]) -> dict:
    """Multiply two matrices."""

@server.tool(name="matrix_determinant")
async def matrix_determinant(matrix: list[list[float]]) -> dict:
    """Calculate the determinant of a square matrix."""
```

### Unit Conversions
```python
@server.tool(name="convert_units")
async def convert_units(value: float, from_unit: str, to_unit: str, unit_type: str) -> dict:
    """Convert between different units of measurement."""

@server.tool(name="convert_currency")
async def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    """Convert between currencies using real-time exchange rates (if enabled)."""
```

## Configuration Options

### Environment Variables
- `CALCULATOR_PRECISION`: Decimal precision for calculations (default: 15)
- `CALCULATOR_LOG_LEVEL`: Logging level (default: INFO)
- `CALCULATOR_CACHE_SIZE`: Cache size for expensive operations (default: 1000)
- `CALCULATOR_ENABLE_CURRENCY_CONVERSION`: Enable currency conversion (default: false)
- `CALCULATOR_CURRENCY_API_KEY`: API key for currency conversion (optional)
- `CALCULATOR_WORKING_DIR`: Working directory for temporary files

### Server Configuration
- Support for both stdio and HTTP transport
- Configurable timeout settings
- Memory usage limits
- Concurrent operation limits

## Error Handling

### Error Types
- `CalculationError`: General calculation errors
- `ValidationError`: Input validation errors
- `PrecisionError`: Precision-related errors
- `UnitConversionError`: Unit conversion errors
- `MatrixError`: Matrix operation errors
- `CurrencyError`: Currency conversion errors

### Error Response Format
```python
{
    "error": true,
    "error_type": "CalculationError",
    "message": "Division by zero",
    "details": {
        "operation": "divide",
        "inputs": {"a": 5, "b": 0}
    },
    "suggestions": ["Check for zero denominators before division"]
}
```

## Security Considerations

### Input Validation
- Strict validation of all mathematical expressions
- Prevention of code injection through eval()
- Limits on computation complexity and memory usage
- Sanitization of all user inputs

### Resource Limits
- Maximum computation time limits
- Memory usage restrictions
- Concurrent operation limits
- Rate limiting for expensive operations

### Privacy Controls
- Currency conversion disabled by default
- No external API calls without explicit enablement
- Local computation preferred over external services

## Performance Requirements

### Response Times
- Basic operations: < 10ms
- Advanced functions: < 100ms
- Statistical operations: < 500ms
- Matrix operations: < 1s (depending on size)
- Unit conversions: < 50ms
- Currency conversions: < 2s (external API dependent)

### Accuracy Requirements
- Floating-point precision: 15 decimal places
- Statistical calculations: 99.9% accuracy
- Unit conversions: 100% accuracy
- Financial calculations: Exact precision

## Installation and Usage

### Installation Methods
```bash
# Using pip from PyPI
pip install p6plab-mcp-calculator

# Using uvx (recommended for MCP servers)
uvx p6plab-mcp-calculator@latest

# Development installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ p6plab-mcp-calculator
```

### PyPI Distribution Requirements
- **PyPI Publication:** Package must be available on https://pypi.org/
- **Test PyPI Validation:** Package must be tested on https://test.pypi.org/ before production release
- **uvx Compatibility:** Package must support execution via uvx for seamless MCP server deployment
- **Semantic Versioning:** Package versions must follow semantic versioning standards
- **Metadata Compliance:** Package must include proper PyPI metadata (description, author, license, keywords)
- **Entry Points:** Package must define proper console scripts and entry points for uvx execution

### MCP Client Configuration
```json
{
  "mcpServers": {
    "p6plab-mcp-calculator": {
      "command": "uvx",
      "args": ["p6plab-mcp-calculator@latest"],
      "env": {
        "CALCULATOR_PRECISION": "15",
        "CALCULATOR_LOG_LEVEL": "INFO",
        "CALCULATOR_ENABLE_CURRENCY_CONVERSION": "false"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## Testing Strategy

### Unit Tests
- Individual function testing
- Edge case handling
- Error condition testing
- Performance benchmarking

### Integration Tests
- End-to-end MCP communication
- Complex calculation workflows
- Error propagation testing
- Resource usage testing

### Performance Tests
- Load testing with concurrent operations
- Memory usage profiling
- Response time benchmarking
- Stress testing with large datasets

This specification provides a comprehensive roadmap for developing a robust scientific calculator MCP server that prioritizes security, performance, and user control over external dependencies.
