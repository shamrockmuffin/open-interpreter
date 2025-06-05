"""Example: Using MixtureOfAgents.

Run with:
    python examples/mixture_of_agents.py

(or, once installed via poetry/pip, simply `moa`).
"""
from __future__ import annotations

from interpreter.agents import MixtureOfAgents


def main() -> None:  # noqa: D401 – simple verb
    # Create two specialist agents plus a judge.
    moa = MixtureOfAgents(
        agent_configs=[
            {
                "system_message": "You are a concise Python expert.",
            },
            {
                "system_message": "You are a verbose step-by-step reasoner.",
            },
        ],
        judge_config={
            "system_message": "You evaluate which response best answers the user's question.",
        },
    )

    query = "Write a Python function that returns the Fibonacci sequence up to n."
    all_answers = moa.chat(query, return_all=True)
    print("Candidate answers:\n------------------")
    for idx, ans in enumerate(all_answers, 1):
        print(f"Option {idx}:\n{ans}\n")

    print("Selected answer:\n-----------------")
    best = moa.chat(query)
    print(best)


if __name__ == "__main__":
    main()