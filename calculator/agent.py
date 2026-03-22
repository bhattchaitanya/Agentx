"""Calculator agent powered by Claude with tool use."""

import anthropic

from calculator.tools import CALCULATOR_TOOLS, execute_tool
from guardrails.input_guardrail import InputGuardrail
from guardrails.output_guardrail import OutputGuardrail


class CalculatorAgent:
    """A calculator agent that uses Claude to interpret and solve math problems."""

    def __init__(
        self,
        model: str = "claude-opus-4-6",
        max_tokens: int = 4096,
        input_guardrail: InputGuardrail | None = None,
        output_guardrail: OutputGuardrail | None = None,
    ):
        self.client = anthropic.Anthropic()
        self.model = model
        self.max_tokens = max_tokens
        self.input_guardrail = input_guardrail or InputGuardrail()
        self.output_guardrail = output_guardrail or OutputGuardrail()
        self.system_prompt = (
            "You are a precise calculator assistant. "
            "When given a math problem, use the available tools to compute the answer. "
            "Always use tools to perform calculations — do not compute in your head. "
            "Present the final answer clearly."
        )

    def solve(self, problem: str) -> dict:
        """
        Solve a math problem using Claude and calculator tools.

        Returns a dict with:
          - answer: the final text response
          - tool_calls: list of tool calls made
          - blocked: True if the input was blocked by guardrails
          - block_reason: reason for blocking (if blocked)
        """
        # Input guardrail check
        check = self.input_guardrail.check(problem)
        if check.blocked:
            return {
                "answer": f"Request blocked: {check.reason}",
                "tool_calls": [],
                "blocked": True,
                "block_reason": check.reason,
            }

        messages = [{"role": "user", "content": problem}]
        tool_calls = []

        # Agentic tool-use loop
        while True:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=self.system_prompt,
                tools=CALCULATOR_TOOLS,
                messages=messages,
            )

            if response.stop_reason == "end_turn":
                # Extract final text answer
                answer = next(
                    (b.text for b in response.content if b.type == "text"), ""
                )

                # Output guardrail check
                out_check = self.output_guardrail.check(answer)
                if out_check.blocked:
                    return {
                        "answer": f"Output blocked: {out_check.reason}",
                        "tool_calls": tool_calls,
                        "blocked": True,
                        "block_reason": out_check.reason,
                    }

                return {
                    "answer": answer,
                    "tool_calls": tool_calls,
                    "blocked": False,
                    "block_reason": None,
                }

            if response.stop_reason != "tool_use":
                # Unexpected stop reason — return whatever text we have
                answer = next(
                    (b.text for b in response.content if b.type == "text"), ""
                )
                return {
                    "answer": answer,
                    "tool_calls": tool_calls,
                    "blocked": False,
                    "block_reason": None,
                }

            # Execute tool calls
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []

            for block in response.content:
                if block.type != "tool_use":
                    continue

                result = execute_tool(block.name, block.input)
                tool_calls.append(
                    {"tool": block.name, "input": block.input, "result": result}
                )
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    }
                )

            messages.append({"role": "user", "content": tool_results})
