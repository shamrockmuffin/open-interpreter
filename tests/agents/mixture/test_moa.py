from interpreter.agents.mixture import MixtureOfAgents


def _patch_agent_chats(moa, responses, monkeypatch):
    """Patch each agent's chat method to return corresponding response."""
    for idx, agent in enumerate(moa.agents):
        reply = responses[idx]

        def _chat(_self, _msg, display=False, _reply=reply):  # type: ignore[unused-argument]
            return [{"role": "assistant", "content": _reply}]

        monkeypatch.setattr(agent, "chat", _chat)


def test_return_all(monkeypatch):
    """`return_all=True` should return *all* candidate strings in order."""
    moa = MixtureOfAgents([{}, {}])
    expected = ["A", "B"]
    _patch_agent_chats(moa, expected.copy(), monkeypatch)

    outputs = moa.chat("hello", return_all=True)
    assert outputs == expected


def test_choose_best(monkeypatch):
    """With a judge and `choose_best` picking idx 1, the orchestrator returns that response."""
    # Monkeypatch choose_best to always pick index 1
    monkeypatch.setattr(
        "interpreter.agents.mixture.orchestrator.choose_best",  # module-level variable
        lambda _judge, _msg, _cands: 1,
    )

    moa = MixtureOfAgents([{}, {}], judge_config={})
    responses = ["RESP0", "RESP1"]
    _patch_agent_chats(moa, responses, monkeypatch)

    # Patch judge.chat to return dummy content (won't be parsed because choose_best mocked)
    monkeypatch.setattr(
        moa.judge,
        "chat",
        lambda _self, _msg, display=False: [{"role": "assistant", "content": "2"}],
    )

    result = moa.chat("question")
    assert result == "RESP1"