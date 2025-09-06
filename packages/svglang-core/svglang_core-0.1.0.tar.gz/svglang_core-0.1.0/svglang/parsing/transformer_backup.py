# transformer.py - Main SVG transformer combining all components
from __future__ import annotations

from .transformers.statement_transformer import StatementTransformer


class SVGTransformer(StatementTransformer):
    """Main SVG transformer that combines all parsing capabilities."""

    pass



    def start(self, statements):
        # Filter out None values and any other invalid statements
        filtered = []
        # Ensure statements is always a list
        if not isinstance(statements, (list, tuple)):
            statements = [statements]

        for stmt in statements:
            if stmt is not None:
                filtered.append(stmt)
        return filtered

    def number(self, args):
        return Number(float(args[0]))

    def unit_value(self, args):
        return UnitValue(float(args[0]), str(args[1]))

    def negative_number(self, args):
        return Number(-float(args[0]))

    def negative_unit_value(self, args):
        return UnitValue(-float(args[0]), str(args[1]))

    def array_literal(self, items):
        # items can be None if empty array
        if items is None:
            return ArrayLiteral([])
        # items is a Tree object, extract the children
        if hasattr(items, 'children'):
            return ArrayLiteral(list(items.children))
        # items is a list of expressions
        return ArrayLiteral(items)

    @v_args(inline=True)
    def array_access(self, array_expr, index):
        # array_expr can be a variable name (str) or another expression (like nested array access)
        if isinstance(array_expr, str):
            # Convert string to Var object
            return ArrayAccess(Var(array_expr), index)
        else:
            # Already an expression (like another ArrayAccess)
            return ArrayAccess(array_expr, index)

    @v_args(inline=True)
    def function_call(self, module, function, argument):
        return FunctionCall(str(module), str(function), argument)





    def expr_list(self, items):
        # Convert Tree to list of expressions
        return list(items)

    def var(self, token):
        return Var(str(token[0]))

    def string(self, token):
        # Remove quotes from string literal
        value = str(token[0])
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]

        # Check if the string contains interpolation patterns like {variable}
        if '{' in value and '}' in value:
            return self._parse_interpolated_string(value)
        else:
            return String(value)

    def _parse_interpolated_string(self, text):
        """Parse a string with {variable} interpolation into parts"""
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
                parts.append(CanvasProperty("width"))
            elif expr_text == 'canvas.height':
                parts.append(CanvasProperty("height"))
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
        return Boolean(True)

    def false_literal(self, token):
        return Boolean(False)

    def COMMENT(self, token):
        return None  # Filter out comments

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

    @v_args(inline=True)
    def ternary_op(self, condition, true_value, false_value):
        return TernaryOp(condition, true_value, false_value)

    @v_args(inline=True)
    def canvas_stmt(self, width, height, bg=None):
        if bg:
            # bg is a raw token, strip quotes
            bg_str = str(bg)
            if bg_str.startswith('"') and bg_str.endswith('"'):
                bg = bg_str[1:-1]
            else:
                bg = bg_str
        else:
            bg = "white"
        return Canvas(int(width), int(height), bg)

    def circle_stmt(self, args):
        # Parser structure: radius, x, y, [circle_property]*, [transform_list]?, [animate_block]?
        radius, x, y = args[0], args[1], args[2]

        fill_val = String("none")
        stroke_val = String("black")
        transform_list = []
        gradient_ref = None
        clip_ref = None
        animation_block = None

        # Process remaining arguments
        i = 3
        while i < len(args):
            arg = args[i]
            if isinstance(arg, tuple) and len(arg) == 2:
                prop_name, prop_value = arg
                if prop_name == 'fill':
                    fill_val = prop_value
                elif prop_name == 'stroke':
                    stroke_val = prop_value
                elif prop_name == 'gradient':
                    gradient_ref = GradientRef(prop_value)
                elif prop_name == 'clip':
                    clip_ref = ClipRef(prop_value)
            elif isinstance(arg, list):  # transform_list
                transform_list = arg
            elif isinstance(arg, AnimationBlock):  # animation block
                animation_block = arg
            elif isinstance(arg, (Rotate, Scale, Translate)):  # single transform
                transform_list = [arg]
            i += 1

        # If gradient is specified, use it for fill
        if gradient_ref:
            fill_val = gradient_ref

        circle = Circle(radius, x, y, fill_val, stroke_val, transform_list)
        circle.animation = animation_block
        circle.clip = clip_ref
        return circle

    def fill_expr(self, args):
        # args[0] is the expression after "fill"
        return ('fill', args[0])

    def stroke_expr(self, args):
        # args[0] is the expression after "stroke"
        return ('stroke', args[0])

    def rx_expr(self, args):
        # args[0] is the expression after "rx"
        return ('rx', args[0])

    def font_size_expr(self, args):
        # args[0] is the expression after "font-size"
        return ('font-size', args[0])

    def gradient_ref(self, args):
        # args[0] is the IDENT after "gradient"
        return ('gradient', str(args[0]))

    def clip_ref(self, args):
        # args[0] is the IDENT after "clip"
        return ('clip', str(args[0]))

    def circle_property(self, args):
        return args[0]  # Just pass through the property tuple

    def rect_property(self, args):
        return args[0]  # Just pass through the property tuple

    def ellipse_property(self, args):
        return args[0]  # Just pass through the property tuple

    def text_property(self, args):
        return args[0]  # Just pass through the property tuple

    def clip_def(self, args):
        # args[0] is the name, args[1:] are the shapes
        name = str(args[0])
        shapes = list(args[1:])
        return ClipDef(name, shapes)

    def rect_stmt(self, args):
        # Parser structure: width, height, x, y, [rect_property]*, [transform_list]?, [animate_block]?
        width, height, x, y = args[0], args[1], args[2], args[3]

        fill_val = String("none")
        stroke_val = String("black")
        rx_val = None
        transform_list = []
        gradient_ref = None
        clip_ref = None
        animation_block = None

        # Process remaining arguments
        i = 4
        while i < len(args):
            arg = args[i]
            if isinstance(arg, tuple) and len(arg) == 2:
                prop_name, prop_value = arg
                if prop_name == 'fill':
                    fill_val = prop_value
                elif prop_name == 'stroke':
                    stroke_val = prop_value
                elif prop_name == 'rx':
                    rx_val = prop_value
                elif prop_name == 'gradient':
                    gradient_ref = GradientRef(prop_value)
                elif prop_name == 'clip':
                    clip_ref = ClipRef(prop_value)
            elif isinstance(arg, list):  # transform_list
                transform_list = arg
            elif isinstance(arg, AnimationBlock):  # animation block
                animation_block = arg
            elif isinstance(arg, (Rotate, Scale, Translate)):  # single transform
                transform_list = [arg]
            i += 1

        # If gradient is specified, use it for fill
        if gradient_ref:
            fill_val = gradient_ref

        rect = Rect(width, height, x, y, fill_val, stroke_val, transform_list, rx_val)
        rect.animation = animation_block
        rect.clip = clip_ref
        return rect

    @v_args(inline=True)
    def line_stmt(self, x1, y1, x2, y2, stroke=None, stroke_width=None, transforms=None):
        stroke_val = stroke if stroke else String("black")
        sw = stroke_width if stroke_width else Number(1)
        transform_list = transforms if transforms else []
        return Line(x1, y1, x2, y2, stroke_val, sw, transform_list)

    @v_args(inline=True)
    def var_stmt(self, name, value):
        return VarDecl(str(name), value)

    def ellipse_stmt(self, args):
        # Parser structure: rx, ry, x, y, [ellipse_property]*, [transform_list]?, [animate_block]?
        rx, ry, x, y = args[0], args[1], args[2], args[3]

        fill_val = String("none")
        stroke_val = String("black")
        transform_list = []
        gradient_ref = None
        clip_ref = None
        animation_block = None

        # Process remaining arguments
        i = 4
        while i < len(args):
            arg = args[i]
            if isinstance(arg, tuple) and len(arg) == 2:
                prop_name, prop_value = arg
                if prop_name == 'fill':
                    fill_val = prop_value
                elif prop_name == 'stroke':
                    stroke_val = prop_value
                elif prop_name == 'gradient':
                    gradient_ref = GradientRef(prop_value)
                elif prop_name == 'clip':
                    clip_ref = ClipRef(prop_value)
            elif isinstance(arg, list):  # transform_list
                transform_list = arg
            elif isinstance(arg, AnimationBlock):  # animation block
                animation_block = arg
            elif isinstance(arg, (Rotate, Scale, Translate)):  # single transform
                transform_list = [arg]
            i += 1

        # If gradient is specified, use it for fill
        if gradient_ref:
            fill_val = gradient_ref

        ellipse = Ellipse(rx, ry, x, y, fill_val, stroke_val, transform_list)
        ellipse.animation = animation_block
        ellipse.clip = clip_ref
        return ellipse

    def point_list(self, points):
        # points is a list of point objects, filter out None values
        return [p for p in points if p is not None]

    @v_args(inline=True)
    def point(self, x, y):
        # Convert point to (x, y) tuple
        return (x, y)

    @v_args(inline=True)
    def polygon_stmt(self, points, fill=None, stroke=None):
        fill_val = fill if fill else String("none")
        stroke_val = stroke if stroke else String("black")
        return Polygon(points, fill_val, stroke_val)

    @v_args(inline=True)
    def text_stmt(self, *args):
        # Parser structure: content, x, y, [text_property]*, [transform_list]?, [animate_block]?
        content, x, y = args[0], args[1], args[2]

        fill_val = String("black")
        font_size_val = Number(16)
        transform_list = []
        clip_ref = None
        animation_block = None

        # Process remaining arguments
        i = 3
        while i < len(args):
            arg = args[i]
            if isinstance(arg, tuple) and len(arg) == 2:
                prop_name, prop_value = arg
                if prop_name == 'fill':
                    fill_val = prop_value
                elif prop_name == 'font-size':
                    font_size_val = prop_value
                elif prop_name == 'clip':
                    clip_ref = ClipRef(prop_value)
            elif isinstance(arg, list):  # transform_list
                transform_list = arg
            elif isinstance(arg, AnimationBlock):  # animation block
                animation_block = arg
            elif isinstance(arg, (Rotate, Scale, Translate)):  # single transform
                transform_list = [arg]
            i += 1

        text = Text(content, x, y, fill_val, font_size_val, transform_list)
        text.animation = animation_block
        text.clip = clip_ref
        return text

    @v_args(inline=True)
    def path_stmt(self, path_data, fill=None, stroke=None, stroke_width=None):
        # path_data is a raw STRING token, so we need to process it
        if hasattr(path_data, 'value') and not hasattr(path_data, 'type'): # It's a String object
            path_val = path_data.value
        else: # It's a raw token, strip quotes
            path_str = str(path_data)
            if path_str.startswith('"') and path_str.endswith('"'):
                path_val = path_str[1:-1]
            else:
                path_val = path_str
        fill_val = fill if fill else String("none")
        stroke_val = stroke if stroke else String("black")
        sw = stroke_width if stroke_width else Number(1)
        return Path(path_val, fill_val, stroke_val, sw)

    @v_args(inline=True)
    def arc_stmt(self, rx, ry, x, y, start_angle, end_angle, fill=None, stroke=None):
        fill_val = fill if fill else String("none")
        stroke_val = stroke if stroke else String("black")
        return Arc(rx, ry, x, y, start_angle, end_angle, fill_val, stroke_val)

    @v_args(inline=True)
    def curve_stmt(self, x1, y1, x2, y2, cx1, cy1, cx2, cy2, stroke=None, stroke_width=None):
        stroke_val = stroke if stroke else String("black")
        sw = stroke_width if stroke_width else Number(1)
        return Curve(x1, y1, x2, y2, cx1, cy1, cx2, cy2, stroke_val, sw)

    @v_args(inline=True)
    def group_def(self, name, *body):
        # Filter out None values from body
        filtered_body = [stmt for stmt in body if stmt is not None]
        # name is now an IDENT token, so we can get it directly
        name_str = str(name)
        return GroupDef(name_str, filtered_body)

    @v_args(inline=True)
    def group_use(self, name, x, y, fill=None, stroke=None, transforms=None):
        # name is an IDENT token
        name_str = str(name)
        # transforms might be None or a list
        transform_list = transforms if transforms else []
        return GroupUse(name_str, x, y, fill, stroke, transform_list)



    def transform_list(self, transforms):
        return [t for t in transforms if t is not None]

    @v_args(inline=True)
    def rotate(self, angle):
        return Rotate(angle)

    @v_args(inline=True)
    def scale(self, factor):
        return Scale(factor)

    @v_args(inline=True)
    def translate(self, x, y):
        return Translate(x, y)




    @v_args(inline=True)
    def repeat_stmt(self, times, var_name, *body):
        # Filter out None values from body
        filtered_body = [stmt for stmt in body if stmt is not None]
        return Repeat(int(times), str(var_name), filtered_body)

    @v_args(inline=True)
    def while_stmt(self, condition, *body):
        # Filter out None values from body
        filtered_body = [stmt for stmt in body if stmt is not None]
        return While(condition, filtered_body)

    @v_args(inline=True)
    def for_stmt(self, var_name, start, end, *body):
        # Filter out None values from body
        filtered_body = [stmt for stmt in body if stmt is not None]
        return For(str(var_name), start, end, filtered_body)

    @v_args(inline=True)
    def foreach_stmt(self, var_name, iterable, *args):
        # Check if we have index parameter or just body statements
        if len(args) > 0 and isinstance(args[0], str):
            # First arg is index_name (string), rest are body statements
            index_name = args[0]
            body = args[1:]
            filtered_body = [stmt for stmt in body if stmt is not None]
            return ForEach(str(var_name), iterable, str(index_name), filtered_body)
        else:
            # No index parameter, all args are body statements
            body = args
            filtered_body = [stmt for stmt in body if stmt is not None]
            return ForEach(str(var_name), iterable, None, filtered_body)

    def if_stmt(self, items):
        # items[0] is condition
        # items[1:] are body statements (if and optional else)
        condition = items[0]
        body_parts = items[1:]

        # Filter out None values
        filtered_parts = [part for part in body_parts if part is not None]

        # The parser gives us all statements in sequence
        # We need to find where the 'else' keyword splits them
        # For now, assume all filtered_parts are if_body statements
        # (else handling will need to be implemented separately)

        if_body = filtered_parts
        else_body = []

        return If(condition, if_body, else_body)



    def COMMENT(self, comment):
        return None  # Comments are ignored

    # Gradient transformers
    @v_args(inline=True)
    def gradient_stop(self, color, offset):
        return GradientStop(color, offset)

    @v_args(inline=True)
    def linear_gradient(self, name, x1, y1, x2, y2, *stops):
        return LinearGradient(str(name), x1, y1, x2, y2, list(stops))

    @v_args(inline=True)
    def radial_gradient(self, name, cx, cy, r, *stops):
        return RadialGradient(str(name), cx, cy, r, list(stops))

    @v_args(inline=True)
    def conic_gradient(self, name, cx, cy, angle, *stops):
        return ConicGradient(str(name), cx, cy, angle, list(stops))

    @v_args(inline=True)
    def gradient_stmt(self, gradient_obj):
        return gradient_obj

    # Animation transformers
    def animation_attr(self, args):
        if len(args) == 1:
            return str(args[0])  # Simple IDENT
        else:
            return "font-size"  # "font" "-" "size"

    def animation_property(self, args):
        # Handle variable number of arguments for optional parameters
        prop_name = args[0]  # This is now from animation_attr
        from_val = args[1]
        to_val = args[2]
        duration = str(args[3])

        repeat = "once"
        direction = "normal"
        easing = "linear"

        # Process optional arguments
        for i in range(4, len(args)):
            arg_str = str(args[i])
            if arg_str in ["once", "infinite"] or arg_str.isdigit():
                repeat = arg_str
            elif arg_str in ["normal", "reverse", "alternate", "alternate-reverse"]:
                direction = arg_str
            elif arg_str in ["linear", "ease", "ease-in", "ease-out", "ease-in-out"]:
                easing = arg_str

        return AnimationProperty(prop_name, from_val, to_val, duration, repeat, direction, easing)

    @v_args(inline=True)
    def animate_block(self, *properties):
        return AnimationBlock(list(properties))

    @v_args(inline=True)
    def logical_or_op(self, left, right):
        return LogicalOr(left, right)

    @v_args(inline=True)
    def logical_and_op(self, left, right):
        return LogicalAnd(left, right)

    @v_args(inline=True)
    def logical_not_op(self, operand):
        return LogicalNot(operand)

    def canvas_width(self, args):
        return CanvasProperty("width")

    def canvas_height(self, args):
        return CanvasProperty("height")

