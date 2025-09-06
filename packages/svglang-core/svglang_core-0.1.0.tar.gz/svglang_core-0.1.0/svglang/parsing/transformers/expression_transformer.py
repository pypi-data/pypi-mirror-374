# expression_transformer.py - Expression-specific transformations
from __future__ import annotations

import re
from lark import v_args

from .base_transformer import BaseTransformer
from ...core.ast import BinOp, TernaryOp


class ExpressionTransformer(BaseTransformer):
    """Transformer for expressions and operators."""

    # Binary operations
    @v_args(inline=True)
    def add(self, left, right):
        return BinOp(left, '+', right)

    @v_args(inline=True)
    def sub(self, left, right):
        return BinOp(left, '-', right)

    @v_args(inline=True)
    def mul(self, left, right):
        return BinOp(left, '*', right)

    @v_args(inline=True)
    def div(self, left, right):
        return BinOp(left, '/', right)

    @v_args(inline=True)
    def mod(self, left, right):
        return BinOp(left, '%', right)

    # Comparison operations
    @v_args(inline=True)
    def lt(self, left, right):
        return BinOp(left, '<', right)

    @v_args(inline=True)
    def gt(self, left, right):
        return BinOp(left, '>', right)

    @v_args(inline=True)
    def le(self, left, right):
        return BinOp(left, '<=', right)

    @v_args(inline=True)
    def ge(self, left, right):
        return BinOp(left, '>=', right)

    @v_args(inline=True)
    def eq(self, left, right):
        return BinOp(left, '==', right)

    @v_args(inline=True)
    def ne(self, left, right):
        return BinOp(left, '!=', right)

    # Logical operations
    @v_args(inline=True)
    def logical_or_op(self, left, right):
        return BinOp(left, '||', right)

    @v_args(inline=True)
    def logical_and_op(self, left, right):
        return BinOp(left, '&&', right)

    @v_args(inline=True)
    def logical_not_op(self, operand):
        return BinOp(None, '!', operand)

    # Ternary operation
    @v_args(inline=True)
    def ternary_op(self, condition, true_value, false_value):
        return TernaryOp(condition, true_value, false_value)
