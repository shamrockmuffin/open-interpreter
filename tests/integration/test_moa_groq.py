"""Integration test hitting Groq's public API via LiteLLM.

Runs only if a Groq API key is available via the *GROQ_API_KEY* env var or uses
the key provided in the developer instructions.  The goal is simply to ensure
that our MixtureOfAgents wrapper can execute a real LLM round-trip without
raising, not to validate semantic correctness.
"""
from __future__ import annotations

import os
import time
from typing import List

import pytest

from interpreter.agents import MixtureOfAgents

# ---------------------------------------------------------------------------
# Test activation logic ------------------------------------------------------
# ---------------------------------------------------------------------------

DEFAULT_GROQ_KEY = "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"

API_KEY = os.getenv("GROQ_API_KEY", DEFAULT_GROQ_KEY)

if not API_KEY:
    pytest.skip("No Groq API key available", allow_module_level=True)

# Set the env var so litellm picks it up
os.environ["GROQ_API_KEY"] = API_KEY


@pytest.mark.timeout(60)
def test_moa_round_trip():  # noqa: D401 – imperative verb fine
    agent_cfgs: List[dict] = [{} for _ in range(2)]
    judge_cfg: dict = {}

    moa = MixtureOfAgents(agent_cfgs, judge_config=judge_cfg)

    # Configure all agents to hit Groq's free Llama-3 model
    MODEL_NAME = "groq/llama3-8b-8192"
    for agent in moa.agents:
        agent.llm.model = MODEL_NAME
        agent.llm.temperature = 0.0
        agent.llm.max_tokens = 64
    if moa.judge:
        moa.judge.llm.model = MODEL_NAME
        moa.judge.llm.temperature = 0.0
        moa.judge.llm.max_tokens = 64

    question = "What is 2 + 2? Answer with just the number."

    # The judge will pick one of the deterministic, identical answers.
    answer = moa.chat(question)

    assert answer.strip().startswith("4"), f"Unexpected answer: {answer}"