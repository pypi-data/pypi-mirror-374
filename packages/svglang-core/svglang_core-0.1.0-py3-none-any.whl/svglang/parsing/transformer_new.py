# transformer.py - Main SVG transformer combining all components
from __future__ import annotations

from .transformers.statement_transformer import StatementTransformer


class SVGTransformer(StatementTransformer):
    """Main SVG transformer that combines all parsing capabilities."""
