"""Error models and exception classes for the calculator."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CalculatorError(Exception):
    """Base exception class for calculator operations."""

    def __init__(
        self,
        message: str,
        error_type: str = "CalculatorError",
        details: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.details = details or {}
        self.suggestions = suggestions or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format."""
        return {
            "error": True,
            "error_type": self.error_type,
            "message": self.message,
            "details": self.details,
            "suggestions": self.suggestions,
        }


class ValidationError(CalculatorError):
    """Exception for input validation errors."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        suggestions: Optional[List[str]] = None,
    ):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["invalid_value"] = str(value)

        default_suggestions = [
            "Check input format and data types",
            "Ensure all required fields are provided",
            "Verify that numeric values are within valid ranges",
        ]

        super().__init__(
            message=message,
            error_type="ValidationError",
            details=details,
            suggestions=suggestions or default_suggestions,
        )


class PrecisionError(CalculatorError):
    """Exception for precision-related errors."""

    def __init__(
        self,
        message: str,
        requested_precision: Optional[int] = None,
        max_precision: Optional[int] = None,
        suggestions: Optional[List[str]] = None,
    ):
        details = {}
        if requested_precision is not None:
            details["requested_precision"] = requested_precision
        if max_precision is not None:
            details["max_precision"] = max_precision

        default_suggestions = [
            "Reduce the requested precision",
            "Use appropriate data types for high precision calculations",
            "Consider using symbolic computation for exact results",
        ]

        super().__init__(
            message=message,
            error_type="PrecisionError",
            details=details,
            suggestions=suggestions or default_suggestions,
        )


class MatrixError(CalculatorError):
    """Exception for matrix operation errors."""

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        matrix_dimensions: Optional[tuple] = None,
        suggestions: Optional[List[str]] = None,
    ):
        details = {}
        if operation:
            details["operation"] = operation
        if matrix_dimensions:
            details["matrix_dimensions"] = matrix_dimensions

        default_suggestions = [
            "Check matrix dimensions for compatibility",
            "Ensure matrices are not singular for inversion operations",
            "Verify that matrices contain only finite numeric values",
        ]

        super().__init__(
            message=message,
            error_type="MatrixError",
            details=details,
            suggestions=suggestions or default_suggestions,
        )


class UnitConversionError(CalculatorError):
    """Exception for unit conversion errors."""

    def __init__(
        self,
        message: str,
        from_unit: Optional[str] = None,
        to_unit: Optional[str] = None,
        unit_type: Optional[str] = None,
        suggestions: Optional[List[str]] = None,
    ):
        details = {}
        if from_unit:
            details["from_unit"] = from_unit
        if to_unit:
            details["to_unit"] = to_unit
        if unit_type:
            details["unit_type"] = unit_type

        default_suggestions = [
            "Check that both units belong to the same unit type",
            "Verify unit names and abbreviations are correct",
            "Use supported unit types: length, weight, temperature, volume, time, energy, pressure",
        ]

        super().__init__(
            message=message,
            error_type="UnitConversionError",
            details=details,
            suggestions=suggestions or default_suggestions,
        )


class CurrencyError(CalculatorError):
    """Exception for currency conversion errors."""

    def __init__(
        self,
        message: str,
        from_currency: Optional[str] = None,
        to_currency: Optional[str] = None,
        api_error: Optional[str] = None,
        suggestions: Optional[List[str]] = None,
    ):
        details = {}
        if from_currency:
            details["from_currency"] = from_currency
        if to_currency:
            details["to_currency"] = to_currency
        if api_error:
            details["api_error"] = api_error

        default_suggestions = [
            "Ensure currency conversion is enabled in configuration",
            "Check that currency codes are valid ISO 4217 codes",
            "Verify internet connection for real-time exchange rates",
            "Try again later if external API is temporarily unavailable",
        ]

        super().__init__(
            message=message,
            error_type="CurrencyError",
            details=details,
            suggestions=suggestions or default_suggestions,
        )


class ComputationError(CalculatorError):
    """Exception for general computation errors."""

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        inputs: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
    ):
        details = {}
        if operation:
            details["operation"] = operation
        if inputs:
            details["inputs"] = inputs

        default_suggestions = [
            "Check input values for mathematical validity",
            "Ensure operations are defined for the given inputs",
            "Consider using alternative computational methods",
        ]

        super().__init__(
            message=message,
            error_type="ComputationError",
            details=details,
            suggestions=suggestions or default_suggestions,
        )


class TimeoutError(CalculatorError):
    """Exception for computation timeout errors."""

    def __init__(
        self,
        message: str,
        timeout_seconds: Optional[float] = None,
        operation: Optional[str] = None,
        suggestions: Optional[List[str]] = None,
    ):
        details = {}
        if timeout_seconds:
            details["timeout_seconds"] = timeout_seconds
        if operation:
            details["operation"] = operation

        default_suggestions = [
            "Simplify the computation or reduce input size",
            "Increase the computation timeout limit",
            "Break complex operations into smaller steps",
        ]

        super().__init__(
            message=message,
            error_type="TimeoutError",
            details=details,
            suggestions=suggestions or default_suggestions,
        )


class MemoryError(CalculatorError):
    """Exception for memory limit errors."""

    def __init__(
        self,
        message: str,
        memory_used_mb: Optional[float] = None,
        memory_limit_mb: Optional[float] = None,
        suggestions: Optional[List[str]] = None,
    ):
        details = {}
        if memory_used_mb:
            details["memory_used_mb"] = memory_used_mb
        if memory_limit_mb:
            details["memory_limit_mb"] = memory_limit_mb

        default_suggestions = [
            "Reduce the size of input data",
            "Increase the memory limit configuration",
            "Process data in smaller batches",
        ]

        super().__init__(
            message=message,
            error_type="MemoryError",
            details=details,
            suggestions=suggestions or default_suggestions,
        )


class ConfigurationError(CalculatorError):
    """Exception for configuration-related errors."""

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_value: Optional[Any] = None,
        suggestions: Optional[List[str]] = None,
    ):
        details = {}
        if config_key:
            details["config_key"] = config_key
        if config_value is not None:
            details["config_value"] = str(config_value)

        default_suggestions = [
            "Check environment variable configuration",
            "Ensure configuration values are within valid ranges",
            "Restart the server after configuration changes",
        ]

        super().__init__(
            message=message,
            error_type="ConfigurationError",
            details=details,
            suggestions=suggestions or default_suggestions,
        )


class ErrorResponse(BaseModel):
    """Pydantic model for structured error responses."""

    error: bool = Field(default=True, description="Error flag")
    error_type: str = Field(..., description="Type of error")
    message: str = Field(..., description="Error message")
    details: Dict[str, Any] = Field(default_factory=dict, description="Error details")
    suggestions: List[str] = Field(default_factory=list, description="Suggested solutions")
    timestamp: Optional[str] = Field(default=None, description="Error timestamp")
    request_id: Optional[str] = Field(default=None, description="Request identifier")

    @classmethod
    def from_exception(
        cls, exc: CalculatorError, request_id: Optional[str] = None
    ) -> "ErrorResponse":
        """Create ErrorResponse from CalculatorError exception."""
        import datetime

        return cls(
            error_type=exc.error_type,
            message=exc.message,
            details=exc.details,
            suggestions=exc.suggestions,
            timestamp=datetime.datetime.utcnow().isoformat(),
            request_id=request_id,
        )

    @classmethod
    def from_generic_exception(
        cls, exc: Exception, error_type: str = "UnknownError", request_id: Optional[str] = None
    ) -> "ErrorResponse":
        """Create ErrorResponse from generic exception."""
        import datetime

        return cls(
            error_type=error_type,
            message=str(exc),
            details={"exception_type": type(exc).__name__},
            suggestions=["Contact support if this error persists"],
            timestamp=datetime.datetime.utcnow().isoformat(),
            request_id=request_id,
        )


# Error code mappings for different error types
ERROR_CODES = {
    "ValidationError": 400,
    "PrecisionError": 422,
    "MatrixError": 422,
    "UnitConversionError": 422,
    "CurrencyError": 503,
    "ComputationError": 422,
    "TimeoutError": 408,
    "MemoryError": 507,
    "ConfigurationError": 500,
    "UnknownError": 500,
}


def get_error_code(error_type: str) -> int:
    """Get HTTP status code for error type."""
    return ERROR_CODES.get(error_type, 500)


def create_error_response(
    error_type: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    suggestions: Optional[List[str]] = None,
    request_id: Optional[str] = None,
) -> ErrorResponse:
    """Create a standardized error response."""
    import datetime

    return ErrorResponse(
        error_type=error_type,
        message=message,
        details=details or {},
        suggestions=suggestions or [],
        timestamp=datetime.datetime.utcnow().isoformat(),
        request_id=request_id,
    )
