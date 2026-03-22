"""Calculator tools for use with Claude API."""

import math
import operator
from typing import Any


def add(a: float, b: float) -> float:
    """Add two numbers."""
    return operator.add(a, b)


def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    return operator.sub(a, b)


def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return operator.mul(a, b)


def divide(a: float, b: float) -> float:
    """Divide a by b. Raises ValueError if b is zero."""
    if b == 0:
        raise ValueError("Division by zero is not allowed.")
    return operator.truediv(a, b)


def power(base: float, exponent: float) -> float:
    """Raise base to the power of exponent."""
    return math.pow(base, exponent)


def sqrt(n: float) -> float:
    """Return the square root of n. Raises ValueError for negative numbers."""
    if n < 0:
        raise ValueError(f"Cannot take square root of negative number: {n}")
    return math.sqrt(n)


def modulo(a: float, b: float) -> float:
    """Return a modulo b. Raises ValueError if b is zero."""
    if b == 0:
        raise ValueError("Modulo by zero is not allowed.")
    return a % b


# Tool definitions for the Claude API
CALCULATOR_TOOLS = [
    {
        "name": "add",
        "description": "Add two numbers together.",
        "input_schema": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "First operand"},
                "b": {"type": "number", "description": "Second operand"},
            },
            "required": ["a", "b"],
        },
    },
    {
        "name": "subtract",
        "description": "Subtract the second number from the first.",
        "input_schema": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "Minuend"},
                "b": {"type": "number", "description": "Subtrahend"},
            },
            "required": ["a", "b"],
        },
    },
    {
        "name": "multiply",
        "description": "Multiply two numbers together.",
        "input_schema": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "First factor"},
                "b": {"type": "number", "description": "Second factor"},
            },
            "required": ["a", "b"],
        },
    },
    {
        "name": "divide",
        "description": "Divide the first number by the second. Returns an error if dividing by zero.",
        "input_schema": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "Dividend"},
                "b": {"type": "number", "description": "Divisor (cannot be zero)"},
            },
            "required": ["a", "b"],
        },
    },
    {
        "name": "power",
        "description": "Raise a base number to an exponent.",
        "input_schema": {
            "type": "object",
            "properties": {
                "base": {"type": "number", "description": "The base number"},
                "exponent": {"type": "number", "description": "The exponent"},
            },
            "required": ["base", "exponent"],
        },
    },
    {
        "name": "sqrt",
        "description": "Compute the square root of a non-negative number.",
        "input_schema": {
            "type": "object",
            "properties": {
                "n": {"type": "number", "description": "Non-negative number"},
            },
            "required": ["n"],
        },
    },
    {
        "name": "modulo",
        "description": "Compute the remainder of dividing a by b.",
        "input_schema": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "Dividend"},
                "b": {"type": "number", "description": "Divisor (cannot be zero)"},
            },
            "required": ["a", "b"],
        },
    },
]

# Dispatch table
TOOL_FUNCTIONS: dict[str, Any] = {
    "add": add,
    "subtract": subtract,
    "multiply": multiply,
    "divide": divide,
    "power": power,
    "sqrt": sqrt,
    "modulo": modulo,
}


def execute_tool(name: str, inputs: dict) -> str:
    """Execute a calculator tool by name and return its result as a string."""
    from calculator.calculus_tools import CALCULUS_TOOL_FUNCTIONS
    from calculator.matrix_tools import MATRIX_TOOL_FUNCTIONS

    all_fns = {**TOOL_FUNCTIONS, **CALCULUS_TOOL_FUNCTIONS, **MATRIX_TOOL_FUNCTIONS}
    fn = all_fns.get(name)
    if fn is None:
        return f"Unknown tool: {name}"
    try:
        result = fn(**inputs)
        return str(result)
    except (ValueError, ZeroDivisionError, Exception) as e:
        return f"Error: {e}"
