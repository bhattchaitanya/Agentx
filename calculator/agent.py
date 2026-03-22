"""Calculator agent powered by Claude with tool use."""

import anthropic

from calculator.tools import CALCULATOR_TOOLS, execute_tool
from calculator.calculus_tools import CALCULUS_TOOLS
from calculator.matrix_tools import MATRIX_TOOLS
from guardrails.input_guardrail import InputGuardrail
from guardrails.output_guardrail import OutputGuardrail

# Skill name → additional tool definitions to load
_SKILL_TOOLS: dict[str, list] = {
    "arithmetic": [],
    "calculus":   CALCULUS_TOOLS,
    "matrices":   MATRIX_TOOLS,
}

# System prompts per skill
_SKILL_PROMPTS: dict[str, str] = {
    "arithmetic": (
        "You are a precise arithmetic calculator assistant. "
        "Always use the provided tools to compute answers — never compute in your head."
    ),
    "calculus": (
        "You are a calculus assistant. "
        "Use the differentiate, integrate, limit, and taylor_series tools to answer questions. "
        "Express results using standard mathematical notation where possible."
    ),
    "matrices": (
        "You are a linear algebra assistant. "
        "Use the matrix tools to perform operations like multiplication, inversion, "
        "eigenvalue computation, and solving linear systems. "
        "Always use tools — never compute by hand."
    ),
}


class CalculatorAgent:
    """
    A calculator agent that uses Claude to interpret and solve math problems.

    Skills:
      - "arithmetic"  (default) — basic arithmetic tools
      - "calculus"    — differentiation, integration, limits, Taylor series
      - "matrices"    — matrix operations and linear systems
      - "all"         — every tool enabled
    """

    def __init__(
        self,
        model: str = "claude-opus-4-6",
        max_tokens: int = 4096,
        skill: str = "all",
        input_guardrail: InputGuardrail | None = None,
        output_guardrail: OutputGuardrail | None = None,
    ):
        if skill not in (*_SKILL_TOOLS, "all"):
            raise ValueError(f"Unknown skill: {skill!r}. Choose from: arithmetic, calculus, matrices, all")

        self.client = anthropic.Anthropic()
        self.model = model
        self.max_tokens = max_tokens
        self.skill = skill
        self.input_guardrail = input_guardrail or InputGuardrail()
        self.output_guardrail = output_guardrail or OutputGuardrail()

        if skill == "all":
            self.tools = CALCULATOR_TOOLS + CALCULUS_TOOLS + MATRIX_TOOLS
            self.system_prompt = (
                "You are a comprehensive math assistant with skills in arithmetic, "
                "calculus, and linear algebra. Always use the provided tools to compute "
                "answers — never compute in your head. Present results clearly."
            )
        else:
            self.tools = CALCULATOR_TOOLS + _SKILL_TOOLS[skill]
            self.system_prompt = _SKILL_PROMPTS.get(skill, _SKILL_PROMPTS["arithmetic"])

    def solve(self, problem: str) -> dict:
        """
        Solve a math problem using Claude and the loaded tools.

        Returns a dict with:
          - answer: the final text response
          - tool_calls: list of tool calls made
          - blocked: True if guardrails blocked the request/response
          - block_reason: reason for blocking (if blocked)
          - skill: the skill set used
        """
        check = self.input_guardrail.check(problem)
        if check.blocked:
            return {
                "answer": f"Request blocked: {check.reason}",
                "tool_calls": [],
                "blocked": True,
                "block_reason": check.reason,
                "skill": self.skill,
            }

        messages = [{"role": "user", "content": problem}]
        tool_calls = []

        while True:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=self.system_prompt,
                tools=self.tools,
                messages=messages,
            )

            if response.stop_reason == "end_turn":
                answer = next(
                    (b.text for b in response.content if b.type == "text"), ""
                )
                out_check = self.output_guardrail.check(answer)
                if out_check.blocked:
                    return {
                        "answer": f"Output blocked: {out_check.reason}",
                        "tool_calls": tool_calls,
                        "blocked": True,
                        "block_reason": out_check.reason,
                        "skill": self.skill,
                    }
                return {
                    "answer": answer,
                    "tool_calls": tool_calls,
                    "blocked": False,
                    "block_reason": None,
                    "skill": self.skill,
                }

            if response.stop_reason != "tool_use":
                answer = next(
                    (b.text for b in response.content if b.type == "text"), ""
                )
                return {
                    "answer": answer,
                    "tool_calls": tool_calls,
                    "blocked": False,
                    "block_reason": None,
                    "skill": self.skill,
                }

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
