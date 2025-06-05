"""Utility functions to select the *best* response among multiple agents."""
from __future__ import annotations

import re
from typing import List

from interpreter.core.core import OpenInterpreter

__all__ = [
    "choose_best",
]


_NUMBER_RE = re.compile(r"(\d+)")


def _extract_first_int(text: str, *, default: int = 1) -> int:  # noqa: D401 – helper
    """Return the first integer found in *text*, falling back to *default*."""
    match = _NUMBER_RE.search(text)
    return int(match.group(1)) if match else default


def choose_best(
    judge_ai: OpenInterpreter, user_msg: str, candidate_responses: List[str]
) -> int:
    """Ask *judge_ai* to pick the best response index (0-based).

    The judge is prompted with the original user request followed by
    enumerated candidate answers.  It *must* reply with either the option
    number (1-based) or the full phrase ``Option X``.  We then parse the first
    integer in its output.
    """
    formatted_options = "\n\n".join(
        f"### Option {idx + 1}\n{resp}" for idx, resp in enumerate(candidate_responses)
    )

    judge_prompt = (
        "You are an impartial arbiter tasked with choosing the best assistant "
        "response to the user query.\n\n"
        f"## User query\n{user_msg}\n\n"
        f"## Candidate answers\n{formatted_options}\n\n"
        "Reply *only* with the number of the best option."
    )

    judge_messages = judge_ai.chat(judge_prompt, display=False)
    if not judge_messages:
        return 0  # fallback to first agent

    judge_reply = judge_messages[-1]["content"].strip()
    return _extract_first_int(judge_reply, default=1) - 1  # convert to 0-based