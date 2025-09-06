# statement_transformer.py - Statement and shape transformations
from __future__ import annotations

from lark import v_args

from .expression_transformer import ExpressionTransformer
from ...core.ast import (
    AnimationBlock,
    AnimationProperty,
    Arc,
    Canvas,
    Circle,
    ClipDef,
    ClipRef,
    ConicGradient,
    Curve,
    Ellipse,
    For,
    ForEach,
    GradientRef,
    GradientStop,
    GroupDef,
    GroupUse,
    If,
    Line,
    LinearGradient,
    LogicalAnd,
    LogicalNot,
    LogicalOr,
    Number,
    Path,
    Polygon,
    RadialGradient,
    Rect,
    Repeat,
    Rotate,
    Scale,
    String,
    Text,
    Transform,
    Translate,
    VarDecl,
    While,
)


class StatementTransformer(ExpressionTransformer):
    """Transformer for statements and shapes."""

    @v_args(inline=True)
    def canvas_stmt(self, width, height, bg=None):
        if bg:
            bg_str = str(bg)
            if bg_str.startswith('"') and bg_str.endswith('"'):
                bg = bg_str[1:-1]
            else:
                bg = bg_str
        else:
            bg = 'white'
        return Canvas(int(width), int(height), bg)

    def circle_stmt(self, args):
        """Transform circle statements."""
        radius, x, y = args[0], args[1], args[2]

        fill_val = String('none')
        stroke_val = String('black')
        stroke_width_val = Number(1)
        opacity_val = None
        transform_list = []
        gradient_ref = None
        clip_ref = None
        animation_block = None

        # Process remaining arguments
        i = 3
        while i < len(args):
            arg = args[i]
            if isinstance(arg, dict):  # shape_attributes
                if 'fill' in arg:
                    fill_val = arg['fill']
                if 'stroke' in arg:
                    stroke_val = arg['stroke']
                if 'stroke_width' in arg:
                    stroke_width_val = arg['stroke_width']
                if 'opacity' in arg:
                    opacity_val = arg['opacity']
                if 'gradient' in arg:
                    gradient_ref = GradientRef(arg['gradient'])
                if 'clip' in arg:
                    clip_ref = ClipRef(arg['clip'])
                if 'transforms' in arg:
                    transform_list.extend(arg['transforms'])
            elif isinstance(arg, tuple) and len(arg) == 2:
                prop_name, prop_value = arg
                if prop_name == 'fill':
                    fill_val = prop_value
                elif prop_name == 'stroke':
                    stroke_val = prop_value
                elif prop_name in {'stroke_width', 'width'}:
                    stroke_width_val = prop_value
                elif prop_name == 'gradient':
                    gradient_ref = GradientRef(prop_value)
                elif prop_name == 'clip':
                    clip_ref = ClipRef(prop_value)
            elif isinstance(arg, list):  # transform_list
                transform_list = arg
            elif hasattr(arg, '__class__') and arg.__class__.__name__ in ['Rotate', 'Scale', 'Translate']:  # individual transform
                transform_list.append(arg)
            elif isinstance(arg, AnimationBlock):  # animation block
                animation_block = arg
            i += 1

        return Circle(
            radius=radius,
            x=x,
            y=y,
            fill=fill_val.value if hasattr(fill_val, 'value') else fill_val,
            stroke=stroke_val.value if hasattr(stroke_val, 'value') else stroke_val,
            stroke_width=stroke_width_val,
            opacity=opacity_val,
            transforms=transform_list,
            animation=animation_block,
            clip=clip_ref,
            gradient=gradient_ref
        )

    def rect_stmt(self, args):
        """Transform rectangle statements."""
        width, height, x, y = args[0], args[1], args[2], args[3]

        fill_val = String('none')
        stroke_val = String('black')
        stroke_width = None
        transform_list = []
        rx_val = None
        gradient_ref = None
        clip_ref = None
        animation_block = None

        # Process remaining arguments
        i = 4
        while i < len(args):
            arg = args[i]
            if isinstance(arg, dict):  # shape_attributes
                if 'fill' in arg:
                    fill_val = arg['fill']
                if 'stroke' in arg:
                    stroke_val = arg['stroke']
                if 'stroke_width' in arg:
                    stroke_width = arg['stroke_width']
                if 'rx' in arg:
                    rx_val = arg['rx']
                if 'gradient' in arg:
                    gradient_ref = GradientRef(arg['gradient'])
                if 'clip' in arg:
                    clip_ref = ClipRef(arg['clip'])
                if 'transforms' in arg:
                    transform_list.extend(arg['transforms'])
            elif isinstance(arg, tuple) and len(arg) == 2:
                prop_name, prop_value = arg
                if prop_name == 'fill':
                    fill_val = prop_value
                elif prop_name == 'stroke':
                    stroke_val = prop_value
                elif prop_name == 'stroke_width':
                    stroke_width = prop_value
                elif prop_name == 'rx':
                    rx_val = prop_value
                elif prop_name == 'gradient':
                    gradient_ref = GradientRef(prop_value)
                elif prop_name == 'clip':
                    clip_ref = ClipRef(prop_value)
            elif isinstance(arg, list):  # transform_list
                transform_list = arg
            elif hasattr(arg, '__class__') and arg.__class__.__name__ in ['Rotate', 'Scale', 'Translate']:  # individual transform
                transform_list.append(arg)
            elif isinstance(arg, AnimationBlock):  # animation block
                animation_block = arg
            i += 1

        rect = Rect(
            width=width,
            height=height,
            x=x,
            y=y,
            fill=fill_val,
            stroke=stroke_val,
            stroke_width=stroke_width or Number(1),
            transforms=transform_list,
            rx=rx_val,
            animation=animation_block,
            clip=clip_ref
        )
        
        if gradient_ref:
            rect.gradient = gradient_ref

        return rect

    def line_stmt(self, args):
        """Transform line statements."""
        x1, y1, x2, y2 = args[0], args[1], args[2], args[3]

        stroke_val = String('black')
        stroke_width = Number(1)
        transform_list = []
        gradient_ref = None
        clip_ref = None
        animation_block = None

        # Process remaining arguments
        i = 4
        while i < len(args):
            arg = args[i]
            if isinstance(arg, dict):  # shape_attributes
                if 'stroke' in arg:
                    stroke_val = arg['stroke']
                if 'stroke_width' in arg:
                    stroke_width = arg['stroke_width']
                if 'gradient' in arg:
                    gradient_ref = GradientRef(arg['gradient'])
                if 'clip' in arg:
                    clip_ref = ClipRef(arg['clip'])
                if 'transforms' in arg:
                    transform_list.extend(arg['transforms'])
            elif isinstance(arg, tuple) and len(arg) == 2:
                prop_name, prop_value = arg
                if prop_name == 'stroke':
                    stroke_val = prop_value
                elif prop_name == 'stroke_width':
                    stroke_width = prop_value
                elif prop_name == 'gradient':
                    gradient_ref = GradientRef(prop_value)
                elif prop_name == 'clip':
                    clip_ref = ClipRef(prop_value)
            elif isinstance(arg, list):  # transform_list
                transform_list = arg
            elif isinstance(arg, AnimationBlock):  # animation block
                animation_block = arg
            i += 1

        return Line(
            x1=x1,
            y1=y1, 
            x2=x2,
            y2=y2,
            stroke=stroke_val,
            stroke_width=stroke_width,
            transforms=transform_list
        )

    @v_args(inline=True)
    def var_stmt(self, name, value):
        return VarDecl(str(name), value)

    def ellipse_stmt(self, args):
        """Transform ellipse statements."""
        rx, ry, x, y = args[0], args[1], args[2], args[3]

        fill_val = String('none')
        stroke_val = String('black')
        stroke_width = None
        transform_list = []
        gradient_ref = None
        clip_ref = None
        animation_block = None

        # Process remaining arguments
        i = 4
        while i < len(args):
            arg = args[i]
            if isinstance(arg, dict):  # shape_attributes
                if 'fill' in arg:
                    fill_val = arg['fill']
                if 'stroke' in arg:
                    stroke_val = arg['stroke']
                if 'stroke_width' in arg:
                    stroke_width = arg['stroke_width']
                if 'gradient' in arg:
                    gradient_ref = GradientRef(arg['gradient'])
                if 'clip' in arg:
                    clip_ref = ClipRef(arg['clip'])
                if 'transforms' in arg:
                    transform_list.extend(arg['transforms'])
            elif isinstance(arg, tuple) and len(arg) == 2:
                prop_name, prop_value = arg
                if prop_name == 'fill':
                    fill_val = prop_value
                elif prop_name == 'stroke':
                    stroke_val = prop_value
                elif prop_name == 'stroke_width':
                    stroke_width = prop_value
                elif prop_name == 'gradient':
                    gradient_ref = GradientRef(prop_value)
                elif prop_name == 'clip':
                    clip_ref = ClipRef(prop_value)
            elif isinstance(arg, list):  # transform_list
                transform_list = arg
            elif isinstance(arg, AnimationBlock):
                animation_block = arg
            i += 1

        ellipse = Ellipse(
            rx=rx,
            ry=ry,
            x=x,
            y=y,
            fill=fill_val,
            stroke=stroke_val,
            stroke_width=stroke_width or Number(1),
            transforms=transform_list,
            animation=animation_block,
            clip=clip_ref
        )
        
        if gradient_ref:
            ellipse.gradient = gradient_ref

        return ellipse

    def polygon_stmt(self, args):
        """Transform polygon statements."""
        point_list = args[0]
        
        # Extract points from the point_list tree
        points = []
        for point in point_list.children:
            x_val = point.children[0]
            y_val = point.children[1]
            points.append((x_val, y_val))

        fill_val = String('none')
        stroke_val = String('black')
        transform_list = []
        gradient_ref = None
        clip_ref = None
        animation_block = None

        # Process remaining arguments
        i = 1
        while i < len(args):
            arg = args[i]
            if isinstance(arg, dict):  # shape_attributes
                if 'fill' in arg:
                    fill_val = arg['fill']
                if 'stroke' in arg:
                    stroke_val = arg['stroke']
                if 'gradient' in arg:
                    gradient_ref = GradientRef(arg['gradient'])
                if 'clip' in arg:
                    clip_ref = ClipRef(arg['clip'])
                if 'transforms' in arg:
                    transform_list.extend(arg['transforms'])
            elif isinstance(arg, tuple) and len(arg) == 2:
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
            i += 1
        
        return Polygon(
            points=points,
            fill=fill_val,
            stroke=stroke_val
        )

    @v_args(inline=True)
    def text_stmt(self, *args):
        """Transform text statements."""
        content, x, y = args[0], args[1], args[2]

        fill_val = String('black')
        stroke_val = String('none')
        stroke_width = None
        font_size_val = Number(16)
        transform_list = []
        clip_ref = None
        animation_block = None

        # Process remaining arguments
        i = 3
        while i < len(args):
            arg = args[i]
            if isinstance(arg, dict):  # shape_attributes
                if 'fill' in arg:
                    fill_val = arg['fill']
                if 'stroke' in arg:
                    stroke_val = arg['stroke']
                if 'stroke_width' in arg:
                    stroke_width = arg['stroke_width']
                if 'font-size' in arg:  # Use hyphen, not underscore!
                    font_size_val = arg['font-size']
                if 'clip' in arg:
                    clip_ref = ClipRef(arg['clip'])
            elif isinstance(arg, tuple) and len(arg) == 2:
                prop_name, prop_value = arg
                if prop_name == 'fill':
                    fill_val = prop_value
                elif prop_name == 'stroke':
                    stroke_val = prop_value
                elif prop_name == 'stroke_width':
                    stroke_width = prop_value
                elif prop_name == 'font-size':
                    font_size_val = prop_value
                elif prop_name == 'clip':
                    clip_ref = ClipRef(prop_value)
            elif isinstance(arg, list):  # transform_list
                transform_list = arg
            elif isinstance(arg, AnimationBlock):  # animation block
                animation_block = arg
            i += 1

        text = Text(
            content=content,
            x=x,
            y=y,
            fill=fill_val,
            stroke=stroke_val,
            stroke_width=stroke_width or Number(1),
            font_size=font_size_val,
            transforms=transform_list,
            animation=animation_block,
            clip=clip_ref
        )
        return text

    def path_stmt(self, args):
        """Transform path statements."""
        path_data = args[0]
        
        # Remove quotes from string if present
        if isinstance(path_data, str) and path_data.startswith('"') and path_data.endswith('"'):
            path_data = path_data[1:-1]
        elif hasattr(path_data, 'value'):
            path_data = path_data.value
            if path_data.startswith('"') and path_data.endswith('"'):
                path_data = path_data[1:-1]
        
        fill_val = String('none')
        stroke_val = String('black')
        stroke_width_val = Number(1)
        transform_list = []
        gradient_ref = None
        clip_ref = None

        # Process remaining arguments
        i = 1
        while i < len(args):
            arg = args[i]
            if isinstance(arg, dict):  # shape_attributes
                if 'fill' in arg:
                    fill_val = arg['fill']
                if 'stroke' in arg:
                    stroke_val = arg['stroke']
                if 'stroke_width' in arg:
                    stroke_width_val = arg['stroke_width']
                if 'gradient' in arg:
                    gradient_ref = GradientRef(arg['gradient'])
                if 'clip' in arg:
                    clip_ref = ClipRef(arg['clip'])
                if 'transforms' in arg:
                    transform_list.extend(arg['transforms'])
            elif isinstance(arg, tuple) and len(arg) == 2:
                prop_name, prop_value = arg
                if prop_name == 'fill':
                    fill_val = prop_value
                elif prop_name == 'stroke':
                    stroke_val = prop_value
                elif prop_name == 'stroke_width':
                    stroke_width_val = prop_value
                elif prop_name == 'gradient':
                    gradient_ref = GradientRef(prop_value)
                elif prop_name == 'clip':
                    clip_ref = ClipRef(prop_value)
            elif isinstance(arg, list):  # transform_list
                transform_list = arg
            elif hasattr(arg, '__class__') and arg.__class__.__name__ in ['Rotate', 'Scale', 'Translate']:
                transform_list.append(arg)
            i += 1

        path = Path(
            path_data=path_data,
            fill=fill_val,
            stroke=stroke_val, 
            stroke_width=stroke_width_val,
            transforms=transform_list
        )
        if gradient_ref:
            path.gradient = gradient_ref
        if clip_ref:
            path.clip = clip_ref
        return path

    def arc_stmt(self, args):
        """Transform arc statements."""
        rx, ry, x, y, start_angle, end_angle = args[0], args[1], args[2], args[3], args[4], args[5]
        
        fill_val = String('none')
        stroke_val = String('black')
        transform_list = []
        gradient_ref = None
        clip_ref = None

        # Process remaining arguments
        i = 6
        while i < len(args):
            arg = args[i]
            if isinstance(arg, dict):  # shape_attributes
                if 'fill' in arg:
                    fill_val = arg['fill']
                if 'stroke' in arg:
                    stroke_val = arg['stroke']
                if 'gradient' in arg:
                    gradient_ref = GradientRef(arg['gradient'])
                if 'clip' in arg:
                    clip_ref = ClipRef(arg['clip'])
                if 'transforms' in arg:
                    transform_list.extend(arg['transforms'])
            elif isinstance(arg, tuple) and len(arg) == 2:
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
            elif hasattr(arg, '__class__') and arg.__class__.__name__ in ['Rotate', 'Scale', 'Translate']:
                transform_list.append(arg)
            i += 1

        arc = Arc(rx, ry, x, y, start_angle, end_angle, fill_val, stroke_val, transform_list)
        if gradient_ref:
            arc.gradient = gradient_ref
        if clip_ref:
            arc.clip = clip_ref
        return arc

    def curve_stmt(self, args):
        """Transform curve statements."""
        x1, y1, x2, y2, cx1, cy1, cx2, cy2 = args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7]
        
        stroke_val = String('black')
        stroke_width_val = Number(1)
        fill_val = String('none')
        transform_list = []
        gradient_ref = None
        clip_ref = None

        # Process remaining arguments
        i = 8
        while i < len(args):
            arg = args[i]
            if isinstance(arg, dict):  # shape_attributes
                if 'fill' in arg:
                    fill_val = arg['fill']
                if 'stroke' in arg:
                    stroke_val = arg['stroke']
                if 'stroke-width' in arg or 'width' in arg:
                    stroke_width_val = arg.get('stroke-width', arg.get('width'))
                if 'gradient' in arg:
                    gradient_ref = GradientRef(arg['gradient'])
                if 'clip' in arg:
                    clip_ref = ClipRef(arg['clip'])
                if 'transforms' in arg:
                    transform_list.extend(arg['transforms'])
            elif isinstance(arg, tuple) and len(arg) == 2:
                prop_name, prop_value = arg
                if prop_name == 'fill':
                    fill_val = prop_value
                elif prop_name == 'stroke':
                    stroke_val = prop_value
                elif prop_name in ['stroke-width', 'width']:
                    stroke_width_val = prop_value
                elif prop_name == 'gradient':
                    gradient_ref = GradientRef(prop_value)
                elif prop_name == 'clip':
                    clip_ref = ClipRef(prop_value)
            elif isinstance(arg, list):  # transform_list
                transform_list = arg
            elif hasattr(arg, '__class__') and arg.__class__.__name__ in ['Rotate', 'Scale', 'Translate']:
                transform_list.append(arg)
            i += 1

        curve = Curve(x1, y1, x2, y2, cx1, cy1, cx2, cy2, stroke_val, stroke_width_val, fill_val, transform_list)
        if gradient_ref:
            curve.gradient = gradient_ref
        if clip_ref:
            curve.clip = clip_ref
        return curve

    @v_args(inline=True)
    def group_def(self, name, *body):
        """Transform group definitions."""
        # Filter out None values from body
        filtered_body = [stmt for stmt in body if stmt is not None]
        # name is now an IDENT token, so we can get it directly
        name_str = str(name)
        return GroupDef(name_str, filtered_body)

    @v_args(inline=True)
    def group_use(self, name, x, y, fill=None, stroke=None, transforms=None):
        """Transform group usage."""
        # name is an IDENT token
        name_str = str(name)
        # transforms might be None or a list
        transform_list = transforms if transforms else []
        return GroupUse(name_str, x, y, fill, stroke, transform_list)

    def transform_list(self, transforms):
        """Transform transform lists."""
        return [t for t in transforms if t is not None]

    @v_args(inline=True)
    def repeat_stmt(self, times, var_name, *body):
        """Transform repeat statements."""
        # Filter out None values from body
        filtered_body = [stmt for stmt in body if stmt is not None]
        return Repeat(int(times), str(var_name), filtered_body)

    @v_args(inline=True)
    def while_stmt(self, condition, *body):
        """Transform while statements."""
        # Filter out None values from body
        filtered_body = [stmt for stmt in body if stmt is not None]
        return While(condition, filtered_body)

    def clip_def(self, args):
        """Transform clip definitions."""
        # args[0] is the name, args[1:] are the shapes
        name = str(args[0])
        shapes = list(args[1:])
        return ClipDef(name, shapes)

    # Property transformers
    @v_args(inline=True)
    def fill_expr(self, value):
        return ('fill', value)

    @v_args(inline=True)
    def stroke_expr(self, value):
        return ('stroke', value)

    @v_args(inline=True)
    def opacity_expr(self, value):
        return ('opacity', value)

    @v_args(inline=True)
    def rx_expr(self, value):
        return ('rx', value)

    def font_size_expr(self, args):
        # Handle both "font-size expr" and "size expr" formats
        if len(args) == 1:
            # "size expr" format
            return ('font-size', args[0])
        else:
            # "font - size expr" format
            return ('font-size', args[-1])  # Last argument is the expression

    @v_args(inline=True)
    def gradient_ref(self, name):
        return ('gradient', str(name))

    @v_args(inline=True)
    def clip_ref(self, name):
        return ('clip', str(name))

    # Shape property wrapper transformers
    @v_args(inline=True)
    def circle_property(self, prop):
        return prop

    @v_args(inline=True)
    def rect_property(self, prop):
        return prop

    @v_args(inline=True)
    def ellipse_property(self, prop):
        return prop

    @v_args(inline=True)
    def text_property(self, prop):
        return prop

    # Control flow transformers
    @v_args(inline=True)
    def for_stmt(self, var_name, start, end, *body):
        # Filter out None statements
        filtered_body = [stmt for stmt in body if stmt is not None]
        return For(str(var_name), start, end, filtered_body)

    @v_args(inline=True)
    def foreach_stmt(self, var_name, iterable, *args):
        # Check if we have an index variable (with index variant)
        if len(args) > 0 and isinstance(args[0], str):
            # With index: foreach item in array { index in ... }
            index_var = str(args[0])
            body = args[1:]
            filtered_body = [stmt for stmt in body if stmt is not None]
            return ForEach(str(var_name), iterable, index_var, filtered_body)
        else:
            # Without index: foreach item in array { ... }
            body = args
            filtered_body = [stmt for stmt in body if stmt is not None]
            return ForEach(str(var_name), iterable, None, filtered_body)

    def if_stmt(self, items):
        condition = items[0]
        body_parts = items[1:]

        # Filter out None values
        filtered_parts = [part for part in body_parts if part is not None]

        if_body = filtered_parts
        else_body = []

        return If(condition, if_body, else_body)

    # Transform transformers
    @v_args(inline=True)
    def rotate(self, angle):
        return Rotate(angle)

    @v_args(inline=True)
    def scale(self, factor):
        return Scale(factor)

    @v_args(inline=True)
    def translate(self, x, y):
        return Translate(x, y)

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
            return 'font-size'  # "font" "-" "size"

    def animation_property(self, args):
        prop_name = args[0]
        from_val = args[1]
        to_val = args[2]
        duration = str(args[3])

        repeat = 'once'
        direction = 'normal'
        easing = 'linear'

        # Process optional arguments
        for i in range(4, len(args)):
            arg_str = str(args[i])
            if arg_str in ['once', 'infinite'] or arg_str.isdigit():
                repeat = arg_str
            elif arg_str in ['normal', 'reverse', 'alternate', 'alternate-reverse']:
                direction = arg_str
            elif arg_str in ['linear', 'ease', 'ease-in', 'ease-out', 'ease-in-out']:
                easing = arg_str

        return AnimationProperty(prop_name, from_val, to_val, duration, repeat, direction, easing)

    @v_args(inline=True)
    def animate_block(self, *properties):
        return AnimationBlock(list(properties))

    # Logical operations
    @v_args(inline=True)
    def logical_or_op(self, left, right):
        return LogicalOr(left, right)

    @v_args(inline=True)
    def logical_and_op(self, left, right):
        return LogicalAnd(left, right)

    @v_args(inline=True)
    def logical_not_op(self, operand):
        return LogicalNot(operand)

    # Comment handler (keep this method name)
    def COMMENT(self, comment):
        return None

    def shape_attributes(self, *attributes):
        """Transform shape_attributes into a dictionary of properties."""
        props = {}
        transforms = []
        
        for attr in attributes:
            # Handle both direct tuples and lists containing tuples
            if isinstance(attr, tuple) and len(attr) == 2:
                prop_name, prop_value = attr
                # In shape_attributes context, 'width' means 'stroke_width'
                if prop_name == 'width':
                    prop_name = 'stroke_width'
                props[prop_name] = prop_value
            elif isinstance(attr, list):
                # If it's a list, process each item in the list
                for item in attr:
                    if isinstance(item, tuple) and len(item) == 2:
                        prop_name, prop_value = item
                        # In shape_attributes context, 'width' means 'stroke_width'
                        if prop_name == 'width':
                            prop_name = 'stroke_width'
                        props[prop_name] = prop_value
                    elif hasattr(item, '__class__') and item.__class__.__name__ in ['Rotate', 'Scale', 'Translate']:
                        # Handle transform objects within lists
                        transforms.append(item)
            elif hasattr(attr, '__class__') and attr.__class__.__name__ in ['Rotate', 'Scale', 'Translate']:
                # Handle transform objects
                transforms.append(attr)
        
        # Add transforms to props if any were found
        if transforms:
            props['transforms'] = transforms
            
        return props

    def shape_attribute(self, attr):
        """Transform individual shape attribute."""
        # Return the first item if it's a list with one element
        if isinstance(attr, list) and len(attr) == 1:
            return attr[0]
        return attr

    def stroke_width_expr(self, args):
        """Transform stroke-width expressions."""
        return ('stroke_width', args[0])
