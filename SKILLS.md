# Skills Reference

The calculator agent supports three skill sets. Pass `skill=` when constructing `CalculatorAgent`, or use `"all"` (default) to load every tool.

```python
from calculator.agent import CalculatorAgent

agent = CalculatorAgent(skill="arithmetic")  # basic ops only
agent = CalculatorAgent(skill="calculus")    # + calculus tools
agent = CalculatorAgent(skill="matrices")    # + matrix tools
agent = CalculatorAgent(skill="all")         # everything (default)
```

---

## Arithmetic

**Module:** `calculator/tools.py`
**Backed by:** Python `math` / `operator` stdlib

| Tool | Description | Example |
|------|-------------|---------|
| `add` | a + b | `add(3, 5)` → `8` |
| `subtract` | a − b | `subtract(10, 4)` → `6` |
| `multiply` | a × b | `multiply(6, 7)` → `42` |
| `divide` | a ÷ b | `divide(20, 4)` → `5.0` |
| `power` | baseᵉˣᵖ | `power(2, 10)` → `1024.0` |
| `sqrt` | √n | `sqrt(144)` → `12.0` |
| `modulo` | a % b | `modulo(17, 5)` → `2.0` |

---

## Calculus

**Module:** `calculator/calculus_tools.py`
**Backed by:** [SymPy](https://www.sympy.org)

Use standard Python/SymPy notation in expressions:

| Notation | Meaning |
|----------|---------|
| `x**2` | x² |
| `sin(x)`, `cos(x)`, `tan(x)` | trig functions |
| `exp(x)` | eˣ |
| `log(x)` | ln(x) |
| `sqrt(x)` | √x |
| `pi`, `E`, `oo` | π, e, ∞ |

### Tools

#### `differentiate`

```
differentiate(expression, variable="x", order=1)
```

Symbolically differentiates `expression` w.r.t. `variable`.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `expression` | string | — | Expression to differentiate |
| `variable` | string | `"x"` | Variable |
| `order` | integer | `1` | Derivative order |

**Examples:**
- `"Differentiate x**3 + sin(x)"` → `3*x**2 + cos(x)`
- `"Second derivative of x**4"` → `12*x**2`

---

#### `integrate`

```
integrate(expression, variable="x", lower=None, upper=None)
```

Computes the indefinite or definite integral.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `expression` | string | — | Expression to integrate |
| `variable` | string | `"x"` | Variable of integration |
| `lower` | number | `None` | Lower bound (definite) |
| `upper` | number | `None` | Upper bound (definite) |

**Examples:**
- `"Integrate x**2"` → `x**3/3`
- `"Definite integral of x**2 from 0 to 3"` → `9`

---

#### `limit`

```
limit(expression, variable="x", point="0", direction="+-")
```

Computes the limit of `expression` as `variable → point`.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `expression` | string | — | Expression |
| `variable` | string | `"x"` | Variable |
| `point` | string | `"0"` | Approach point (`"0"`, `"oo"`, `"-oo"`, `"pi"`, …) |
| `direction` | string | `"+-"` | `"+"` right, `"-"` left, `"+-"` two-sided |

**Examples:**
- `"Limit of sin(x)/x as x→0"` → `1`
- `"Limit of 1/x as x→∞"` → `0`

---

#### `taylor_series`

```
taylor_series(expression, variable="x", point=0, order=5)
```

Expands `expression` as a Taylor series around `point`.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `expression` | string | — | Expression to expand |
| `variable` | string | `"x"` | Variable |
| `point` | number | `0` | Centre of expansion |
| `order` | integer | `5` | Highest power to include |

**Example:**
- `"Taylor series of exp(x) around 0 order 4"` → `x**4/24 + x**3/6 + x**2/2 + x + 1`

---

## Matrices

**Module:** `calculator/matrix_tools.py`
**Backed by:** [NumPy](https://numpy.org)

Matrices are passed as nested lists (list of rows):

```
[[1, 2],
 [3, 4]]
```

### Tools

| Tool | Description | Notes |
|------|-------------|-------|
| `matrix_add` | A + B element-wise | Same dimensions required |
| `matrix_subtract` | A − B element-wise | Same dimensions required |
| `matrix_multiply` | A × B (dot product) | Inner dimensions must match |
| `matrix_scalar_multiply` | scalar × A | |
| `matrix_transpose` | Aᵀ | |
| `matrix_determinant` | det(A) | Square matrix only |
| `matrix_inverse` | A⁻¹ | Square, non-singular only |
| `matrix_eigenvalues` | eigenvalues of A | Square matrix only |
| `matrix_rank` | rank(A) | |
| `solve_linear_system` | Solve Ax = b | Square, non-singular A |

**Examples:**
- `"Multiply [[1,2],[3,4]] by [[2,0],[1,3]]"` → `[[4, 6], [10, 12]]`
- `"Determinant of [[3,8],[4,6]]"` → `-14.0`
- `"Eigenvalues of [[2,1],[1,2]]"` → `[3.0, 1.0]`
- `"Solve 2x + y = 5, x + 3y = 10"` → `[1.0, 3.0]`

---

## Adding a New Skill

1. Create `calculator/<skill>_tools.py` with tool functions, `<SKILL>_TOOLS` list, and `<SKILL>_TOOL_FUNCTIONS` dict.
2. Import and register the functions in `calculator/tools.py` → `execute_tool()`.
3. Add the skill to `_SKILL_TOOLS` and `_SKILL_PROMPTS` in `calculator/agent.py`.
4. Extend `InputGuardrail.MATH_SIGNAL_PATTERN` with relevant keywords.
5. Add eval cases to `evals/eval_cases.py` and include them in `ALL_CASES`.
