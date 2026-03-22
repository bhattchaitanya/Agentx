"""Matrix tools: arithmetic, decomposition, solving linear systems."""

import numpy as np


def _parse_matrix(data: list[list[float]]) -> np.ndarray:
    return np.array(data, dtype=float)


def matrix_add(a: list[list[float]], b: list[list[float]]) -> str:
    """Add two matrices element-wise."""
    result = _parse_matrix(a) + _parse_matrix(b)
    return _fmt(result)


def matrix_subtract(a: list[list[float]], b: list[list[float]]) -> str:
    """Subtract matrix b from matrix a element-wise."""
    result = _parse_matrix(a) - _parse_matrix(b)
    return _fmt(result)


def matrix_multiply(a: list[list[float]], b: list[list[float]]) -> str:
    """Multiply two matrices (standard matrix product)."""
    result = _parse_matrix(a) @ _parse_matrix(b)
    return _fmt(result)


def matrix_scalar_multiply(matrix: list[list[float]], scalar: float) -> str:
    """Multiply every element of a matrix by a scalar."""
    result = _parse_matrix(matrix) * scalar
    return _fmt(result)


def matrix_transpose(matrix: list[list[float]]) -> str:
    """Return the transpose of a matrix."""
    result = _parse_matrix(matrix).T
    return _fmt(result)


def matrix_determinant(matrix: list[list[float]]) -> str:
    """Compute the determinant of a square matrix."""
    m = _parse_matrix(matrix)
    if m.shape[0] != m.shape[1]:
        raise ValueError("Determinant requires a square matrix.")
    det = np.linalg.det(m)
    return str(round(det, 10))


def matrix_inverse(matrix: list[list[float]]) -> str:
    """Compute the inverse of a square matrix. Raises ValueError if singular."""
    m = _parse_matrix(matrix)
    if m.shape[0] != m.shape[1]:
        raise ValueError("Inverse requires a square matrix.")
    det = np.linalg.det(m)
    if abs(det) < 1e-12:
        raise ValueError("Matrix is singular (determinant ≈ 0); inverse does not exist.")
    result = np.linalg.inv(m)
    return _fmt(result)


def matrix_eigenvalues(matrix: list[list[float]]) -> str:
    """Return the eigenvalues of a square matrix."""
    m = _parse_matrix(matrix)
    if m.shape[0] != m.shape[1]:
        raise ValueError("Eigenvalues require a square matrix.")
    vals = np.linalg.eigvals(m)
    # Round small imaginary parts to zero
    if np.all(np.abs(vals.imag) < 1e-10):
        vals = vals.real
    rounded = [round(float(v), 8) for v in vals]
    return str(rounded)


def matrix_rank(matrix: list[list[float]]) -> str:
    """Return the rank of a matrix."""
    return str(int(np.linalg.matrix_rank(_parse_matrix(matrix))))


def solve_linear_system(a: list[list[float]], b: list[float]) -> str:
    """
    Solve the linear system Ax = b.
    a is the coefficient matrix, b is the right-hand side vector.
    """
    A = _parse_matrix(a)
    B = np.array(b, dtype=float)
    if np.linalg.matrix_rank(A) < A.shape[0]:
        raise ValueError("System has no unique solution (matrix is singular or under-determined).")
    x = np.linalg.solve(A, B)
    return _fmt_vec(x)


def _fmt(m: np.ndarray, decimals: int = 8) -> str:
    """Format a 2-D ndarray as a nested Python list string."""
    rounded = np.round(m, decimals)
    # Remove -0.0
    rounded = rounded + 0.0
    return str(rounded.tolist())


def _fmt_vec(v: np.ndarray, decimals: int = 8) -> str:
    rounded = np.round(v, decimals) + 0.0
    return str(rounded.tolist())


# Tool definitions for the Claude API
MATRIX_TOOLS = [
    {
        "name": "matrix_add",
        "description": "Add two matrices element-wise. Both must have the same dimensions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "a": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}, "description": "First matrix (list of rows)"},
                "b": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}, "description": "Second matrix (list of rows)"},
            },
            "required": ["a", "b"],
        },
    },
    {
        "name": "matrix_subtract",
        "description": "Subtract matrix b from matrix a element-wise.",
        "input_schema": {
            "type": "object",
            "properties": {
                "a": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}, "description": "First matrix"},
                "b": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}, "description": "Second matrix"},
            },
            "required": ["a", "b"],
        },
    },
    {
        "name": "matrix_multiply",
        "description": "Compute the matrix product A × B (standard dot product, not element-wise).",
        "input_schema": {
            "type": "object",
            "properties": {
                "a": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}, "description": "Left matrix"},
                "b": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}, "description": "Right matrix"},
            },
            "required": ["a", "b"],
        },
    },
    {
        "name": "matrix_scalar_multiply",
        "description": "Multiply every element of a matrix by a scalar.",
        "input_schema": {
            "type": "object",
            "properties": {
                "matrix": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}, "description": "The matrix"},
                "scalar": {"type": "number", "description": "Scalar multiplier"},
            },
            "required": ["matrix", "scalar"],
        },
    },
    {
        "name": "matrix_transpose",
        "description": "Return the transpose of a matrix.",
        "input_schema": {
            "type": "object",
            "properties": {
                "matrix": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}, "description": "Matrix to transpose"},
            },
            "required": ["matrix"],
        },
    },
    {
        "name": "matrix_determinant",
        "description": "Compute the determinant of a square matrix.",
        "input_schema": {
            "type": "object",
            "properties": {
                "matrix": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}, "description": "Square matrix"},
            },
            "required": ["matrix"],
        },
    },
    {
        "name": "matrix_inverse",
        "description": "Compute the inverse of a square, non-singular matrix.",
        "input_schema": {
            "type": "object",
            "properties": {
                "matrix": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}, "description": "Square invertible matrix"},
            },
            "required": ["matrix"],
        },
    },
    {
        "name": "matrix_eigenvalues",
        "description": "Return the eigenvalues of a square matrix.",
        "input_schema": {
            "type": "object",
            "properties": {
                "matrix": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}, "description": "Square matrix"},
            },
            "required": ["matrix"],
        },
    },
    {
        "name": "matrix_rank",
        "description": "Return the rank of a matrix.",
        "input_schema": {
            "type": "object",
            "properties": {
                "matrix": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}, "description": "Matrix"},
            },
            "required": ["matrix"],
        },
    },
    {
        "name": "solve_linear_system",
        "description": "Solve the linear system Ax = b for x, given coefficient matrix A and vector b.",
        "input_schema": {
            "type": "object",
            "properties": {
                "a": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}, "description": "Coefficient matrix A"},
                "b": {"type": "array", "items": {"type": "number"}, "description": "Right-hand side vector b"},
            },
            "required": ["a", "b"],
        },
    },
]

MATRIX_TOOL_FUNCTIONS = {
    "matrix_add": matrix_add,
    "matrix_subtract": matrix_subtract,
    "matrix_multiply": matrix_multiply,
    "matrix_scalar_multiply": matrix_scalar_multiply,
    "matrix_transpose": matrix_transpose,
    "matrix_determinant": matrix_determinant,
    "matrix_inverse": matrix_inverse,
    "matrix_eigenvalues": matrix_eigenvalues,
    "matrix_rank": matrix_rank,
    "solve_linear_system": solve_linear_system,
}
