"""Input guardrails for the calculator agent."""

import re
from dataclasses import dataclass


@dataclass
class GuardrailResult:
    blocked: bool
    reason: str | None = None


class InputGuardrail:
    """
    Validates and sanitizes incoming calculator requests.

    Checks:
    - Length limit (prevent abuse / prompt injection via very long inputs)
    - Non-math content (jailbreak / off-topic requests)
    - Disallowed patterns (code execution attempts, system prompts, etc.)
    """

    MAX_LENGTH = 500

    # Patterns that suggest attempts to abuse the system
    DISALLOWED_PATTERNS = [
        re.compile(r"ignore\s+(previous|above|prior|all)\s+instructions", re.IGNORECASE),
        re.compile(r"system\s*prompt", re.IGNORECASE),
        re.compile(r"<(script|iframe|img)[^>]*>", re.IGNORECASE),
        re.compile(r"(exec|eval|import|os\.system|subprocess)", re.IGNORECASE),
        re.compile(r"you\s+are\s+(now|actually|really)", re.IGNORECASE),
    ]

    # Minimum signal that the input is math-related
    MATH_SIGNAL_PATTERN = re.compile(
        r"[\d\+\-\*\/\^\(\)\.\%]|"
        r"\b(add|subtract|multiply|divide|plus|minus|times|divided|"
        r"square root|sqrt|power|modulo|remainder|percent|"
        r"sum|product|difference|quotient|calculate|compute|what is|"
        r"how much|solve|evaluate|"
        # calculus
        r"derivative|differentiate|integral|integrate|limit|taylor|series|"
        r"gradient|diverge|converge|"
        # matrices / linear algebra
        r"matrix|matrices|determinant|inverse|eigenvalue|eigenvector|"
        r"transpose|rank|linear system|vector)\b",
        re.IGNORECASE,
    )

    def check(self, text: str) -> GuardrailResult:
        """Run all input checks. Returns GuardrailResult."""
        if not text or not text.strip():
            return GuardrailResult(blocked=True, reason="Empty input.")

        if len(text) > self.MAX_LENGTH:
            return GuardrailResult(
                blocked=True,
                reason=f"Input too long ({len(text)} chars). Maximum is {self.MAX_LENGTH}.",
            )

        for pattern in self.DISALLOWED_PATTERNS:
            if pattern.search(text):
                return GuardrailResult(
                    blocked=True,
                    reason="Input contains disallowed content.",
                )

        if not self.MATH_SIGNAL_PATTERN.search(text):
            return GuardrailResult(
                blocked=True,
                reason="Input does not appear to be a math problem.",
            )

        return GuardrailResult(blocked=False)
