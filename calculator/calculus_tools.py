"""Calculus tools: differentiation, integration, limits, series."""

import sympy as sp


def _parse_expr(expr_str: str, var: str = "x") -> tuple[sp.Expr, sp.Symbol]:
    """Parse a string expression into a sympy Expr and Symbol."""
    sym = sp.Symbol(var)
    fns = [sp.sin, sp.cos, sp.tan, sp.exp, sp.log, sp.sqrt,
           sp.asin, sp.acos, sp.atan, sp.sinh, sp.cosh, sp.tanh]
    local = {
        var: sym,
        **{f.__name__: f for f in fns},
        "pi": sp.pi,
        "E":  sp.E,
        "oo": sp.oo,
    }
    return sp.sympify(expr_str, locals=local), sym


def differentiate(expression: str, variable: str = "x", order: int = 1) -> str:
    """Differentiate expression with respect to variable."""
    expr, var = _parse_expr(expression, variable)
    result = sp.diff(expr, var, order)
    return str(sp.simplify(result))


def integrate(
    expression: str,
    variable: str = "x",
    lower: float | None = None,
    upper: float | None = None,
) -> str:
    """
    Integrate expression. If lower/upper are provided, compute a definite integral;
    otherwise compute the indefinite integral (no constant of integration).
    """
    expr, var = _parse_expr(expression, variable)
    if lower is not None and upper is not None:
        result = sp.integrate(expr, (var, lower, upper))
    else:
        result = sp.integrate(expr, var)
    return str(sp.simplify(result))


def limit(expression: str, variable: str = "x", point: str = "0", direction: str = "+-") -> str:
    """
    Compute the limit of expression as variable -> point.
    direction: '+' (from right), '-' (from left), '+-' (two-sided, default).
    """
    expr, var = _parse_expr(expression, variable)
    pt = sp.sympify(point)
    result = sp.limit(expr, var, pt, dir=direction)
    return str(result)


def taylor_series(expression: str, variable: str = "x", point: float = 0, order: int = 5) -> str:
    """Compute the Taylor series of expression around point up to given order."""
    expr, var = _parse_expr(expression, variable)
    series = sp.series(expr, var, point, order + 1).removeO()
    return str(sp.expand(series))


# Tool definitions for Claude API
CALCULUS_TOOLS = [
    {
        "name": "differentiate",
        "description": (
            "Differentiate a mathematical expression with respect to a variable. "
            "Supports polynomial, trigonometric, exponential, and logarithmic functions. "
            "Use standard Python/sympy notation: x**2 for x², exp(x) for e^x, log(x) for ln(x)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Expression to differentiate, e.g. 'x**3 + sin(x)'"},
                "variable":   {"type": "string", "description": "Variable to differentiate with respect to (default: x)", "default": "x"},
                "order":      {"type": "integer", "description": "Order of differentiation (default: 1)", "default": 1},
            },
            "required": ["expression"],
        },
    },
    {
        "name": "integrate",
        "description": (
            "Integrate a mathematical expression. For a definite integral supply lower and upper bounds; "
            "otherwise returns the indefinite integral. "
            "Use standard notation: x**2, sin(x), exp(x), log(x), pi, E."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Expression to integrate, e.g. 'x**2 + cos(x)'"},
                "variable":   {"type": "string", "description": "Variable of integration (default: x)", "default": "x"},
                "lower":      {"type": "number", "description": "Lower bound (omit for indefinite integral)"},
                "upper":      {"type": "number", "description": "Upper bound (omit for indefinite integral)"},
            },
            "required": ["expression"],
        },
    },
    {
        "name": "limit",
        "description": (
            "Compute the limit of a mathematical expression as a variable approaches a point. "
            "Point can be a number or 'oo' for infinity, '-oo' for negative infinity."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Expression to evaluate the limit of"},
                "variable":   {"type": "string", "description": "Variable (default: x)", "default": "x"},
                "point":      {"type": "string", "description": "Point to approach, e.g. '0', 'oo', '-oo', 'pi'", "default": "0"},
                "direction":  {"type": "string", "description": "Direction: '+' (right), '-' (left), '+-' (two-sided, default)", "default": "+-"},
            },
            "required": ["expression", "point"],
        },
    },
    {
        "name": "taylor_series",
        "description": "Compute the Taylor series expansion of an expression around a point.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Expression to expand"},
                "variable":   {"type": "string", "description": "Variable (default: x)", "default": "x"},
                "point":      {"type": "number", "description": "Center of expansion (default: 0)", "default": 0},
                "order":      {"type": "integer", "description": "Order of expansion (default: 5)", "default": 5},
            },
            "required": ["expression"],
        },
    },
]

CALCULUS_TOOL_FUNCTIONS = {
    "differentiate": differentiate,
    "integrate": integrate,
    "limit": limit,
    "taylor_series": taylor_series,
}
