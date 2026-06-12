"""Tests for session memory."""

import pytest

from rocket_tools.memory import SessionStore, get_store


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

    def test_record_history_copies_mutable_values(self):
        store = get_store()
        sid = store.create()
        mem = store.get(sid)
        params = {"cross_section": {"width": 0.05}}
        result = {"stress": {"max": 100}}

        mem.record("beam_analysis", params, result)
        params["cross_section"]["width"] = 0.1
        result["stress"]["max"] = 200

        assert mem.history[0].params["cross_section"]["width"] == 0.05
        assert mem.history[0].result["stress"]["max"] == 100

    def test_get_rejects_invalid_session_id(self):
        store = get_store()

        with pytest.raises(ValueError, match="non-empty string"):
            store.get("")

    def test_store_rejects_non_positive_ttl(self):
        with pytest.raises(ValueError, match="greater than 0"):
            SessionStore(ttl_seconds=0)
