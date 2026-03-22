# Calculator Agent — Template with Guardrails & Evals

A template project demonstrating how to build a Claude-powered calculator agent with **input/output guardrails** and an **evaluation framework**.

## Project Structure

```
.
├── calculator/
│   ├── agent.py        # CalculatorAgent — agentic tool-use loop
│   └── tools.py        # Tool definitions + dispatch table
├── guardrails/
│   ├── input_guardrail.py   # Validate/block incoming requests
│   └── output_guardrail.py  # Validate model outputs before returning
├── evals/
│   ├── eval_cases.py   # Test cases (basic, advanced, edge, guardrail)
│   └── runner.py       # Eval runner + reporting
├── main.py             # Entry point (interactive / --eval / --solve)
└── requirements.txt
```

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here
```

## Usage

### Interactive mode

```bash
python main.py
```

### Solve a single problem

```bash
python main.py --solve "What is the square root of 256?"
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
- Don't appear to be math problems

### Output Guardrail (`guardrails/output_guardrail.py`)

Blocks responses that:
- Are empty
- Exceed 2,000 characters (hallucination signal)
- Contain leaked system-prompt fragments
- Don't include a numeric answer

## Evals

Test cases are organised into four groups:

| Group | Cases | Purpose |
|-------|-------|---------|
| `basic` | 6 | Core arithmetic (+, -, ×, ÷, %, mod) |
| `advanced` | 4 | Power, sqrt, chained, multi-step |
| `edge` | 4 | Zero, negatives, large numbers, floats |
| `guardrail` | 5 | Inputs that should be blocked |

The runner extracts the numeric answer from the model's response and compares it to the expected value within a configurable tolerance.

## Extending

- **Add a tool**: add a function in `calculator/tools.py`, add its schema to `CALCULATOR_TOOLS`, and register it in `TOOL_FUNCTIONS`.
- **Add an eval case**: add an `EvalCase` to the appropriate list in `evals/eval_cases.py`.
- **Tighten guardrails**: add patterns to `InputGuardrail.DISALLOWED_PATTERNS` or additional checks to `OutputGuardrail`.
