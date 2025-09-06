# base.py - Base grammar components
from __future__ import annotations

base_grammar = r"""
// Base tokens and primitives
NUMBER: /\d+(\.\d+)?/
STRING: /"[^"]*"/

// Unit tokens - defined before IDENT for higher priority
DEG: "deg"
RAD: "rad"
TURN: "turn"
PX: "px"
MM: "mm"
CM: "cm"
IN: "in"
PT: "pt"
PERCENT: "%"
SEC: "s"
MS: "ms"

IDENT: /[a-zA-Z_][a-zA-Z0-9_]*/
DURATION: /\d+(\.\d+)?(s|ms)/
REPEAT: /infinite|once|\d+/
DIRECTION: /normal|reverse|alternate|alternate-reverse/
EASING: /linear|ease|ease-in|ease-out|ease-in-out/

COMMENT: /(\/\/.*|#.*)/

%ignore /\s+/
"""
