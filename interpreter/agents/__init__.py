"""Top-level package for additional agent implementations (e.g. Mixture-of-Agents).

Importing `MixtureOfAgents` from here avoids callers needing to know the exact file layout::

    from interpreter.agents import MixtureOfAgents
"""

from importlib import import_module

# Re-export the main orchestrator so it is discoverable at the package root.
try:
    MixtureOfAgents = import_module("interpreter.agents.mixture.orchestrator").MixtureOfAgents  # type: ignore[attr-defined]
except ModuleNotFoundError:  # In case sub-package hasn't been created yet.
    MixtureOfAgents = None  # type: ignore

__all__ = ["MixtureOfAgents"]