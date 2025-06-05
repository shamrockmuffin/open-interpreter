"""Orchestrator for running multiple `OpenInterpreter` agents in parallel (broadcast-reduce).

The orchestrator creates N `OpenInterpreter` instances, sends the same user
prompt to each, and (optionally) uses a judge model to pick the best answer.

The implementation purposefully stays *thin* – it delegates real work to the
already-existing :class:`interpreter.core.core.OpenInterpreter` class to avoid
forking core logic.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Union

from interpreter.core.core import OpenInterpreter

try:
    # Local import to avoid a hard dependency cycle.
    from .selectors import choose_best  # type: ignore  # noqa: WPS433 (allow import inside try)
except ImportError:  # pragma: no cover – during bootstrap the file may not yet exist.
    choose_best = None  # type: ignore

# Public exports -----------------------------------------------------------------
__all__ = ["MixtureOfAgents"]


class MixtureOfAgents:
    """A lightweight *Mixture-of-Agents* controller.

    Parameters
    ----------
    agent_configs:
        Sequence of kwargs passed to the ``OpenInterpreter`` constructor – one
        dict per agent.  Example::

            [
                {"system_message": "You are a concise expert."},
                {"system_message": "You are a verbose step-by-step reasoner."}
            ]

    judge_config:
        (Optional) kwargs for a *judge* ``OpenInterpreter`` used to select the
        best response.  If *None*, the orchestrator returns the first agent's
        answer (or *all* answers if ``return_all=True``).

    max_parallel:
        Placeholder for future async parallelism.  Currently unused but kept in
        the signature so the public API doesn't break once async support lands.
    """

    def __init__(
        self,
        agent_configs: Sequence[Dict[str, Any]],
        *,
        judge_config: Optional[Dict[str, Any]] = None,
        max_parallel: int = 4,
    ) -> None:
        if not agent_configs:
            raise ValueError("`agent_configs` must contain at least one config dict.")

        self.agents: List[OpenInterpreter] = [
            OpenInterpreter(**cfg) for cfg in agent_configs
        ]
        self.judge: Optional[OpenInterpreter] = (
            OpenInterpreter(**judge_config) if judge_config else None
        )
        self.max_parallel = max_parallel

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def chat(
        self,
        message: str,
        *,
        display: bool = False,
        return_all: bool = False,
    ) -> Union[str, List[str]]:
        """Send *message* to every agent and return the selected response.

        Parameters
        ----------
        message:
            The user prompt to broadcast to all agents.
        display:
            Passed through to each ``OpenInterpreter.chat`` call (defaults to
            *False* so that orchestrator usage inside Jupyter / scripts is
            silent by default).
        return_all:
            If *True*, return a ``list`` with every agent's answer instead of
            selecting the best.
        """
        # NOTE: For now we run calls sequentially – easy to debug and avoids
        # race conditions with the underlying LLM provider API limits.  Async
        # broadcasting is a future enhancement.
        candidate_responses: List[str] = []
        for agent in self.agents:
            # The OpenInterpreter.chat interface returns a list of new messages.
            # The last element is typically the assistant reply.
            messages = agent.chat(message, display=display)
            if not messages:
                candidate_responses.append("")
            else:
                candidate_responses.append(messages[-1]["content"])

        if return_all or self.judge is None or choose_best is None:
            return candidate_responses if return_all else candidate_responses[0]

        best_idx = choose_best(self.judge, message, candidate_responses)
        # Safety: clamp to valid range to avoid IndexError on malformed judge output.
        best_idx = max(0, min(best_idx, len(candidate_responses) - 1))
        return candidate_responses[best_idx]

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------
    def reset(self) -> None:  # noqa: D401 – simple verb is fine
        """Reset *all* underlying agents (clears conversation history)."""
        for agent in self.agents:
            agent.reset()
        if self.judge is not None:
            self.judge.reset()