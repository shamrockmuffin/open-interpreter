#!/usr/bin/env python
"""Light-weight CLI wrapper around MixtureOfAgents.

This intentionally offers **minimal** ergonomics so it stays maintenance-free:

    $ moa                          # 2 agents + judge, default models
    $ moa -n 3 --model gpt-4o      # 3 agents running GPT-4o + judge
    $ moa -n 2 --judge-model ""     # disable judging; returns first answer

The script is installed via a Poetry entry-point declared in ``pyproject.toml``.
"""
from __future__ import annotations

import argparse
from typing import List

from interpreter.agents import MixtureOfAgents


def _parse_arguments(argv: List[str] | None = None) -> argparse.Namespace:  # noqa: D401
    parser = argparse.ArgumentParser(description="Mixture-of-Agents interactive shell")
    parser.add_argument(
        "-n",
        "--num-agents",
        type=int,
        default=2,
        help="Number of OpenInterpreter agents to spin up (default: 2)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-3.5-turbo",
        help="LLM model name for each agent (default: gpt-3.5-turbo)",
    )
    parser.add_argument(
        "--judge-model",
        type=str,
        default="gpt-3.5-turbo",
        help="Model name for judge – pass empty string to disable judging",
    )
    return parser.parse_args(argv)


def main() -> None:  # noqa: D401 – imperative verb fine
    args = _parse_arguments()

    agent_cfgs = [{} for _ in range(max(1, args.num_agents))]
    judge_cfg = {} if args.judge_model else None

    moa = MixtureOfAgents(agent_cfgs, judge_config=judge_cfg)

    # Apply model selections **after** construction so we don't break the normal
    # OpenInterpreter constructor (which expects an Llm instance, not a dict).
    for agent in moa.agents:
        agent.llm.model = args.model

    if moa.judge and args.judge_model:
        moa.judge.llm.model = args.judge_model

    print("Mixture-of-Agents shell – press Ctrl+C to exit.")
    try:
        while True:
            user_prompt = input("\n> ").strip()
            if not user_prompt:
                continue
            reply = moa.chat(user_prompt)
            print(f"\n[MOA] {reply}")
    except (KeyboardInterrupt, EOFError):
        print("\nBye!")


if __name__ == "__main__":  # pragma: no cover
    main()