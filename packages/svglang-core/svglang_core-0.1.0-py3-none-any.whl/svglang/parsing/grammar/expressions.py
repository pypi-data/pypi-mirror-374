# expressions.py - Expression grammar components
from __future__ import annotations

expressions_grammar = r"""
// Expression parsing rules
?expr: ternary

?ternary: logical_or "?" ternary ":" ternary -> ternary_op
        | logical_or

?logical_or: logical_or "||" logical_and -> logical_or_op
           | logical_or "or" logical_and -> logical_or_op
           | logical_and

?logical_and: logical_and "&&" logical_not -> logical_and_op
            | logical_and "and" logical_not -> logical_and_op
            | logical_not

?logical_not: "!" logical_not -> logical_not_op
            | "not" logical_not -> logical_not_op
            | comparison

?comparison: comparison "+" term   -> add
           | comparison "-" term   -> sub
           | comparison "<" term   -> lt
           | comparison ">" term   -> gt
           | comparison "<=" term  -> le
           | comparison ">=" term  -> ge
           | comparison "==" term  -> eq
           | comparison "!=" term  -> ne
           | term

?term: term "*" power -> mul
     | term "/" power -> div
     | term "%" power -> mod
     | power

?power: factor "**" power -> pow
      | factor

?factor: NUMBER        -> number
       | NUMBER (DEG|RAD|TURN|PX|MM|CM|IN|PT|PERCENT|SEC|MS)   -> unit_value
       | "+" NUMBER    -> positive_number
       | "+" NUMBER (DEG|RAD|TURN|PX|MM|CM|IN|PT|PERCENT|SEC|MS) -> positive_unit_value
       | "-" NUMBER    -> negative_number
       | "-" NUMBER (DEG|RAD|TURN|PX|MM|CM|IN|PT|PERCENT|SEC|MS) -> negative_unit_value
       | IDENT         -> var
       | "canvas" "." "width" -> canvas_width
       | "canvas" "." "height" -> canvas_height
       | "math" "." "sin" expr -> math_sin
       | "math" "." "cos" expr -> math_cos
       | "math" "." "tan" expr -> math_tan
       | "math" "." "sqrt" expr -> math_sqrt
       | "math" "." "abs" expr -> math_abs
       | "math" "." "floor" expr -> math_floor
       | "math" "." "ceil" expr -> math_ceil
       | "math" "." "min" expr expr -> math_min
       | "math" "." "max" expr expr -> math_max
       | "math" "." "pow" expr expr -> math_pow
       | STRING        -> string
       | "true"        -> true_literal
       | "false"       -> false_literal
       | factor "[" expr "]" -> array_access
       | "[" expr_list? "]" -> array_literal
       | "(" expr ")"

?expr_list: expr ("," expr)*
"""
