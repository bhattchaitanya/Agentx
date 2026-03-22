#!/usr/bin/env python3
"""
Calculator Agent — entry point.

Usage:
    # Interactive mode
    python main.py

    # Run evals
    python main.py --eval

    # Solve a single problem
    python main.py --solve "What is 2 + 2?"
"""

import argparse
import sys


def interactive_mode() -> None:
    from calculator.agent import CalculatorAgent

    agent = CalculatorAgent()
    print("Calculator Agent (type 'quit' to exit)\n")

    while True:
        try:
            problem = input("Enter a math problem: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if problem.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        result = agent.solve(problem)
        if result["blocked"]:
            print(f"Blocked: {result['block_reason']}\n")
        else:
            print(f"Answer: {result['answer']}")
            if result["tool_calls"]:
                print("Tool calls:")
                for tc in result["tool_calls"]:
                    print(f"  {tc['tool']}({tc['input']}) = {tc['result']}")
            print()


def run_evals() -> None:
    from evals.runner import run_evals as _run_evals

    print("Running evaluations...\n")
    summary = _run_evals()
    summary.print_report()

    if summary.failed > 0:
        sys.exit(1)


def solve_single(problem: str) -> None:
    from calculator.agent import CalculatorAgent

    agent = CalculatorAgent()
    result = agent.solve(problem)

    if result["blocked"]:
        print(f"Blocked: {result['block_reason']}")
        sys.exit(1)
    else:
        print(result["answer"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculator Agent")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--eval", action="store_true", help="Run evaluations")
    group.add_argument("--solve", metavar="PROBLEM", help="Solve a single problem")
    args = parser.parse_args()

    if args.eval:
        run_evals()
    elif args.solve:
        solve_single(args.solve)
    else:
        interactive_mode()
