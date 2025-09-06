# interpreter.py
import math
from ..core.ast import *

class Environment:
    def __init__(self):
        self.vars = {}

    def get(self, name):





        if name not in self.vars:
            raise ValueError(f"Undefined variable: {name}")
        return self.vars[name]

    def set(self, name, value):
        self.vars[name] = value


class SVGInterpreter:
    def __init__(self, ast):
        self.ast = ast
        self.env = Environment()

        # Add math constants
        import math
        self.env.set('pi', math.pi)
        self.env.set('e', math.e)
        self.env.set('tau', math.tau)  # 2 * pi

        self.canvas_width = 500
        self.canvas_height = 500
        self.background = "white"
        self.elements = []
        self.groups = {}  # Store group definitions
        self.gradients = {}  # Store gradient definitions
        self.clips = {}  # Store clip definitions

    def eval_expr(self, expr: Expr):
        if isinstance(expr, Number):
            return expr.value
        elif isinstance(expr, UnitValue):
            return expr  # Keep unit values as objects for now
        elif isinstance(expr, Boolean):
            return expr.value
        elif isinstance(expr, Var):
            # Check if it's a gradient reference first
            if expr.name in self.gradients:
                return f"url(#{expr.name})"
            return self.env.get(expr.name)
        elif isinstance(expr, String):
            return expr.value
        elif isinstance(expr, InterpolatedString):
            # Evaluate each part and concatenate
            result = ""
            for part in expr.parts:
                if isinstance(part, str):
                    # Literal string part
                    result += part
                else:
                    # Expression part - evaluate and convert to string
                    value = self.eval_expr(part)
                    result += str(value)
            return result
        elif isinstance(expr, GradientRef):
            return f"url(#{expr.name})"
        elif isinstance(expr, ArrayLiteral):
            result = []
            for elem in expr.elements:
                if isinstance(elem, list):
                    result.extend([self.eval_expr(e) for e in elem])
                else:
                    result.append(self.eval_expr(elem))
            return result
        elif isinstance(expr, ArrayAccess):
            array = self.eval_expr(expr.array)  # Evaluate the array expression (could be nested)
            index = self.eval_expr(expr.index)
            if isinstance(array, list):
                return array[int(index)]
            else:
                raise ValueError(f"Cannot access index {index} of non-array value: {array}")
        elif isinstance(expr, FunctionCall):
            return self.eval_function_call(expr)
        elif isinstance(expr, CanvasProperty):
            if expr.property == "width":
                return self.canvas_width
            elif expr.property == "height":
                return self.canvas_height
            else:
                raise ValueError(f"Unknown canvas property: {expr.property}")
        elif isinstance(expr, Rotate):
            return self.eval_expr(expr.angle)
        elif isinstance(expr, Scale):
            return self.eval_expr(expr.factor)
        elif isinstance(expr, Translate):
            return (self.eval_expr(expr.x), self.eval_expr(expr.y))
        elif isinstance(expr, BinOp):
            l = self.eval_expr(expr.left)
            r = self.eval_expr(expr.right)
            if expr.op == '+': return l + r
            if expr.op == '-': return l - r
            if expr.op == '*': return l * r
            if expr.op == '/': return l / r
            if expr.op == '%': return l % r
            if expr.op == '<': return l < r
            if expr.op == '>': return l > r
            if expr.op == '<=': return l <= r
            if expr.op == '>=': return l >= r
            if expr.op == '==': return l == r
            if expr.op == '!=': return l != r
        elif isinstance(expr, LogicalOr):
            return self.eval_logical_or(expr)
        elif isinstance(expr, LogicalAnd):
            return self.eval_logical_and(expr)
        elif isinstance(expr, LogicalNot):
            return self.eval_logical_not(expr)
        elif isinstance(expr, TernaryOp):
            condition = self.eval_expr(expr.condition)
            if condition:
                return self.eval_expr(expr.true_value)
            else:
                return self.eval_expr(expr.false_value)
        else:
            raise ValueError(f"Unknown expression: {expr}")

    def eval_function_call(self, func_call):
        """Evaluate function calls like math.sin(90deg)"""
        if func_call.module == "math":
            # Get the first argument for single-argument functions
            if len(func_call.arguments) >= 1:
                arg_value = self.eval_expr(func_call.arguments[0])
            else:
                raise ValueError(f"Function {func_call.function} requires at least 1 argument")

            # Handle unit values for trigonometric functions
            if isinstance(arg_value, UnitValue):
                if arg_value.unit == "deg":
                    # Convert degrees to radians for math functions
                    radians = math.radians(arg_value.value)
                elif arg_value.unit == "rad":
                    radians = arg_value.value
                elif arg_value.unit == "turn":
                    radians = arg_value.value * 2 * math.pi
                else:
                    radians = arg_value.value  # Assume radians if unknown unit
            else:
                # Raw number - treat as mathematical value (not degrees)
                radians = arg_value

            if func_call.function == "sin":
                if isinstance(arg_value, UnitValue) and arg_value.unit in ["deg", "rad", "turn"]:
                    return math.sin(radians)
                else:
                    return math.sin(arg_value)  # Raw mathematical sine
            elif func_call.function == "cos":
                if isinstance(arg_value, UnitValue) and arg_value.unit in ["deg", "rad", "turn"]:
                    return math.cos(radians)
                else:
                    return math.cos(arg_value)  # Raw mathematical cosine
            elif func_call.function == "tan":
                if isinstance(arg_value, UnitValue) and arg_value.unit in ["deg", "rad", "turn"]:
                    return math.tan(radians)
                else:
                    return math.tan(arg_value)  # Raw mathematical tangent
            elif func_call.function == "sqrt":
                value = arg_value.value if isinstance(arg_value, UnitValue) else arg_value
                return math.sqrt(value)
            elif func_call.function == "abs":
                value = arg_value.value if isinstance(arg_value, UnitValue) else arg_value
                return abs(value)
            elif func_call.function == "round":
                value = arg_value.value if isinstance(arg_value, UnitValue) else arg_value
                return round(value)
            elif func_call.function == "floor":
                value = arg_value.value if isinstance(arg_value, UnitValue) else arg_value
                return math.floor(value)
            elif func_call.function == "ceil":
                value = arg_value.value if isinstance(arg_value, UnitValue) else arg_value
                return math.ceil(value)
            elif func_call.function == "radians":
                value = arg_value.value if isinstance(arg_value, UnitValue) else arg_value
                return math.radians(value)  # Convert degrees to radians
            elif func_call.function == "degrees":
                value = arg_value.value if isinstance(arg_value, UnitValue) else arg_value
                return math.degrees(value)  # Convert radians to degrees
            elif func_call.function == "pow":
                # Power function - expects two arguments
                if len(func_call.arguments) == 2:
                    base = self.eval_expr(func_call.arguments[0])
                    exp = self.eval_expr(func_call.arguments[1])
                    base_val = base.value if isinstance(base, UnitValue) else base
                    exp_val = exp.value if isinstance(exp, UnitValue) else exp
                    return math.pow(base_val, exp_val)
                else:
                    raise ValueError("pow function requires exactly 2 arguments")
            elif func_call.function == "log":
                value = arg_value.value if isinstance(arg_value, UnitValue) else arg_value
                return math.log(value)  # Natural logarithm
            elif func_call.function == "log10":
                value = arg_value.value if isinstance(arg_value, UnitValue) else arg_value
                return math.log10(value)  # Base-10 logarithm
            elif func_call.function == "exp":
                value = arg_value.value if isinstance(arg_value, UnitValue) else arg_value
                return math.exp(value)  # e^x
            elif func_call.function == "min":
                # Min function - expects two arguments
                if len(func_call.arguments) == 2:
                    val1 = self.eval_expr(func_call.arguments[0])
                    val2 = self.eval_expr(func_call.arguments[1])
                    val1_num = val1.value if isinstance(val1, UnitValue) else val1
                    val2_num = val2.value if isinstance(val2, UnitValue) else val2
                    return min(val1_num, val2_num)
                else:
                    raise ValueError("min function requires exactly 2 arguments")
            elif func_call.function == "max":
                # Max function - expects two arguments
                if len(func_call.arguments) == 2:
                    val1 = self.eval_expr(func_call.arguments[0])
                    val2 = self.eval_expr(func_call.arguments[1])
                    val1_num = val1.value if isinstance(val1, UnitValue) else val1
                    val2_num = val2.value if isinstance(val2, UnitValue) else val2
                    return max(val1_num, val2_num)
                else:
                    raise ValueError("max function requires exactly 2 arguments")
            elif func_call.function == "clamp":
                # Clamp function - expects three arguments (value, min, max)
                if hasattr(func_call, 'args') and len(func_call.args) == 3:
                    value = self.eval_expr(func_call.args[0])
                    min_val = self.eval_expr(func_call.args[1])
                    max_val = self.eval_expr(func_call.args[2])
                    value_num = value.value if isinstance(value, UnitValue) else value
                    min_num = min_val.value if isinstance(min_val, UnitValue) else min_val
                    max_num = max_val.value if isinstance(max_val, UnitValue) else max_val
                    return max(min_num, min(max_num, value_num))
                else:
                    raise ValueError("clamp function requires exactly 3 arguments")
            elif func_call.function == "lerp":
                # Linear interpolation - expects three arguments (start, end, t)
                if hasattr(func_call, 'args') and len(func_call.args) == 3:
                    start = self.eval_expr(func_call.args[0])
                    end = self.eval_expr(func_call.args[1])
                    t = self.eval_expr(func_call.args[2])
                    start_num = start.value if isinstance(start, UnitValue) else start
                    end_num = end.value if isinstance(end, UnitValue) else end
                    t_num = t.value if isinstance(t, UnitValue) else t
                    return start_num + (end_num - start_num) * t_num
                else:
                    raise ValueError("lerp function requires exactly 3 arguments")
            elif func_call.function == "random":
                # Random number between 0 and 1 (argument is ignored)
                import random
                return random.random()
            elif func_call.function == "randomRange":
                # Random number between min and max
                if hasattr(func_call, 'args') and len(func_call.args) == 2:
                    min_val = self.eval_expr(func_call.args[0])
                    max_val = self.eval_expr(func_call.args[1])
                    min_num = min_val.value if isinstance(min_val, UnitValue) else min_val
                    max_num = max_val.value if isinstance(max_val, UnitValue) else max_val
                    import random
                    return random.uniform(min_num, max_num)
                else:
                    raise ValueError("randomRange function requires exactly 2 arguments")
            else:
                raise ValueError(f"Unknown math function: {func_call.function}")
        else:
            raise ValueError(f"Unknown module: {func_call.module}")

    def run(self):
        for i, stmt in enumerate(self.ast):
            if stmt is None:
                print(f"Warning: Found None statement at index {i}")
                continue
            self.exec_stmt(stmt)

    def _build_transform_attr(self, transforms, stmt=None):
        if not transforms:
            return ""

        # Ensure transforms is always a list
        if not isinstance(transforms, (list, tuple)):
            transforms = [transforms]

        # Build transformation matrix step by step to ensure correct order
        # We'll collect simple transforms and apply them in reverse order for SVG
        simple_transforms = []

        for transform in transforms:
            if isinstance(transform, Rotate):
                angle_value = self.eval_expr(transform.angle)
                if isinstance(angle_value, UnitValue):
                    if angle_value.unit == "deg":
                        angle = angle_value.value
                    elif angle_value.unit == "rad":
                        angle = math.degrees(angle_value.value)
                    elif angle_value.unit == "turn":
                        angle = angle_value.value * 360
                    else:
                        angle = angle_value.value  # Assume degrees
                else:
                    angle = angle_value  # Raw number as degrees
                # Rotate around the center of the shape
                if stmt and hasattr(stmt, 'x') and hasattr(stmt, 'y'):
                    x = self.eval_expr(stmt.x)
                    y = self.eval_expr(stmt.y)

                    # For rectangles, rotate around center
                    if hasattr(stmt, 'width') and hasattr(stmt, 'height'):
                        center_x = x + self.eval_expr(stmt.width) / 2
                        center_y = y + self.eval_expr(stmt.height) / 2
                    else:
                        # For circles and other shapes, use position as center
                        center_x = x
                        center_y = y

                    simple_transforms.append(f"rotate({angle},{center_x},{center_y})")
                else:
                    simple_transforms.append(f"rotate({angle})")

            elif isinstance(transform, Scale):
                factor = self.eval_expr(transform.factor)
                # For scale, we need to handle center-point scaling differently
                # to maintain intuitive transform order
                if stmt and hasattr(stmt, 'x') and hasattr(stmt, 'y'):
                    x = self.eval_expr(stmt.x)
                    y = self.eval_expr(stmt.y)

                    # For rectangles, scale around center
                    if hasattr(stmt, 'width') and hasattr(stmt, 'height'):
                        center_x = x + self.eval_expr(stmt.width) / 2
                        center_y = y + self.eval_expr(stmt.height) / 2
                    else:
                        # For circles and other shapes, use position as center
                        center_x = x
                        center_y = y

                    # Add the scale transformation as a single unit
                    simple_transforms.append(f"translate({center_x},{center_y}) scale({factor}) translate({-center_x},{-center_y})")
                else:
                    simple_transforms.append(f"scale({factor})")

            elif isinstance(transform, Translate):
                x = self.eval_expr(transform.x)
                y = self.eval_expr(transform.y)
                simple_transforms.append(f"translate({x},{y})")

        if simple_transforms:
            # SVG applies transforms right-to-left, but users expect left-to-right
            # So we reverse the order to make it intuitive
            return f' transform="{" ".join(reversed(simple_transforms))}"'
        return ""

    def exec_stmt(self, stmt: Statement):
        if isinstance(stmt, Canvas):
            self.canvas_width = stmt.width
            self.canvas_height = stmt.height
            self.background = stmt.background
        elif isinstance(stmt, VarDecl):
            if isinstance(stmt.value, Expr):
                # Traditional variable with expression value
                val = self.eval_expr(stmt.value)
                self.env.set(stmt.name, val)
            else:
                # Shape variable - store the statement for later use
                self.env.set(stmt.name, stmt.value)
        elif isinstance(stmt, Circle):
            x = self.eval_expr(stmt.x)
            y = self.eval_expr(stmt.y)
            r = self.eval_expr(stmt.radius)
            
            # Handle fill and stroke - they might be string literals or String objects
            if hasattr(stmt.fill, 'value'):
                fill_val = stmt.fill.value
            elif isinstance(stmt.fill, str):
                fill_val = stmt.fill
            else:
                fill_val = self.eval_expr(stmt.fill)
                
            if hasattr(stmt.stroke, 'value'):
                stroke_val = stmt.stroke.value
            elif isinstance(stmt.stroke, str):
                stroke_val = stmt.stroke
            else:
                stroke_val = self.eval_expr(stmt.stroke)
            
            # Handle stroke-width
            stroke_width_val = self.eval_expr(stmt.stroke_width) if stmt.stroke_width else 1
            stroke_width_attr = f' stroke-width="{stroke_width_val}"'
            
            # Handle opacity
            opacity_attr = ""
            if stmt.opacity is not None:
                opacity_val = self.eval_expr(stmt.opacity)
                opacity_attr = f' opacity="{opacity_val}"'
            
            transform_attr = self._build_transform_attr(stmt.transforms, stmt)

            # Use gradient if specified, otherwise use fill
            if hasattr(stmt, 'gradient') and stmt.gradient:
                fill_val = self.eval_expr(stmt.gradient)

            # Build clip attribute if clip is specified
            clip_attr = ""
            if stmt.clip:
                clip_name = stmt.clip.name
                clip_attr = f' clip-path="url(#{clip_name})"'

            if stmt.animation:
                # Generate animated circle with group wrapper for static transforms
                animation_elements = self._build_animation_elements(stmt.animation, x, y)
                
                if transform_attr:
                    # Wrap in group if we have both static transforms and animation
                    circle_elem = f'<g{transform_attr}>'
                    circle_elem += f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill_val}" stroke="{stroke_val}"{stroke_width_attr}{opacity_attr}{clip_attr}>'
                    circle_elem += animation_elements
                    circle_elem += '</circle>'
                    circle_elem += '</g>'
                else:
                    # No static transforms, animation can go directly on circle
                    circle_elem = f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill_val}" stroke="{stroke_val}"{stroke_width_attr}{opacity_attr}{clip_attr}>'
                    circle_elem += animation_elements
                    circle_elem += '</circle>'
                    
                self.elements.append(circle_elem)
            else:
                # Generate static circle
                self.elements.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill_val}" stroke="{stroke_val}"{stroke_width_attr}{opacity_attr}{transform_attr}{clip_attr}/>')
        elif isinstance(stmt, Rect):
            x = self.eval_expr(stmt.x)
            y = self.eval_expr(stmt.y)
            w = self.eval_expr(stmt.width)
            h = self.eval_expr(stmt.height)
            fill_val = self.eval_expr(stmt.fill)
            stroke_val = self.eval_expr(stmt.stroke)
            stroke_width_val = self.eval_expr(stmt.stroke_width) if stmt.stroke_width else 1
            transform_attr = self._build_transform_attr(stmt.transforms, stmt)

            # Use gradient if specified, otherwise use fill
            if hasattr(stmt, 'gradient') and stmt.gradient:
                fill_val = self.eval_expr(stmt.gradient)

            rx_attr = ""
            if stmt.rx:
                rx_val = self.eval_expr(stmt.rx)
                rx_attr = f' rx="{rx_val}" ry="{rx_val}"'  # Set both rx and ry for all corners

            # Build clip attribute if clip is specified
            clip_attr = ""
            if stmt.clip:
                clip_name = stmt.clip.name
                clip_attr = f' clip-path="url(#{clip_name})"'

            # Build stroke-width attribute
            stroke_width_attr = f' stroke-width="{stroke_width_val}"'

            if stmt.animation:
                # Generate animated rectangle with group wrapper for static transforms
                animation_elements = self._build_animation_elements(stmt.animation, x, y)
                
                if transform_attr:
                    # Wrap in group if we have both static transforms and animation
                    rect_elem = f'<g{transform_attr}>'
                    rect_elem += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill_val}" stroke="{stroke_val}"{stroke_width_attr}{rx_attr}{clip_attr}>'
                    rect_elem += animation_elements
                    rect_elem += '</rect>'
                    rect_elem += '</g>'
                else:
                    # No static transforms, animation can go directly on rectangle
                    rect_elem = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill_val}" stroke="{stroke_val}"{stroke_width_attr}{rx_attr}{clip_attr}>'
                    rect_elem += animation_elements
                    rect_elem += '</rect>'
                    
                self.elements.append(rect_elem)
            else:
                # Generate static rectangle
                self.elements.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill_val}" stroke="{stroke_val}"{stroke_width_attr}{rx_attr}{transform_attr}{clip_attr}/>')
        elif isinstance(stmt, Line):
            x1 = self.eval_expr(stmt.x1)
            y1 = self.eval_expr(stmt.y1)
            x2 = self.eval_expr(stmt.x2)
            y2 = self.eval_expr(stmt.y2)
            sw = self.eval_expr(stmt.stroke_width)
            transform_attr = self._build_transform_attr(stmt.transforms, stmt)
            stroke_val = self.eval_expr(stmt.stroke)
            self.elements.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke_val}" stroke-width="{sw}"{transform_attr}/>')
        elif isinstance(stmt, Ellipse):
            x = self.eval_expr(stmt.x)
            y = self.eval_expr(stmt.y)
            rx = self.eval_expr(stmt.rx)
            ry = self.eval_expr(stmt.ry)
            stroke_width_val = self.eval_expr(stmt.stroke_width) if stmt.stroke_width else 1
            transform_attr = self._build_transform_attr(stmt.transforms, stmt)

            fill_val = self.eval_expr(stmt.fill)
            stroke_val = self.eval_expr(stmt.stroke)

            # Use gradient if specified, otherwise use fill
            if hasattr(stmt, 'gradient') and stmt.gradient:
                fill_val = self.eval_expr(stmt.gradient)

            # Build clip attribute if clip is specified
            clip_attr = ""
            if stmt.clip:
                clip_name = stmt.clip.name
                clip_attr = f' clip-path="url(#{clip_name})"'

            # Build stroke-width attribute
            stroke_width_attr = f' stroke-width="{stroke_width_val}"'

            if stmt.animation:
                # Generate animated ellipse with group wrapper for static transforms
                animation_elements = self._build_animation_elements(stmt.animation, x, y)
                
                if transform_attr:
                    # Wrap in group if we have both static transforms and animation
                    ellipse_elem = f'<g{transform_attr}>'
                    ellipse_elem += f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill_val}" stroke="{stroke_val}"{stroke_width_attr}{clip_attr}>'
                    ellipse_elem += animation_elements
                    ellipse_elem += '</ellipse>'
                    ellipse_elem += '</g>'
                else:
                    # No static transforms, animation can go directly on ellipse
                    ellipse_elem = f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill_val}" stroke="{stroke_val}"{stroke_width_attr}{clip_attr}>'
                    ellipse_elem += animation_elements
                    ellipse_elem += '</ellipse>'
                    
                self.elements.append(ellipse_elem)
            else:
                # Generate static ellipse
                self.elements.append(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill_val}" stroke="{stroke_val}"{stroke_width_attr}{transform_attr}{clip_attr}/>')
        elif isinstance(stmt, Polygon):
            points_str = " ".join([f"{self.eval_expr(x)},{self.eval_expr(y)}" for x, y in stmt.points])
            fill_val = self.eval_expr(stmt.fill)
            stroke_val = self.eval_expr(stmt.stroke)
            self.elements.append(f'<polygon points="{points_str}" fill="{fill_val}" stroke="{stroke_val}"/>')
        elif isinstance(stmt, Text):
            x = self.eval_expr(stmt.x)
            y = self.eval_expr(stmt.y)
            font_size = self.eval_expr(stmt.font_size)
            fill_val = self.eval_expr(stmt.fill)
            stroke_val = self.eval_expr(stmt.stroke)
            stroke_width_val = self.eval_expr(stmt.stroke_width) if stmt.stroke_width else 1
            content = self.eval_expr(stmt.content)
            transform_attr = self._build_transform_attr(stmt.transforms, stmt)

            # Build clip attribute if clip is specified
            clip_attr = ""
            if stmt.clip:
                clip_name = stmt.clip.name
                clip_attr = f' clip-path="url(#{clip_name})"'

            # Build stroke attributes
            stroke_attrs = ""
            if stroke_val != 'none':
                stroke_attrs = f' stroke="{stroke_val}" stroke-width="{stroke_width_val}"'

            if stmt.animation:
                # Generate animated text with group wrapper for static transforms
                animation_elements = self._build_animation_elements(stmt.animation, x, y)
                
                if transform_attr:
                    # Wrap in group if we have both static transforms and animation
                    text_elem = f'<g{transform_attr}>'
                    text_elem += f'<text x="{x}" y="{y}" fill="{fill_val}" font-size="{font_size}"{stroke_attrs}{clip_attr}>'
                    text_elem += animation_elements
                    text_elem += f'{content}</text>'
                    text_elem += '</g>'
                else:
                    # No static transforms, animation can go directly on text
                    text_elem = f'<text x="{x}" y="{y}" fill="{fill_val}" font-size="{font_size}"{stroke_attrs}{clip_attr}>'
                    text_elem += animation_elements
                    text_elem += f'{content}</text>'
                    
                self.elements.append(text_elem)
            else:
                # Generate static text
                self.elements.append(f'<text x="{x}" y="{y}" fill="{fill_val}" font-size="{font_size}"{stroke_attrs}{transform_attr}{clip_attr}>{content}</text>')
        elif isinstance(stmt, Path):
            stroke_width = self.eval_expr(stmt.stroke_width)
            fill_val = self.eval_expr(stmt.fill)
            stroke_val = self.eval_expr(stmt.stroke)
            transform_attr = self._build_transform_attr(stmt.transforms, stmt)

            # Use gradient if specified, otherwise use fill
            if hasattr(stmt, 'gradient') and stmt.gradient:
                fill_val = self.eval_expr(stmt.gradient)

            # Build clip attribute if clip is specified
            clip_attr = ""
            if hasattr(stmt, 'clip') and stmt.clip:
                clip_name = stmt.clip.name
                clip_attr = f' clip-path="url(#{clip_name})"'

            self.elements.append(f'<path d="{stmt.path_data}" fill="{fill_val}" stroke="{stroke_val}" stroke-width="{stroke_width}"{transform_attr}{clip_attr}/>')
        elif isinstance(stmt, Arc):
            x = self.eval_expr(stmt.x)
            y = self.eval_expr(stmt.y)
            rx = self.eval_expr(stmt.rx)
            ry = self.eval_expr(stmt.ry)
            start_angle = self.eval_expr(stmt.start_angle)
            end_angle = self.eval_expr(stmt.end_angle)
            # Convert angles to radians and create arc path
            import math
            start_rad = math.radians(start_angle)
            end_rad = math.radians(end_angle)
            x1 = x + rx * math.cos(start_rad)
            y1 = y + ry * math.sin(start_rad)
            x2 = x + rx * math.cos(end_rad)
            y2 = y + ry * math.sin(end_rad)
            large_arc = 1 if abs(end_angle - start_angle) > 180 else 0
            sweep = 1 if end_angle > start_angle else 0
            path_data = f"M {x1},{y1} A {rx},{ry} 0 {large_arc},{sweep} {x2},{y2}"
            fill_val = self.eval_expr(stmt.fill)
            stroke_val = self.eval_expr(stmt.stroke)
            self.elements.append(f'<path d="{path_data}" fill="{fill_val}" stroke="{stroke_val}"/>')
        elif isinstance(stmt, Curve):
            x1 = self.eval_expr(stmt.x1)
            y1 = self.eval_expr(stmt.y1)
            x2 = self.eval_expr(stmt.x2)
            y2 = self.eval_expr(stmt.y2)
            cx1 = self.eval_expr(stmt.cx1)
            cy1 = self.eval_expr(stmt.cy1)
            cx2 = self.eval_expr(stmt.cx2)
            cy2 = self.eval_expr(stmt.cy2)
            stroke_width = self.eval_expr(stmt.stroke_width)
            path_data = f"M {x1},{y1} C {cx1},{cy1} {cx2},{cy2} {x2},{y2}"
            stroke_val = self.eval_expr(stmt.stroke)
            self.elements.append(f'<path d="{path_data}" fill="none" stroke="{stroke_val}" stroke-width="{stroke_width}"/>')
        elif isinstance(stmt, Polygon):
            # Build the points string for the polygon
            points_str = ""
            for point in stmt.points:
                x = self.eval_expr(point[0])
                y = self.eval_expr(point[1])
                points_str += f"{x},{y} "
            points_str = points_str.strip()
            
            fill_val = self.eval_expr(stmt.fill) if hasattr(stmt, 'fill') and stmt.fill else 'none'
            stroke_val = self.eval_expr(stmt.stroke) if hasattr(stmt, 'stroke') and stmt.stroke else 'black'
            
            self.elements.append(f'<polygon points="{points_str}" fill="{fill_val}" stroke="{stroke_val}"/>')
        elif isinstance(stmt, GroupDef):
            # Store group definition for later use
            self.groups[stmt.name] = stmt
        elif isinstance(stmt, GroupUse):
            # Check if it's a shape variable first
            if stmt.name in self.env.vars:
                shape_stmt = self.env.get(stmt.name)
                # Check if it's a shape statement (has position and rendering properties)
                if isinstance(shape_stmt, (Circle, Rect, Ellipse, Polygon, Text, Path, Arc, Curve, Line)):
                    # It's a shape variable - create a copy with new position
                    self.use_shape_variable(stmt, shape_stmt)
                else:
                    # Use a group definition
                    self.use_group(stmt)
            else:
                # Use a group definition
                self.use_group(stmt)
        elif isinstance(stmt, LinearGradient):
            # Store linear gradient definition
            self.gradients[stmt.name] = stmt
        elif isinstance(stmt, RadialGradient):
            # Store radial gradient definition
            self.gradients[stmt.name] = stmt
        elif isinstance(stmt, ConicGradient):
            # Store conic gradient definition
            self.gradients[stmt.name] = stmt
        elif isinstance(stmt, ClipDef):
            # Store clip definition
            self.clips[stmt.name] = stmt

        elif isinstance(stmt, Repeat):
            for i in range(stmt.times):
                # Only set the variable if it's not the discard symbol
                if stmt.var_name != '_':
                    self.env.set(stmt.var_name, i)
                for s in stmt.body:
                    self.exec_stmt(s)
        elif isinstance(stmt, While):
            while self.eval_expr(stmt.condition):
                for s in stmt.body:
                    self.exec_stmt(s)
        elif isinstance(stmt, For):
            start_val = self.eval_expr(stmt.start)
            end_val = self.eval_expr(stmt.end)
            for i in range(int(start_val), int(end_val) + 1):
                self.env.set(stmt.var_name, i)
                for s in stmt.body:
                    self.exec_stmt(s)
        elif isinstance(stmt, ForEach):
            iterable_val = self.eval_expr(stmt.iterable)
            if isinstance(iterable_val, list):
                for index, item in enumerate(iterable_val):
                    self.env.set(stmt.var_name, item)
                    if stmt.index_name is not None:
                        self.env.set(stmt.index_name, index)
                    for s in stmt.body:
                        self.exec_stmt(s)
            else:
                raise ValueError(f"Cannot iterate over non-array value: {iterable_val}")
        elif isinstance(stmt, If):
            condition_result = self.eval_expr(stmt.condition)
            if condition_result:
                for s in stmt.if_body:
                    self.exec_stmt(s)
            else:
                for s in stmt.else_body:
                    self.exec_stmt(s)

        else:
            raise ValueError(f"Unknown statement: {stmt}")

    def use_group(self, group_use):
        """Use a group definition with positioning and properties"""
        if group_use.name not in self.groups:
            raise ValueError(f"Group '{group_use.name}' not defined. Available groups: {list(self.groups.keys())}")

        group_def = self.groups[group_use.name]
        x = self.eval_expr(group_use.x)
        y = self.eval_expr(group_use.y)

        # Save current environment
        old_env = self.env
        self.env = Environment()

        # Set position variables for relative positioning
        self.env.set('x', x)
        self.env.set('y', y)

        # Set fill and stroke if provided
        if group_use.fill:
            fill_val = self.eval_expr(group_use.fill)
            self.env.set('fill', fill_val)
        if group_use.stroke:
            stroke_val = self.eval_expr(group_use.stroke)
            self.env.set('stroke', stroke_val)

        # Start a new group element
        self.elements.append(f'<g id="{group_use.name}_{len(self.elements)}">')

        # Execute group body with relative positioning
        for stmt in group_def.body:
            self.exec_stmt_with_offset(stmt, x, y)

        # End group element
        self.elements.append('</g>')

        # Restore environment
        self.env = old_env

    def use_shape_variable(self, group_use, shape_stmt):
        """Use a shape variable with new positioning and properties"""
        import copy

        # Create a deep copy of the shape statement
        new_shape = copy.deepcopy(shape_stmt)

        # Update position (these are expressions, not direct values)
        new_shape.x = group_use.x
        new_shape.y = group_use.y

        # Override fill and stroke if provided
        if group_use.fill:
            new_shape.fill = group_use.fill
        if group_use.stroke:
            new_shape.stroke = group_use.stroke

        # Apply transforms if provided
        if group_use.transforms:
            if hasattr(new_shape, 'transforms'):
                new_shape.transforms = group_use.transforms
            else:
                # Add transforms attribute if it doesn't exist
                new_shape.transforms = group_use.transforms

        # Execute the modified shape
        self.exec_stmt(new_shape)

    def exec_stmt_with_offset(self, stmt, offset_x, offset_y):
        """Execute a statement with coordinate offset for relative positioning"""
        # Create a copy of the statement with offset coordinates
        if isinstance(stmt, Circle):
            # Apply offset to circle position
            new_x = BinOp(stmt.x, '+', Number(offset_x))
            new_y = BinOp(stmt.y, '+', Number(offset_y))
            new_stmt = Circle(stmt.radius, new_x, new_y, stmt.fill, stmt.stroke, stmt.transforms)
            self.exec_stmt(new_stmt)
        elif isinstance(stmt, Rect):
            # Apply offset to rectangle position
            new_x = BinOp(stmt.x, '+', Number(offset_x))
            new_y = BinOp(stmt.y, '+', Number(offset_y))
            new_stmt = Rect(stmt.width, stmt.height, new_x, new_y, stmt.fill, stmt.stroke, stmt.transforms, stmt.rx)
            self.exec_stmt(new_stmt)
        elif isinstance(stmt, Line):
            # Apply offset to line coordinates
            new_x1 = BinOp(stmt.x1, '+', Number(offset_x))
            new_y1 = BinOp(stmt.y1, '+', Number(offset_y))
            new_x2 = BinOp(stmt.x2, '+', Number(offset_x))
            new_y2 = BinOp(stmt.y2, '+', Number(offset_y))
            new_stmt = Line(new_x1, new_y1, new_x2, new_y2, stmt.stroke, stmt.stroke_width, stmt.transforms)
            self.exec_stmt(new_stmt)
        elif isinstance(stmt, Ellipse):
            # Apply offset to ellipse position
            new_x = BinOp(stmt.x, '+', Number(offset_x))
            new_y = BinOp(stmt.y, '+', Number(offset_y))
            new_stmt = Ellipse(stmt.rx, stmt.ry, new_x, new_y, stmt.fill, stmt.stroke, stmt.transforms)
            self.exec_stmt(new_stmt)
        elif isinstance(stmt, Text):
            # Apply offset to text position
            new_x = BinOp(stmt.x, '+', Number(offset_x))
            new_y = BinOp(stmt.y, '+', Number(offset_y))
            new_stmt = Text(stmt.content, new_x, new_y, stmt.fill, stmt.font_size, stmt.transforms)
            new_stmt.animation = stmt.animation
            self.exec_stmt(new_stmt)
        else:
            # For other statements, execute normally
            self.exec_stmt(stmt)

    def get_svg(self):
        """Generate and return SVG as string"""
        svg_lines = []
        svg_lines.append(f'<svg width="{self.canvas_width}" height="{self.canvas_height}" xmlns="http://www.w3.org/2000/svg">')

        # Add gradients and clips in defs section if any exist
        if self.gradients or self.clips:
            svg_lines.append('<defs>')
            for gradient_name, gradient in self.gradients.items():
                svg_lines.append(self._build_gradient_svg(gradient))
            for clip_name, clip in self.clips.items():
                svg_lines.append(self._build_clip_svg(clip))
            svg_lines.append('</defs>')

        svg_lines.append(f'<rect width="100%" height="100%" fill="{self.background}"/>')

        # Add all elements
        for el in self.elements:
            svg_lines.append(el)
        svg_lines.append('</svg>')

        return '\n'.join(svg_lines)

    def _build_gradient_svg(self, gradient):
        """Build SVG gradient definition"""
        if isinstance(gradient, LinearGradient):
            x1 = self.eval_expr(gradient.x1)
            y1 = self.eval_expr(gradient.y1)
            x2 = self.eval_expr(gradient.x2)
            y2 = self.eval_expr(gradient.y2)

            gradient_svg = f'<linearGradient id="{gradient.name}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">'
            for stop in gradient.stops:
                color = self.eval_expr(stop.color)
                offset = self.eval_expr(stop.offset)
                gradient_svg += f'<stop offset="{offset}" stop-color="{color}"/>'
            gradient_svg += '</linearGradient>'
            return gradient_svg

        elif isinstance(gradient, RadialGradient):
            cx = self.eval_expr(gradient.cx)
            cy = self.eval_expr(gradient.cy)
            r = self.eval_expr(gradient.r)

            gradient_svg = f'<radialGradient id="{gradient.name}" cx="{cx}" cy="{cy}" r="{r}">'
            for stop in gradient.stops:
                color = self.eval_expr(stop.color)
                offset = self.eval_expr(stop.offset)
                gradient_svg += f'<stop offset="{offset}" stop-color="{color}"/>'
            gradient_svg += '</radialGradient>'
            return gradient_svg

        elif isinstance(gradient, ConicGradient):
            # SVG doesn't natively support conic gradients, so we'll simulate with a radial gradient
            # that approximates the conic effect by using multiple color stops
            cx = self.eval_expr(gradient.cx)
            cy = self.eval_expr(gradient.cy)
            angle = self.eval_expr(gradient.angle)

            # For now, create a radial gradient that cycles through the colors
            # This is a simplified approximation - true conic gradients would need SVG 2.0 or JavaScript
            gradient_svg = f'<radialGradient id="{gradient.name}" cx="0.5" cy="0.5" r="0.5">'
            
            # Use the stops from the conic gradient but arrange them radially
            for stop in gradient.stops:
                color = self.eval_expr(stop.color)
                offset = self.eval_expr(stop.offset)
                gradient_svg += f'<stop offset="{offset}" stop-color="{color}"/>'
            
            gradient_svg += '</radialGradient>'
            return gradient_svg

        return ""

    def _build_clip_svg(self, clip):
        """Build SVG for a clip definition"""
        # Create a temporary interpreter to render the clip shapes
        clip_interpreter = SVGInterpreter([])
        clip_interpreter.canvas_width = self.canvas_width
        clip_interpreter.canvas_height = self.canvas_height

        # Execute the clip shapes
        for shape in clip.shapes:
            clip_interpreter.exec_stmt(shape)

        # Build clipPath element
        clip_elements = []
        for element in clip_interpreter.elements:
            clip_elements.append(element)

        return f'<clipPath id="{clip.name}">{"".join(clip_elements)}</clipPath>'

    def _build_animation_elements(self, animation_block, base_x=0, base_y=0):
        """Build SVG animation elements"""
        if not animation_block or not animation_block.properties:
            return ""

        animation_elements = ""

        for prop in animation_block.properties:
            from_val = self.eval_expr(prop.from_value)
            to_val = self.eval_expr(prop.to_value)

            # Map property names to SVG attributes
            if prop.property_name == "x":
                # For position animations, use animateTransform
                values = f"{from_val - base_x},0;{to_val - base_x},0"
                animation_elements += f'<animateTransform attributeName="transform" type="translate" values="{values}" dur="{prop.duration}" repeatCount="{self._convert_repeat(prop.repeat)}" direction="{prop.direction}"/>'
            elif prop.property_name == "y":
                values = f"0,{from_val - base_y};0,{to_val - base_y}"
                animation_elements += f'<animateTransform attributeName="transform" type="translate" values="{values}" dur="{prop.duration}" repeatCount="{self._convert_repeat(prop.repeat)}" direction="{prop.direction}"/>'
            elif prop.property_name == "rotate":
                values = f"{from_val};{to_val}"
                animation_elements += f'<animateTransform attributeName="transform" type="rotate" values="{values}" dur="{prop.duration}" repeatCount="{self._convert_repeat(prop.repeat)}" direction="{prop.direction}"/>'
            elif prop.property_name == "scale":
                values = f"{from_val};{to_val}"
                animation_elements += f'<animateTransform attributeName="transform" type="scale" values="{values}" dur="{prop.duration}" repeatCount="{self._convert_repeat(prop.repeat)}" direction="{prop.direction}"/>'
            else:
                # For other properties, use animate
                values = f"{from_val};{to_val}"
                animation_elements += f'<animate attributeName="{prop.property_name}" values="{values}" dur="{prop.duration}" repeatCount="{self._convert_repeat(prop.repeat)}" direction="{prop.direction}"/>'

        return animation_elements

    def _convert_repeat(self, repeat):
        """Convert repeat value to SVG format"""
        if repeat == "once":
            return "1"
        elif repeat == "infinite":
            return "indefinite"
        else:
            return repeat

    def eval_logical_or(self, node):
        """Evaluate logical OR (||) operator"""
        left_val = self.eval_expr(node.left)
        # Short-circuit evaluation: if left is truthy, return True
        if self._is_truthy(left_val):
            return True
        # Otherwise evaluate right side
        right_val = self.eval_expr(node.right)
        return self._is_truthy(right_val)

    def eval_logical_and(self, node):
        """Evaluate logical AND (&&) operator"""
        left_val = self.eval_expr(node.left)
        # Short-circuit evaluation: if left is falsy, return False
        if not self._is_truthy(left_val):
            return False
        # Otherwise evaluate right side
        right_val = self.eval_expr(node.right)
        return self._is_truthy(right_val)

    def eval_logical_not(self, node):
        """Evaluate logical NOT (!) operator"""
        operand_val = self.eval_expr(node.operand)
        return not self._is_truthy(operand_val)

    def _is_truthy(self, value):
        """Determine if a value is truthy in SVG Lang context"""
        if isinstance(value, bool):
            return value
        elif isinstance(value, (int, float)):
            return value != 0
        elif isinstance(value, str):
            return value != "" and value.lower() != "false"
        else:
            return bool(value)

    def save(self, filename="output.svg"):
        with open(filename, 'w') as f:
            f.write(self.get_svg())
        print(f"SVG saved to {filename}")
