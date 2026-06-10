"""Safe mathematical expression evaluator using Python's ast module.

Replaces eval() in workflow interpolation with a restricted evaluator
that only permits arithmetic operations and attribute access.
"""

import ast
import operator
from typing import Any

from rocket_tools.utils.validation import ValidationError

# Allowed binary operators
_BIN_OPS: dict[Any, Any] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

# Allowed comparison operators
_COMP_OPS: dict[Any, Any] = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
}


class SafeEvaluator(ast.NodeVisitor):
    """Evaluate AST nodes with restricted operations."""

    def __init__(self, context: dict[str, Any]):
        self.context = context

    def visit(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Expression):
            return self.visit(node.body)
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Num):  # Python <3.8 compatibility
            return node.n
        if isinstance(node, ast.Name):
            if node.id in self.context:
                return self.context[node.id]
            raise ValidationError(
                f"Unknown variable '{node.id}'", "interpolation", "valid variable name"
            )
        if isinstance(node, ast.Attribute):
            obj = self.visit(node.value)
            return getattr(obj, node.attr)
        if isinstance(node, ast.BinOp):
            left = self.visit(node.left)
            right = self.visit(node.right)
            op_type: Any = type(node.op)
            if op_type not in _BIN_OPS:
                raise ValidationError(
                    f"Unsupported binary operator: {op_type.__name__}",
                    "interpolation",
                    "+, -, *, /, **",
                )
            return _BIN_OPS[op_type](left, right)
        if isinstance(node, ast.UnaryOp):
            operand = self.visit(node.operand)
            op_type = type(node.op)
            if op_type not in _BIN_OPS:
                raise ValidationError(
                    f"Unsupported unary operator: {op_type.__name__}",
                    "interpolation",
                    "+, -",
                )
            return _BIN_OPS[op_type](operand)
        if isinstance(node, ast.Compare):
            left = self.visit(node.left)
            if len(node.ops) != 1 or len(node.comparators) != 1:
                raise ValidationError(
                    "Only single comparisons supported", "interpolation", "a == b"
                )
            comp_op_type: Any = type(node.ops[0])
            if comp_op_type not in _COMP_OPS:
                raise ValidationError(
                    f"Unsupported comparison: {op_type.__name__}",
                    "interpolation",
                    "==, !=, <, <=, >, >=",
                )
            right = self.visit(node.comparators[0])
            return _COMP_OPS[comp_op_type](left, right)
        if isinstance(node, ast.Call):
            raise ValidationError(
                "Function calls are not allowed in expressions",
                "interpolation",
                "arithmetic only",
            )
        if isinstance(node, ast.Subscript):
            obj = self.visit(node.value)
            slice_val = self.visit(node.slice)
            return obj[slice_val]
        raise ValidationError(
            f"Unsupported expression type: {type(node).__name__}",
            "interpolation",
            "arithmetic and attribute access only",
        )


def safe_eval(expression: str, context: dict[str, Any]) -> Any:
    """Safely evaluate a mathematical expression.

    Supports: +, -, *, /, **, comparisons, attribute access, variable lookup.
    Does NOT support: function calls, lambda, comprehensions, imports.
    """
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as e:
        raise ValidationError(
            f"Invalid expression syntax: {e}", "interpolation", "valid Python expression"
        ) from e
    evaluator = SafeEvaluator(context)
    return evaluator.visit(tree)
