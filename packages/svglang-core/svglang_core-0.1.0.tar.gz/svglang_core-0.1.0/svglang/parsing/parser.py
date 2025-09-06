# parser.py - Main parser module combining all grammar components
from __future__ import annotations

from lark import Lark

from .grammar.base import base_grammar
from .grammar.expressions import expressions_grammar
from .grammar.shapes import shapes_grammar
from .grammar.statements import statements_grammar
from .transformer import SVGTransformer

# Combine all grammar components
svg_grammar = (
    base_grammar +
    expressions_grammar +
    shapes_grammar +
    statements_grammar
)

parser = Lark(svg_grammar, parser='lalr', transformer=SVGTransformer())
