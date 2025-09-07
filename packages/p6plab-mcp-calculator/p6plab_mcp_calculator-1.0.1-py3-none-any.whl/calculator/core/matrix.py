"""
Matrix operations module for the Scientific Calculator MCP Server.

This module provides comprehensive matrix operations including arithmetic,
linear algebra operations, and system solving capabilities using NumPy.
"""

from typing import List, Dict, Any, Union, Tuple, Optional
import numpy as np
from numpy.linalg import LinAlgError
from decimal import Decimal

from calculator.models.errors import CalculatorError, ValidationError


class MatrixError(CalculatorError):
    """Error for matrix operations."""
    pass


def _validate_matrix(matrix: List[List[Union[float, int]]], name: str = "matrix") -> np.ndarray:
    """Validate and convert matrix to numpy array."""
    if not matrix:
        raise ValidationError(f"{name} cannot be empty")
    
    if not isinstance(matrix, list):
        raise ValidationError(f"{name} must be a list of lists")
    
    # Check if all rows are lists
    if not all(isinstance(row, list) for row in matrix):
        raise ValidationError(f"All rows in {name} must be lists")
    
    # Check if matrix is rectangular (all rows have same length)
    row_lengths = [len(row) for row in matrix]
    if not all(length == row_lengths[0] for length in row_lengths):
        raise ValidationError(f"{name} must be rectangular (all rows must have same length)")
    
    if row_lengths[0] == 0:
        raise ValidationError(f"{name} rows cannot be empty")
    
    # Check matrix size limits
    rows, cols = len(matrix), row_lengths[0]
    if rows > 1000 or cols > 1000:
        raise ValidationError(f"{name} too large (maximum 1000x1000)")
    
    try:
        # Convert to numpy array and validate numeric values
        np_matrix = np.array(matrix, dtype=float)
        
        # Check for invalid values (inf, nan)
        if not np.all(np.isfinite(np_matrix)):
            raise ValidationError(f"{name} contains invalid values (inf or nan)")
        
        return np_matrix
        
    except (ValueError, TypeError) as e:
        raise ValidationError(f"Invalid numeric values in {name}: {e}") from e


def _validate_square_matrix(matrix: np.ndarray, name: str = "matrix") -> np.ndarray:
    """Validate that a matrix is square."""
    if matrix.shape[0] != matrix.shape[1]:
        raise MatrixError(f"{name} must be square, got {matrix.shape[0]}x{matrix.shape[1]}")
    return matrix


def _validate_compatible_for_multiplication(matrix_a: np.ndarray, matrix_b: np.ndarray) -> None:
    """Validate that two matrices are compatible for multiplication."""
    if matrix_a.shape[1] != matrix_b.shape[0]:
        raise MatrixError(
            f"Matrices not compatible for multiplication: "
            f"{matrix_a.shape[0]}x{matrix_a.shape[1]} × {matrix_b.shape[0]}x{matrix_b.shape[1]}"
        )


def _validate_same_dimensions(matrix_a: np.ndarray, matrix_b: np.ndarray, operation: str) -> None:
    """Validate that two matrices have the same dimensions."""
    if matrix_a.shape != matrix_b.shape:
        raise MatrixError(
            f"Matrices must have same dimensions for {operation}: "
            f"{matrix_a.shape} vs {matrix_b.shape}"
        )


def _matrix_to_list(matrix: np.ndarray) -> List[List[float]]:
    """Convert numpy array to list of lists."""
    return matrix.tolist()


# Basic Matrix Arithmetic
def matrix_add(matrix_a: List[List[Union[float, int]]], 
               matrix_b: List[List[Union[float, int]]]) -> Dict[str, Any]:
    """Add two matrices element-wise."""
    try:
        np_a = _validate_matrix(matrix_a, "matrix_a")
        np_b = _validate_matrix(matrix_b, "matrix_b")
        
        _validate_same_dimensions(np_a, np_b, "addition")
        
        result = np_a + np_b
        
        return {
            "result": _matrix_to_list(result),
            "dimensions": result.shape,
            "operation": "matrix_addition"
        }
        
    except Exception as e:
        raise MatrixError(f"Error in matrix addition: {e}") from e


def matrix_subtract(matrix_a: List[List[Union[float, int]]], 
                   matrix_b: List[List[Union[float, int]]]) -> Dict[str, Any]:
    """Subtract matrix_b from matrix_a element-wise."""
    try:
        np_a = _validate_matrix(matrix_a, "matrix_a")
        np_b = _validate_matrix(matrix_b, "matrix_b")
        
        _validate_same_dimensions(np_a, np_b, "subtraction")
        
        result = np_a - np_b
        
        return {
            "result": _matrix_to_list(result),
            "dimensions": result.shape,
            "operation": "matrix_subtraction"
        }
        
    except Exception as e:
        raise MatrixError(f"Error in matrix subtraction: {e}") from e


def matrix_multiply(matrix_a: List[List[Union[float, int]]], 
                   matrix_b: List[List[Union[float, int]]]) -> Dict[str, Any]:
    """Multiply two matrices using matrix multiplication."""
    try:
        np_a = _validate_matrix(matrix_a, "matrix_a")
        np_b = _validate_matrix(matrix_b, "matrix_b")
        
        _validate_compatible_for_multiplication(np_a, np_b)
        
        result = np.dot(np_a, np_b)
        
        return {
            "result": _matrix_to_list(result),
            "dimensions": result.shape,
            "operation": "matrix_multiplication",
            "input_dimensions": {
                "matrix_a": np_a.shape,
                "matrix_b": np_b.shape
            }
        }
        
    except Exception as e:
        raise MatrixError(f"Error in matrix multiplication: {e}") from e


def matrix_scalar_multiply(matrix: List[List[Union[float, int]]], 
                          scalar: Union[float, int]) -> Dict[str, Any]:
    """Multiply a matrix by a scalar value."""
    try:
        np_matrix = _validate_matrix(matrix, "matrix")
        scalar_val = float(scalar)
        
        result = np_matrix * scalar_val
        
        return {
            "result": _matrix_to_list(result),
            "dimensions": result.shape,
            "scalar": scalar_val,
            "operation": "scalar_multiplication"
        }
        
    except Exception as e:
        raise MatrixError(f"Error in scalar multiplication: {e}") from e


# Matrix Properties and Operations
def matrix_transpose(matrix: List[List[Union[float, int]]]) -> Dict[str, Any]:
    """Calculate the transpose of a matrix."""
    try:
        np_matrix = _validate_matrix(matrix, "matrix")
        
        result = np_matrix.T
        
        return {
            "result": _matrix_to_list(result),
            "dimensions": result.shape,
            "original_dimensions": np_matrix.shape,
            "operation": "matrix_transpose"
        }
        
    except Exception as e:
        raise MatrixError(f"Error in matrix transpose: {e}") from e


def matrix_determinant(matrix: List[List[Union[float, int]]]) -> Dict[str, Any]:
    """Calculate the determinant of a square matrix."""
    try:
        np_matrix = _validate_matrix(matrix, "matrix")
        _validate_square_matrix(np_matrix, "matrix")
        
        det = np.linalg.det(np_matrix)
        
        # Handle very small determinants (likely numerical errors)
        if abs(det) < 1e-15:
            det = 0.0
        
        return {
            "result": float(det),
            "dimensions": np_matrix.shape,
            "operation": "matrix_determinant",
            "is_singular": abs(det) < 1e-10
        }
        
    except LinAlgError as e:
        raise MatrixError(f"Linear algebra error calculating determinant: {e}") from e
    except Exception as e:
        raise MatrixError(f"Error calculating determinant: {e}") from e


def matrix_trace(matrix: List[List[Union[float, int]]]) -> Dict[str, Any]:
    """Calculate the trace (sum of diagonal elements) of a square matrix."""
    try:
        np_matrix = _validate_matrix(matrix, "matrix")
        _validate_square_matrix(np_matrix, "matrix")
        
        trace = np.trace(np_matrix)
        
        return {
            "result": float(trace),
            "dimensions": np_matrix.shape,
            "operation": "matrix_trace"
        }
        
    except Exception as e:
        raise MatrixError(f"Error calculating trace: {e}") from e


def matrix_rank(matrix: List[List[Union[float, int]]]) -> Dict[str, Any]:
    """Calculate the rank of a matrix."""
    try:
        np_matrix = _validate_matrix(matrix, "matrix")
        
        rank = np.linalg.matrix_rank(np_matrix)
        
        return {
            "result": int(rank),
            "dimensions": np_matrix.shape,
            "operation": "matrix_rank",
            "is_full_rank": rank == min(np_matrix.shape)
        }
        
    except Exception as e:
        raise MatrixError(f"Error calculating rank: {e}") from e


def matrix_norm(matrix: List[List[Union[float, int]]], 
                norm_type: str = "frobenius") -> Dict[str, Any]:
    """Calculate various norms of a matrix."""
    try:
        np_matrix = _validate_matrix(matrix, "matrix")
        
        # Map norm types to numpy parameters
        norm_map = {
            "frobenius": "fro",
            "fro": "fro",
            "nuclear": "nuc",
            "nuc": "nuc",
            "1": 1,
            "2": 2,
            "-1": -1,
            "-2": -2,
            "inf": np.inf,
            "infinity": np.inf,
            "-inf": -np.inf,
            "-infinity": -np.inf
        }
        
        if norm_type.lower() not in norm_map:
            available_norms = ', '.join(sorted(norm_map.keys()))
            raise ValidationError(f"Unknown norm type: {norm_type}. Available: {available_norms}")
        
        norm_param = norm_map[norm_type.lower()]
        norm_value = np.linalg.norm(np_matrix, ord=norm_param)
        
        return {
            "result": float(norm_value),
            "dimensions": np_matrix.shape,
            "norm_type": norm_type,
            "operation": "matrix_norm"
        }
        
    except Exception as e:
        raise MatrixError(f"Error calculating norm: {e}") from e


# Advanced Matrix Operations
def matrix_inverse(matrix: List[List[Union[float, int]]]) -> Dict[str, Any]:
    """Calculate the inverse of a square matrix."""
    try:
        np_matrix = _validate_matrix(matrix, "matrix")
        _validate_square_matrix(np_matrix, "matrix")
        
        # Check if matrix is singular
        det = np.linalg.det(np_matrix)
        if abs(det) < 1e-10:
            raise MatrixError("Matrix is singular (determinant ≈ 0) and cannot be inverted")
        
        inverse = np.linalg.inv(np_matrix)
        
        return {
            "result": _matrix_to_list(inverse),
            "dimensions": inverse.shape,
            "determinant": float(det),
            "operation": "matrix_inverse"
        }
        
    except LinAlgError as e:
        raise MatrixError(f"Matrix is not invertible: {e}") from e
    except Exception as e:
        raise MatrixError(f"Error calculating inverse: {e}") from e


def matrix_pseudoinverse(matrix: List[List[Union[float, int]]]) -> Dict[str, Any]:
    """Calculate the Moore-Penrose pseudoinverse of a matrix."""
    try:
        np_matrix = _validate_matrix(matrix, "matrix")
        
        pinv = np.linalg.pinv(np_matrix)
        
        return {
            "result": _matrix_to_list(pinv),
            "dimensions": pinv.shape,
            "original_dimensions": np_matrix.shape,
            "operation": "matrix_pseudoinverse"
        }
        
    except Exception as e:
        raise MatrixError(f"Error calculating pseudoinverse: {e}") from e


def matrix_eigenvalues(matrix: List[List[Union[float, int]]]) -> Dict[str, Any]:
    """Calculate eigenvalues and eigenvectors of a square matrix."""
    try:
        np_matrix = _validate_matrix(matrix, "matrix")
        _validate_square_matrix(np_matrix, "matrix")
        
        eigenvalues, eigenvectors = np.linalg.eig(np_matrix)
        
        # Handle complex eigenvalues
        if np.iscomplexobj(eigenvalues):
            eigenvalues_list = [{"real": float(val.real), "imag": float(val.imag)} 
                               for val in eigenvalues]
        else:
            eigenvalues_list = [float(val) for val in eigenvalues]
        
        return {
            "eigenvalues": eigenvalues_list,
            "eigenvectors": _matrix_to_list(eigenvectors.real) if not np.iscomplexobj(eigenvectors) else _matrix_to_list(eigenvectors),
            "dimensions": np_matrix.shape,
            "operation": "matrix_eigenvalues",
            "has_complex_eigenvalues": np.iscomplexobj(eigenvalues)
        }
        
    except LinAlgError as e:
        raise MatrixError(f"Error calculating eigenvalues: {e}") from e
    except Exception as e:
        raise MatrixError(f"Error calculating eigenvalues: {e}") from e


def matrix_svd(matrix: List[List[Union[float, int]]]) -> Dict[str, Any]:
    """Calculate Singular Value Decomposition (SVD) of a matrix."""
    try:
        np_matrix = _validate_matrix(matrix, "matrix")
        
        U, s, Vt = np.linalg.svd(np_matrix)
        
        return {
            "U": _matrix_to_list(U),
            "singular_values": s.tolist(),
            "Vt": _matrix_to_list(Vt),
            "dimensions": np_matrix.shape,
            "operation": "matrix_svd",
            "rank": int(np.sum(s > 1e-10))  # Numerical rank
        }
        
    except LinAlgError as e:
        raise MatrixError(f"Error calculating SVD: {e}") from e
    except Exception as e:
        raise MatrixError(f"Error calculating SVD: {e}") from e


def matrix_qr_decomposition(matrix: List[List[Union[float, int]]]) -> Dict[str, Any]:
    """Calculate QR decomposition of a matrix."""
    try:
        np_matrix = _validate_matrix(matrix, "matrix")
        
        Q, R = np.linalg.qr(np_matrix)
        
        return {
            "Q": _matrix_to_list(Q),
            "R": _matrix_to_list(R),
            "dimensions": np_matrix.shape,
            "operation": "matrix_qr_decomposition"
        }
        
    except LinAlgError as e:
        raise MatrixError(f"Error calculating QR decomposition: {e}") from e
    except Exception as e:
        raise MatrixError(f"Error calculating QR decomposition: {e}") from e


def matrix_lu_decomposition(matrix: List[List[Union[float, int]]]) -> Dict[str, Any]:
    """Calculate LU decomposition of a square matrix."""
    try:
        from scipy.linalg import lu
        
        np_matrix = _validate_matrix(matrix, "matrix")
        _validate_square_matrix(np_matrix, "matrix")
        
        P, L, U = lu(np_matrix)
        
        return {
            "P": _matrix_to_list(P),
            "L": _matrix_to_list(L),
            "U": _matrix_to_list(U),
            "dimensions": np_matrix.shape,
            "operation": "matrix_lu_decomposition"
        }
        
    except ImportError:
        raise MatrixError("SciPy is required for LU decomposition")
    except Exception as e:
        raise MatrixError(f"Error calculating LU decomposition: {e}") from e


# System of Linear Equations
def solve_linear_system(coefficient_matrix: List[List[Union[float, int]]], 
                       constants: List[Union[float, int]]) -> Dict[str, Any]:
    """Solve a system of linear equations Ax = b."""
    try:
        A = _validate_matrix(coefficient_matrix, "coefficient_matrix")
        b = np.array(constants, dtype=float)
        
        if len(b) != A.shape[0]:
            raise ValidationError(
                f"Constants vector length ({len(b)}) must match number of equations ({A.shape[0]})"
            )
        
        # Check if system is solvable
        rank_A = np.linalg.matrix_rank(A)
        rank_Ab = np.linalg.matrix_rank(np.column_stack([A, b]))
        
        if rank_A != rank_Ab:
            raise MatrixError("System of equations is inconsistent (no solution)")
        
        if rank_A < A.shape[1] or A.shape[0] != A.shape[1]:
            # Underdetermined or overdetermined system - use least squares solution
            solution = np.linalg.lstsq(A, b, rcond=None)[0]
            solution_type = "least_squares"
        else:
            # Square determined system
            solution = np.linalg.solve(A, b)
            solution_type = "exact"
        
        # Verify solution
        residual = np.linalg.norm(A @ solution - b)
        
        return {
            "solution": solution.tolist(),
            "solution_type": solution_type,
            "residual": float(residual),
            "rank": int(rank_A),
            "dimensions": A.shape,
            "operation": "solve_linear_system",
            "is_well_conditioned": residual < 1e-10
        }
        
    except LinAlgError as e:
        raise MatrixError(f"Error solving linear system: {e}") from e
    except Exception as e:
        raise MatrixError(f"Error solving linear system: {e}") from e


def matrix_condition_number(matrix: List[List[Union[float, int]]], 
                           norm_type: str = "2") -> Dict[str, Any]:
    """Calculate the condition number of a matrix."""
    try:
        np_matrix = _validate_matrix(matrix, "matrix")
        
        # Map norm types
        norm_map = {
            "1": 1,
            "2": 2,
            "frobenius": "fro",
            "fro": "fro",
            "inf": np.inf,
            "infinity": np.inf
        }
        
        if norm_type.lower() not in norm_map:
            available_norms = ', '.join(sorted(norm_map.keys()))
            raise ValidationError(f"Unknown norm type: {norm_type}. Available: {available_norms}")
        
        norm_param = norm_map[norm_type.lower()]
        cond_num = np.linalg.cond(np_matrix, p=norm_param)
        
        # Interpret condition number
        if cond_num < 1e12:
            conditioning = "well_conditioned"
        elif cond_num < 1e16:
            conditioning = "moderately_conditioned"
        else:
            conditioning = "ill_conditioned"
        
        return {
            "condition_number": float(cond_num),
            "norm_type": norm_type,
            "conditioning": conditioning,
            "dimensions": np_matrix.shape,
            "operation": "matrix_condition_number"
        }
        
    except Exception as e:
        raise MatrixError(f"Error calculating condition number: {e}") from e


# Utility Functions
def create_identity_matrix(size: int) -> Dict[str, Any]:
    """Create an identity matrix of specified size."""
    try:
        if not isinstance(size, int) or size < 1:
            raise ValidationError("Size must be a positive integer")
        
        if size > 1000:
            raise ValidationError("Matrix size too large (maximum 1000)")
        
        identity = np.eye(size)
        
        return {
            "result": _matrix_to_list(identity),
            "dimensions": (size, size),
            "operation": "create_identity_matrix"
        }
        
    except Exception as e:
        raise MatrixError(f"Error creating identity matrix: {e}") from e


def create_zero_matrix(rows: int, cols: int) -> Dict[str, Any]:
    """Create a zero matrix of specified dimensions."""
    try:
        if not isinstance(rows, int) or not isinstance(cols, int) or rows < 1 or cols < 1:
            raise ValidationError("Rows and columns must be positive integers")
        
        if rows > 1000 or cols > 1000:
            raise ValidationError("Matrix size too large (maximum 1000x1000)")
        
        zero_matrix = np.zeros((rows, cols))
        
        return {
            "result": _matrix_to_list(zero_matrix),
            "dimensions": (rows, cols),
            "operation": "create_zero_matrix"
        }
        
    except Exception as e:
        raise MatrixError(f"Error creating zero matrix: {e}") from e


def is_matrix_symmetric(matrix: List[List[Union[float, int]]]) -> Dict[str, Any]:
    """Check if a matrix is symmetric."""
    try:
        np_matrix = _validate_matrix(matrix, "matrix")
        _validate_square_matrix(np_matrix, "matrix")
        
        is_symmetric = np.allclose(np_matrix, np_matrix.T, rtol=1e-10, atol=1e-10)
        
        return {
            "is_symmetric": bool(is_symmetric),
            "dimensions": np_matrix.shape,
            "operation": "check_matrix_symmetry"
        }
        
    except Exception as e:
        raise MatrixError(f"Error checking matrix symmetry: {e}") from e


def is_matrix_orthogonal(matrix: List[List[Union[float, int]]]) -> Dict[str, Any]:
    """Check if a matrix is orthogonal (A * A^T = I)."""
    try:
        np_matrix = _validate_matrix(matrix, "matrix")
        _validate_square_matrix(np_matrix, "matrix")
        
        product = np.dot(np_matrix, np_matrix.T)
        identity = np.eye(np_matrix.shape[0])
        
        is_orthogonal = np.allclose(product, identity, rtol=1e-10, atol=1e-10)
        
        return {
            "is_orthogonal": bool(is_orthogonal),
            "dimensions": np_matrix.shape,
            "operation": "check_matrix_orthogonality"
        }
        
    except Exception as e:
        raise MatrixError(f"Error checking matrix orthogonality: {e}") from e