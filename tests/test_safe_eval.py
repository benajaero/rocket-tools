"""Tests for safe expression evaluation."""

import pytest

from rocket_tools.utils.safe_eval import safe_eval
from rocket_tools.utils.validation import ToolError


class TestSafeEval:
    def test_simple_addition(self):
        assert safe_eval("1 + 2", {}) == 3

    def test_simple_multiplication(self):
        assert safe_eval("3 * 4", {}) == 12

    def test_division(self):
        assert safe_eval("10 / 2", {}) == 5.0

    def test_power(self):
        assert safe_eval("2 ** 3", {}) == 8

    def test_unary_minus(self):
        assert safe_eval("-5", {}) == -5

    def test_variable_lookup(self):
        assert safe_eval("x + 1", {"x": 10}) == 11

    def test_attribute_access(self):
        class Obj:
            mass = 100

        assert safe_eval("obj.mass * 9.80665", {"obj": Obj()}) == pytest.approx(980.665)

    def test_dotdict_attribute(self):
        from rocket_tools.workflows.engine import _DotDict

        ctx = {"inputs": _DotDict({"mass_kg": 50.0})}
        assert safe_eval("inputs.mass_kg * 9.80665", ctx) == pytest.approx(490.3325)

    def test_function_call_blocked(self):
        with pytest.raises(ToolError, match="Function calls are not allowed"):
            safe_eval("max(1, 2)", {})

    def test_import_blocked(self):
        with pytest.raises(ToolError):
            safe_eval("__import__('os')", {})

    def test_invalid_syntax(self):
        with pytest.raises(ToolError, match="Invalid expression syntax"):
            safe_eval("1 + +", {})

    def test_unknown_variable(self):
        with pytest.raises(ToolError, match="Unknown variable"):
            safe_eval("undefined_var + 1", {})

    def test_comparison(self):
        assert safe_eval("5 > 3", {}) is True
        assert safe_eval("5 == 5", {}) is True
        assert safe_eval("5 != 3", {}) is True

    def test_subscript(self):
        assert safe_eval("data['key']", {"data": {"key": 42}}) == 42
