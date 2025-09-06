# statements.py - Statement grammar components
from __future__ import annotations

statements_grammar = r"""
// Main statement rules
?start: statement*

?statement: canvas_stmt
          | shape_stmt
          | repeat_stmt
          | while_stmt
          | for_stmt
          | foreach_stmt
          | if_stmt
          | var_stmt
          | group_def
          | group_use
          | gradient_stmt
          | clip_def
          | COMMENT

canvas_stmt: "canvas" "width" NUMBER "height" NUMBER ("background" STRING)?
var_stmt: "let" IDENT "=" expr
        | "let" IDENT "=" shape_stmt
repeat_stmt: "repeat" NUMBER "{" IDENT "in" statement+ "}"
while_stmt: "while" expr "{" statement+ "}"
for_stmt: "for" IDENT "in" expr ".." expr "{" statement+ "}"
foreach_stmt: "foreach" IDENT "in" expr "{" IDENT "in" statement+ "}"  // with index
          | "foreach" IDENT "in" expr "{" statement+ "}"                    // without index
if_stmt: "if" expr "{" statement+ "}" ("else" "{" statement+ "}")?

group_def: "group" IDENT "{" statement+ "}"
group_use: IDENT "at" "(" expr "," expr ")" ("fill" expr)? ("stroke" expr)? transform_list?

gradient_stmt: "gradient" gradient_type
?gradient_type: linear_gradient | radial_gradient | conic_gradient
linear_gradient: "linear" IDENT "from" "(" expr "," expr ")" "to" "(" expr "," expr ")" "{" gradient_stop+ "}"
radial_gradient: "radial" IDENT "center" "(" expr "," expr ")" "radius" expr "{" gradient_stop+ "}"
conic_gradient: "conic" IDENT "center" "(" expr "," expr ")" "angle" expr "{" gradient_stop+ "}"
gradient_stop: "stop" expr "at" expr

clip_def: "clip" IDENT "{" statement+ "}"

animate_block: "animate" "{" animation_property+ "}"
animation_property: animation_attr "from" expr "to" expr "duration" DURATION ("repeat" REPEAT)? ("direction" DIRECTION)? ("easing" EASING)?
animation_attr: IDENT | "font" "-" "size"

?transform_list: transform+
transform: "rotate" expr -> rotate
         | "scale" expr -> scale
         | "translate" expr expr -> translate
"""
