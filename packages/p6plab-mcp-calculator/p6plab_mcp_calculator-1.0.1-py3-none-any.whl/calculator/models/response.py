"""Pydantic response models for output formatting."""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    """Base response model with success/error status."""

    success: bool = Field(default=True, description="Whether the operation was successful")
    timestamp: Optional[str] = Field(default=None, description="Response timestamp")
    execution_time_ms: Optional[float] = Field(
        default=None, description="Execution time in milliseconds"
    )


class CalculationResult(BaseResponse):
    """Response model for basic calculation results."""

    result: Union[float, int, str, complex] = Field(..., description="Calculation result")
    operation: str = Field(..., description="Type of operation performed")
    inputs: Dict[str, Any] = Field(..., description="Input parameters used")
    precision: int = Field(..., description="Decimal precision used")
    unit: Optional[str] = Field(default=None, description="Unit of the result")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class ExpressionResult(BaseResponse):
    """Response model for mathematical expression evaluation."""

    result: Union[float, int, str, complex] = Field(
        ..., description="Expression evaluation result"
    )
    expression: str = Field(..., description="Original expression")
    simplified_expression: Optional[str] = Field(default=None, description="Simplified form")
    variables_used: List[str] = Field(
        default_factory=list, description="Variables found in expression"
    )
    precision: int = Field(..., description="Decimal precision used")


class StatisticalResult(BaseResponse):
    """Response model for statistical analysis results."""

    mean: float = Field(..., description="Arithmetic mean")
    median: float = Field(..., description="Median value")
    mode: Optional[Union[float, List[float]]] = Field(default=None, description="Mode value(s)")
    std_dev: float = Field(..., description="Standard deviation")
    variance: float = Field(..., description="Variance")
    min_value: float = Field(..., description="Minimum value")
    max_value: float = Field(..., description="Maximum value")
    count: int = Field(..., description="Number of data points")
    quartiles: Dict[str, float] = Field(..., description="Quartile values (Q1, Q2, Q3)")
    range: float = Field(..., description="Range (max - min)")
    skewness: Optional[float] = Field(default=None, description="Skewness measure")
    kurtosis: Optional[float] = Field(default=None, description="Kurtosis measure")


class ProbabilityResult(BaseResponse):
    """Response model for probability distribution calculations."""

    probability: float = Field(..., description="Calculated probability")
    distribution: str = Field(..., description="Distribution type used")
    parameters: Dict[str, Any] = Field(..., description="Distribution parameters")
    x_value: float = Field(..., description="Input value")
    pdf_value: Optional[float] = Field(
        default=None, description="Probability density function value"
    )
    cdf_value: Optional[float] = Field(
        default=None, description="Cumulative distribution function value"
    )


class MatrixResult(BaseResponse):
    """Response model for matrix operation results."""

    result: List[List[float]] = Field(..., description="Resulting matrix")
    operation: str = Field(..., description="Matrix operation performed")
    dimensions: tuple[int, int] = Field(..., description="Result matrix dimensions (rows, cols)")
    determinant: Optional[float] = Field(default=None, description="Matrix determinant")
    rank: Optional[int] = Field(default=None, description="Matrix rank")
    condition_number: Optional[float] = Field(default=None, description="Condition number")
    eigenvalues: Optional[List[Union[float, complex]]] = Field(
        default=None, description="Eigenvalues"
    )
    eigenvectors: Optional[List[List[Union[float, complex]]]] = Field(
        default=None, description="Eigenvectors"
    )
    is_singular: Optional[bool] = Field(default=None, description="Whether matrix is singular")


class ComplexResult(BaseResponse):
    """Response model for complex number operations."""

    result: Union[complex, float] = Field(..., description="Complex operation result")
    operation: str = Field(..., description="Complex operation performed")
    inputs: Dict[str, complex] = Field(..., description="Input complex numbers")
    magnitude: Optional[float] = Field(default=None, description="Magnitude of result")
    phase: Optional[float] = Field(default=None, description="Phase angle in radians")
    phase_degrees: Optional[float] = Field(default=None, description="Phase angle in degrees")
    rectangular_form: Optional[str] = Field(
        default=None, description="Rectangular form representation"
    )
    polar_form: Optional[str] = Field(default=None, description="Polar form representation")


class ConversionResult(BaseResponse):
    """Response model for unit conversions."""

    result: float = Field(..., description="Converted value")
    original_value: float = Field(..., description="Original value")
    from_unit: str = Field(..., description="Source unit")
    to_unit: str = Field(..., description="Target unit")
    unit_type: str = Field(..., description="Type of unit conversion")
    conversion_factor: float = Field(..., description="Conversion factor used")
    formula: Optional[str] = Field(default=None, description="Conversion formula")


class CurrencyResult(BaseResponse):
    """Response model for currency conversions."""

    result: float = Field(..., description="Converted amount")
    original_amount: float = Field(..., description="Original amount")
    from_currency: str = Field(..., description="Source currency code")
    to_currency: str = Field(..., description="Target currency code")
    exchange_rate: float = Field(..., description="Exchange rate used")
    rate_timestamp: Optional[str] = Field(default=None, description="Exchange rate timestamp")
    rate_source: Optional[str] = Field(default=None, description="Exchange rate data source")


class FinancialResult(BaseResponse):
    """Response model for financial calculations."""

    result: Union[float, Dict[str, float]] = Field(..., description="Financial calculation result")
    calculation_type: str = Field(..., description="Type of financial calculation")
    parameters: Dict[str, Any] = Field(..., description="Input parameters")
    formula: Optional[str] = Field(default=None, description="Formula used")
    breakdown: Optional[Dict[str, Any]] = Field(
        default=None, description="Detailed calculation breakdown"
    )
    assumptions: Optional[List[str]] = Field(default=None, description="Calculation assumptions")


class EquationSolutionResult(BaseResponse):
    """Response model for equation solving results."""

    solutions: List[Dict[str, Union[float, complex]]] = Field(
        ..., description="Equation solutions"
    )
    equation_type: str = Field(..., description="Type of equation solved")
    original_equations: List[str] = Field(..., description="Original equations")
    variables: List[str] = Field(..., description="Variables in the equations")
    method_used: str = Field(..., description="Solution method used")
    is_exact: bool = Field(..., description="Whether solutions are exact or approximate")
    verification: Optional[Dict[str, bool]] = Field(
        default=None, description="Solution verification results"
    )


class CalculusResult(BaseResponse):
    """Response model for calculus operations."""

    result: Union[str, float] = Field(..., description="Calculus operation result")
    operation: str = Field(..., description="Calculus operation performed")
    original_expression: str = Field(..., description="Original expression")
    variable: str = Field(..., description="Variable used")
    symbolic_result: Optional[str] = Field(default=None, description="Symbolic form of result")
    numerical_result: Optional[float] = Field(default=None, description="Numerical approximation")
    bounds: Optional[Dict[str, float]] = Field(default=None, description="Integration bounds")
    method_used: str = Field(..., description="Calculation method used")


class ConstantResult(BaseResponse):
    """Response model for mathematical constants."""

    value: Union[float, str] = Field(..., description="Constant value")
    name: str = Field(..., description="Constant name")
    symbol: Optional[str] = Field(default=None, description="Mathematical symbol")
    description: str = Field(..., description="Constant description")
    category: str = Field(..., description="Constant category")
    precision: int = Field(..., description="Decimal precision")
    references: Optional[List[str]] = Field(default=None, description="Reference sources")


class FormulaResult(BaseResponse):
    """Response model for mathematical formulas."""

    formula: str = Field(..., description="Mathematical formula")
    name: str = Field(..., description="Formula name")
    domain: str = Field(..., description="Mathematical domain")
    description: str = Field(..., description="Formula description")
    variables: Dict[str, str] = Field(..., description="Variable definitions")
    examples: Optional[List[str]] = Field(default=None, description="Usage examples")
    related_formulas: Optional[List[str]] = Field(default=None, description="Related formulas")


class HealthCheckResult(BaseResponse):
    """Response model for server health check."""

    status: str = Field(..., description="Server status")
    server: str = Field(..., description="Server name")
    version: str = Field(..., description="Server version")
    precision: int = Field(..., description="Current precision setting")
    cache_size: int = Field(..., description="Cache size setting")
    max_computation_time: int = Field(..., description="Maximum computation time")
    max_memory_mb: int = Field(..., description="Maximum memory limit")
    currency_enabled: bool = Field(..., description="Currency conversion status")
    message: str = Field(..., description="Status message")
    uptime: Optional[float] = Field(default=None, description="Server uptime in seconds")
    memory_usage: Optional[Dict[str, float]] = Field(
        default=None, description="Memory usage statistics"
    )


class BatchResult(BaseResponse):
    """Response model for batch operations."""

    results: List[BaseResponse] = Field(..., description="Individual operation results")
    total_operations: int = Field(..., description="Total number of operations")
    successful_operations: int = Field(..., description="Number of successful operations")
    failed_operations: int = Field(..., description="Number of failed operations")
    total_execution_time_ms: float = Field(..., description="Total execution time")
    batch_id: Optional[str] = Field(default=None, description="Batch operation identifier")


class ValidationResult(BaseResponse):
    """Response model for input validation results."""

    is_valid: bool = Field(..., description="Whether input is valid")
    validation_errors: List[str] = Field(
        default_factory=list, description="Validation error messages"
    )
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    validated_input: Optional[Dict[str, Any]] = Field(
        default=None, description="Cleaned/validated input"
    )
