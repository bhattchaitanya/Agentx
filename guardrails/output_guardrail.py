"""Output guardrails for the calculator agent."""

import re
from dataclasses import dataclass


@dataclass
class GuardrailResult:
    blocked: bool
    reason: str | None = None


class OutputGuardrail:
    """
    Validates the agent's output before returning it to the caller.

    Checks:
    - Output length sanity (very long output might indicate hallucination)
    - Detects leaked system prompt fragments
    - Ensures a numeric answer is present (the agent should always produce one)
    """

    MAX_OUTPUT_LENGTH = 2000

    LEAKED_SYSTEM_PATTERNS = [
        re.compile(r"you are a precise calculator assistant", re.IGNORECASE),
        re.compile(r"always use tools to perform calculations", re.IGNORECASE),
    ]

    # The answer should contain at least one number
    NUMERIC_PATTERN = re.compile(r"-?\d+(\.\d+)?")

    def check(self, text: str) -> GuardrailResult:
        """Run all output checks. Returns GuardrailResult."""
        if not text or not text.strip():
            return GuardrailResult(blocked=True, reason="Empty output from model.")

        if len(text) > self.MAX_OUTPUT_LENGTH:
            return GuardrailResult(
                blocked=True,
                reason=f"Output too long ({len(text)} chars). Possible hallucination.",
            )

        for pattern in self.LEAKED_SYSTEM_PATTERNS:
            if pattern.search(text):
                return GuardrailResult(
                    blocked=True,
                    reason="Output contains leaked system prompt content.",
                )

        if not self.NUMERIC_PATTERN.search(text):
            return GuardrailResult(
                blocked=True,
                reason="Output does not contain a numeric answer.",
            )

        return GuardrailResult(blocked=False)
