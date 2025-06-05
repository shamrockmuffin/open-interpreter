"""Mixture-of-Agents sub-package.

Usage example::

    from interpreter.agents.mixture import MixtureOfAgents
    moa = MixtureOfAgents([
        {"system_message": "Python expert."},
        {"system_message": "Bash wizard."}
    ])
    print(moa.chat("Write hello world", return_all=True))
"""

from .orchestrator import MixtureOfAgents

__all__ = ["MixtureOfAgents"]