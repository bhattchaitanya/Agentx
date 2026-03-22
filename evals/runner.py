"""Evaluation runner for the calculator agent."""

import re
import time
from dataclasses import dataclass, field

from calculator.agent import CalculatorAgent
from evals.eval_cases import EvalCase, ALL_CASES


@dataclass
class EvalResult:
    case: EvalCase
    passed: bool
    actual_answer: str
    blocked: bool
    block_reason: str | None
    tool_calls: list[dict]
    error: str | None = None
    latency_ms: float = 0.0

    @property
    def extracted_number(self) -> float | None:
        """Try to extract the primary numeric answer from the response text."""
        matches = re.findall(r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?", self.actual_answer)
        if not matches:
            return None
        # Return the last number found (usually the final answer)
        return float(matches[-1])


@dataclass
class EvalSummary:
    results: list[EvalResult] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed(self) -> int:
        return self.total - self.passed

    @property
    def pass_rate(self) -> float:
        return self.passed / self.total if self.total else 0.0

    def by_tag(self, tag: str) -> "EvalSummary":
        return EvalSummary(
            results=[r for r in self.results if tag in r.case.tags]
        )

    def print_report(self) -> None:
        print(f"\n{'='*60}")
        print(f"  EVAL REPORT  |  {self.passed}/{self.total} passed  ({self.pass_rate:.1%})")
        print(f"{'='*60}")

        for r in self.results:
            status = "PASS" if r.passed else "FAIL"
            icon = "✓" if r.passed else "✗"
            latency = f"{r.latency_ms:.0f}ms"
            print(f"  {icon} [{status}] {r.case.name:<35} {latency}")
            if not r.passed:
                if r.error:
                    print(f"       Error: {r.error}")
                elif r.case.expect_blocked and not r.blocked:
                    print(f"       Expected blocked, got: {r.actual_answer!r}")
                elif r.blocked and not r.case.expect_blocked:
                    print(f"       Unexpectedly blocked: {r.block_reason}")
                elif r.case.expected_answer is not None:
                    extracted = r.extracted_number
                    print(
                        f"       Expected: {r.case.expected_answer}  "
                        f"Got: {extracted}  "
                        f"Response: {r.actual_answer!r}"
                    )

        # Per-tag breakdown
        tags = set(tag for r in self.results for tag in r.case.tags)
        if tags:
            print(f"\n  By tag:")
            for tag in sorted(tags):
                sub = self.by_tag(tag)
                print(f"    {tag:<20} {sub.passed}/{sub.total} ({sub.pass_rate:.1%})")

        print(f"{'='*60}\n")


def _evaluate_case(agent: CalculatorAgent, case: EvalCase) -> EvalResult:
    """Run a single eval case and return the result."""
    start = time.perf_counter()
    error = None

    try:
        response = agent.solve(case.prompt)
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return EvalResult(
            case=case,
            passed=False,
            actual_answer="",
            blocked=False,
            block_reason=None,
            tool_calls=[],
            error=str(exc),
            latency_ms=elapsed_ms,
        )

    elapsed_ms = (time.perf_counter() - start) * 1000
    actual_answer = response["answer"]
    blocked = response["blocked"]
    block_reason = response["block_reason"]
    tool_calls = response["tool_calls"]

    # Determine pass/fail
    if case.expect_blocked:
        passed = blocked
    elif blocked:
        # Unexpected block
        passed = False
    elif case.expected_answer is not None:
        # Extract numeric answer and compare
        result = EvalResult(
            case=case,
            passed=False,  # placeholder
            actual_answer=actual_answer,
            blocked=blocked,
            block_reason=block_reason,
            tool_calls=tool_calls,
            latency_ms=elapsed_ms,
        )
        extracted = result.extracted_number
        if extracted is None:
            passed = False
        else:
            passed = abs(extracted - case.expected_answer) <= case.tolerance
    else:
        # No expected answer specified — just check it didn't crash
        passed = True

    return EvalResult(
        case=case,
        passed=passed,
        actual_answer=actual_answer,
        blocked=blocked,
        block_reason=block_reason,
        tool_calls=tool_calls,
        error=error,
        latency_ms=elapsed_ms,
    )


def run_evals(
    cases: list[EvalCase] | None = None,
    agent: CalculatorAgent | None = None,
    verbose: bool = True,
) -> EvalSummary:
    """
    Run evaluation cases against the calculator agent.

    Args:
        cases: List of EvalCase objects. Defaults to ALL_CASES.
        agent: CalculatorAgent instance. Creates one with defaults if not provided.
        verbose: Print progress during the run.

    Returns:
        EvalSummary with all results.
    """
    if cases is None:
        cases = ALL_CASES
    if agent is None:
        agent = CalculatorAgent()

    summary = EvalSummary()

    for i, case in enumerate(cases, 1):
        if verbose:
            print(f"  [{i}/{len(cases)}] Running: {case.name} ...", end=" ", flush=True)

        result = _evaluate_case(agent, case)
        summary.results.append(result)

        if verbose:
            status = "PASS" if result.passed else "FAIL"
            print(status)

    return summary
