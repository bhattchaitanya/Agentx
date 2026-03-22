# Calculator Agent — Template with Guardrails & Evals

A template project demonstrating how to build a Claude-powered calculator agent with **input/output guardrails**, **multiple skill sets**, and an **evaluation framework**.

## Project Structure

```
.
├── calculator/
│   ├── agent.py             # CalculatorAgent — agentic tool-use loop + skill routing
│   ├── tools.py             # Arithmetic tool definitions + unified dispatch table
│   ├── calculus_tools.py    # Calculus tools (sympy): differentiate, integrate, limit, taylor
│   └── matrix_tools.py      # Matrix tools (numpy): multiply, inverse, eigenvalues, solve, …
├── guardrails/
│   ├── input_guardrail.py   # Validate/block incoming requests
│   └── output_guardrail.py  # Validate model outputs before returning
├── evals/
│   ├── eval_cases.py        # 35 test cases across 6 groups
│   └── runner.py            # Eval runner with per-tag reporting
├── main.py                  # Entry point (interactive / --eval / --solve)
├── SKILLS.md                # Full skills & tools reference
└── requirements.txt
```

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here
```

## Skills

The agent supports three skill sets. See **[SKILLS.md](SKILLS.md)** for the full reference.

| Skill | Tools | Backed by |
|-------|-------|-----------|
| `arithmetic` | add, subtract, multiply, divide, power, sqrt, modulo | stdlib |
| `calculus` | differentiate, integrate, limit, taylor_series | SymPy |
| `matrices` | matrix_add/subtract/multiply, determinant, inverse, eigenvalues, rank, solve | NumPy |
| `all` (default) | everything above | — |

```python
from calculator.agent import CalculatorAgent

agent = CalculatorAgent(skill="calculus")
result = agent.solve("Differentiate x**3 * sin(x)")

agent = CalculatorAgent(skill="matrices")
result = agent.solve("Find the eigenvalues of [[4,1],[2,3]]")
```

## Usage

### Interactive mode

```bash
python main.py
```

### Solve a single problem

```bash
python main.py --solve "What is the square root of 256?"
python main.py --solve "Integrate x**2 from 0 to 3"
python main.py --solve "Multiply [[1,2],[3,4]] by [[2,0],[1,3]]"
```

### Run evaluations

```bash
python main.py --eval
```

## Guardrails

### Input Guardrail (`guardrails/input_guardrail.py`)

Blocks requests that:
- Are empty
- Exceed 500 characters
- Contain prompt-injection patterns (e.g. "ignore previous instructions")
- Contain code-execution attempts (`eval`, `exec`, `import`, etc.)
- Don't appear to be a math problem (arithmetic, calculus, or matrix keywords)

### Output Guardrail (`guardrails/output_guardrail.py`)

Blocks responses that:
- Are empty
- Exceed 2,000 characters (hallucination signal)
- Contain leaked system-prompt fragments
- Don't include a numeric answer

## Evals

35 test cases across six groups:

| Group | Cases | Purpose |
|-------|-------|---------|
| `basic` | 6 | Core arithmetic (+, -, ×, ÷, %, mod) |
| `advanced` | 4 | Power, sqrt, chained, multi-step |
| `edge` | 4 | Zero, negatives, large numbers, floats |
| `guardrail` | 5 | Inputs that should be blocked |
| `calculus` | 8 | Differentiation, integration, limits, Taylor series |
| `matrices` | 8 | Matrix ops, determinant, eigenvalues, linear systems |

## Extending

See the **Adding a New Skill** section in [SKILLS.md](SKILLS.md).
