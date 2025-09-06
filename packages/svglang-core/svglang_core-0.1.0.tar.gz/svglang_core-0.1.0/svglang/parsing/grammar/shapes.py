# shapes.py - Shape-related grammar components
from __future__ import annotations

shapes_grammar = r"""
// Shape statements
?shape_stmt: circle_stmt
           | rect_stmt
           | line_stmt
           | ellipse_stmt
           | polygon_stmt
           | text_stmt
           | path_stmt
           | arc_stmt
           | curve_stmt

circle_stmt: "circle" "radius" expr "at" "(" expr "," expr ")" shape_attributes? animate_block?
rect_stmt: "rect" "width" expr "height" expr "at" "(" expr "," expr ")" shape_attributes? animate_block?
ellipse_stmt: "ellipse" "rx" expr "ry" expr "at" "(" expr "," expr ")" shape_attributes? animate_block?

// Unified shape attributes - order doesn't matter
shape_attributes: shape_attribute+
shape_attribute: fill_expr
               | stroke_expr
               | stroke_width_expr
               | opacity_expr
               | rx_expr
               | font_size_expr
               | gradient_ref
               | clip_ref
               | transform

fill_expr: "fill" expr
stroke_expr: "stroke" expr
stroke_width_expr: "stroke-width" expr | "width" expr
opacity_expr: "opacity" expr
rx_expr: "rx" expr
font_size_expr: "font" "-" "size" expr | "size" expr
gradient_ref: "gradient" IDENT
clip_ref: "clip" IDENT

line_stmt: "line" "from" "(" expr "," expr ")" "to" "(" expr "," expr ")" shape_attributes?
polygon_stmt: "polygon" "points" point_list shape_attributes?
text_stmt: "text" expr "at" "(" expr "," expr ")" shape_attributes? animate_block?
path_stmt: "path" STRING shape_attributes?
arc_stmt: "arc" "rx" expr "ry" expr "at" "(" expr "," expr ")" "from" expr "to" expr shape_attributes?
curve_stmt: "curve" "from" "(" expr "," expr ")" "to" "(" expr "," expr ")" "control1" "(" expr "," expr ")" "control2" "(" expr "," expr ")" shape_attributes?

?point_list: point ("," point)*
point: "(" expr "," expr ")"
"""
