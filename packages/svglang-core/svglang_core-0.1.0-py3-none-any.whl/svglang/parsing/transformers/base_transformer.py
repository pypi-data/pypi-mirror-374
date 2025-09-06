# base_transformer.py - Base transformer with common functionality
from __future__ import annotations

from lark import Transformer, v_args

from ...core.ast import (
    ArrayAccess,
    ArrayLiteral,
    BinOp,
    Boolean,
    CanvasProperty,
    FunctionCall,
    InterpolatedString,
    Number,
    String,
    TernaryOp,
    UnitValue,
    Var,
)


class BaseTransformer(Transformer):
    """Base transformer with expression and literal handling."""

    def start(self, statements):
        """Handle the start rule - filter valid statements."""
        filtered = []
        if not isinstance(statements, (list, tuple)):
            statements = [statements]

        for stmt in statements:
            if stmt is not None:
                filtered.append(stmt)
        return filtered

    def number(self, args):
        """Transform number literals."""
        return Number(float(args[0]))

    def unit_value(self, args):
        """Transform number + unit combinations."""
        return UnitValue(float(args[0]), str(args[1]))

    def negative_number(self, args):
        """Transform negative number literals."""
        return Number(-float(args[0]))

    def negative_unit_value(self, args):
        """Transform negative number + unit combinations."""
        return UnitValue(-float(args[0]), str(args[1]))

    def array_literal(self, items):
        """Transform array literals."""
        if items is None:
            return ArrayLiteral([])
        if hasattr(items, 'children'):
            return ArrayLiteral(list(items.children))
        return ArrayLiteral(items)

    @v_args(inline=True)
    def array_access(self, array_expr, index):
        """Transform array access expressions."""
        if isinstance(array_expr, str):
            return ArrayAccess(Var(array_expr), index)
        else:
            return ArrayAccess(array_expr, index)

    @v_args(inline=True)
    def function_call(self, module, function, argument):
        """Transform function calls."""
        return FunctionCall(str(module), str(function), argument)

    def expr_list(self, items):
        """Transform expression lists."""
        return list(items)

    def var(self, token):
        """Transform variable references."""
        return Var(str(token[0]))

    def string(self, token):
        """Transform string literals, handling interpolation."""
        value = str(token[0])
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]

        # Check if the string contains interpolation patterns like {variable}
        if '{' in value and '}' in value:
            return self._parse_interpolated_string(value)
        else:
            return String(value)

    def _parse_interpolated_string(self, text):
        """Parse a string with {variable} interpolation into parts."""
        import re

        parts = []
        current_pos = 0

        # Find all {expression} patterns
        pattern = r'\{([^}]+)\}'

        for match in re.finditer(pattern, text):
            # Add literal text before the interpolation
            if match.start() > current_pos:
                literal_part = text[current_pos:match.start()]
                if literal_part:
                    parts.append(literal_part)

            # Parse the expression inside {}
            expr_text = match.group(1).strip()

            # For now, support simple variable names and basic expressions
            if ' ' not in expr_text and '.' not in expr_text:
                # Simple variable name
                parts.append(Var(expr_text))
            elif expr_text == 'canvas.width':
                parts.append(CanvasProperty('width'))
            elif expr_text == 'canvas.height':
                parts.append(CanvasProperty('height'))
            elif expr_text.startswith('math.'):
                # Math function call - parse manually for now
                if '(' in expr_text and ')' in expr_text:
                    # Function call with parentheses: math.sin(90deg)
                    func_match = re.match(r'math\.(\w+)\(([^)]+)\)', expr_text)
                    if func_match:
                        func_name = func_match.group(1)
                        arg_text = func_match.group(2).strip()

                        # Parse the argument
                        if arg_text.endswith('deg'):
                            value = float(arg_text[:-3])
                            arg = UnitValue(value, 'deg')
                        elif arg_text.endswith('rad'):
                            value = float(arg_text[:-3])
                            arg = UnitValue(value, 'rad')
                        elif arg_text.endswith('turn'):
                            value = float(arg_text[:-4])
                            arg = UnitValue(value, 'turn')
                        else:
                            try:
                                arg = Number(float(arg_text))
                            except ValueError:
                                arg = Var(arg_text)

                        parts.append(FunctionCall('math', func_name, arg))
                    else:
                        parts.append('{' + expr_text + '}')
                else:
                    # Function call without parentheses: math.sin 90deg
                    func_parts = expr_text.split()
                    if len(func_parts) >= 2:
                        func_part = func_parts[0]  # math.sin
                        if '.' in func_part:
                            module, func_name = func_part.split('.', 1)
                            arg_text = ' '.join(func_parts[1:])

                            # Parse the argument
                            if arg_text.endswith('deg'):
                                value = float(arg_text[:-3])
                                arg = UnitValue(value, 'deg')
                            elif arg_text.endswith('rad'):
                                value = float(arg_text[:-3])
                                arg = UnitValue(value, 'rad')
                            elif arg_text.endswith('turn'):
                                value = float(arg_text[:-4])
                                arg = UnitValue(value, 'turn')
                            else:
                                try:
                                    arg = Number(float(arg_text))
                                except ValueError:
                                    arg = Var(arg_text)

                            parts.append(FunctionCall(module, func_name, arg))
                        else:
                            parts.append('{' + expr_text + '}')
                    else:
                        parts.append('{' + expr_text + '}')
            else:
                # For now, treat complex expressions as literal text
                parts.append('{' + expr_text + '}')

            current_pos = match.end()

        # Add any remaining literal text
        if current_pos < len(text):
            remaining = text[current_pos:]
            if remaining:
                parts.append(remaining)

        return InterpolatedString(parts)

    def true_literal(self, token):
        """Transform true literals."""
        return Boolean(True)

    def false_literal(self, token):
        """Transform false literals."""
        return Boolean(False)

    def COMMENT(self, token):
        """Filter out comments."""
        return None

    # Canvas property accessors
    def canvas_width(self, args):
        """Transform canvas.width references."""
        return CanvasProperty('width')

    def canvas_height(self, args):
        """Transform canvas.height references."""
        return CanvasProperty('height')

    # Math function transformers
    def math_sin(self, args):
        """Transform math.sin function calls."""
        return FunctionCall('math', 'sin', [args[0]])

    def math_cos(self, args):
        """Transform math.cos function calls."""
        return FunctionCall('math', 'cos', [args[0]])

    def math_tan(self, args):
        """Transform math.tan function calls."""
        return FunctionCall('math', 'tan', [args[0]])

    def math_sqrt(self, args):
        """Transform math.sqrt function calls."""
        return FunctionCall('math', 'sqrt', [args[0]])

    def math_abs(self, args):
        """Transform math.abs function calls."""
        return FunctionCall('math', 'abs', [args[0]])

    def math_floor(self, args):
        """Transform math.floor function calls."""
        return FunctionCall('math', 'floor', [args[0]])

    def math_ceil(self, args):
        """Transform math.ceil function calls."""
        return FunctionCall('math', 'ceil', [args[0]])

    def math_min(self, args):
        """Transform math.min function calls."""
        return FunctionCall('math', 'min', [args[0], args[1]])

    def math_max(self, args):
        """Transform math.max function calls."""
        return FunctionCall('math', 'max', [args[0], args[1]])

    def math_pow(self, args):
        """Transform math.pow function calls."""
        return FunctionCall('math', 'pow', [args[0], args[1]])
