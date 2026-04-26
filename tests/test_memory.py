"""Tests for session memory."""

import pytest
from rocket_tools.memory import get_store


class TestSessionStore:
    def test_create_session(self):
        store = get_store()
        sid = store.create(mission_type="aircraft")
        assert len(sid) == 8
        mem = store.get(sid)
        assert mem.mission_type == "aircraft"

    def test_merge_params(self):
        store = get_store()
        sid = store.create()
        mem = store.get(sid)
        p1 = mem.merge({"load": 500, "length": 2}, "beam_analysis")
        assert p1 == {"load": 500, "length": 2}
        p2 = mem.merge({"material": "6061-T6"}, "beam_analysis")
        assert p2 == {"load": 500, "length": 2, "material": "6061-T6"}

    def test_merge_override(self):
        store = get_store()
        sid = store.create()
        mem = store.get(sid)
        mem.merge({"load": 500}, "beam_analysis")
        p2 = mem.merge({"load": 1000}, "beam_analysis")
        assert p2["load"] == 1000

    def test_record_history(self):
        store = get_store()
        sid = store.create()
        mem = store.get(sid)
        mem.record("beam_analysis", {"load": 500}, {"stress": 100})
        assert len(mem.history) == 1
        assert mem.history[0].tool_name == "beam_analysis"
