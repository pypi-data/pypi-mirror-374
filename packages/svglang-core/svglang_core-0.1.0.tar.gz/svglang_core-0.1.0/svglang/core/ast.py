# ast.py
from dataclasses import dataclass, field
from typing import List, Optional, Union
import math

# Expressions
@dataclass
class Expr:
    pass

@dataclass
class Number(Expr):
    value: float

@dataclass
class UnitValue(Expr):
    value: float
    unit: str

    def __str__(self):
        """String representation for interpolation"""
        return f"{self.value}{self.unit}"

    def __mul__(self, other):
        if isinstance(other, UnitValue):
            # For unit multiplication, we need to handle unit compatibility
            # For now, let's handle angle units specially
            if self.unit in ['deg', 'rad', 'turn'] and other.unit in ['deg', 'rad', 'turn']:
                # Convert both to same unit and multiply values
                self_deg = self._to_degrees()
                other_deg = other._to_degrees()
                return UnitValue(self_deg * other_deg, 'deg')
            else:
                # For other units, multiply values and concatenate units
                return UnitValue(self.value * other.value, f"{self.unit}*{other.unit}")
        elif isinstance(other, (int, float)):
            return UnitValue(self.value * other, self.unit)
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __add__(self, other):
        if isinstance(other, UnitValue):
            if self.unit == other.unit:
                return UnitValue(self.value + other.value, self.unit)
            elif self.unit in ['deg', 'rad', 'turn'] and other.unit in ['deg', 'rad', 'turn']:
                # Convert to common unit
                self_deg = self._to_degrees()
                other_deg = other._to_degrees()
                return UnitValue(self_deg + other_deg, 'deg')
            else:
                raise ValueError(f"Cannot add incompatible units: {self.unit} and {other.unit}")
        elif isinstance(other, (int, float)):
            return UnitValue(self.value + other, self.unit)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, UnitValue):
            if self.unit == other.unit:
                return UnitValue(self.value - other.value, self.unit)
            elif self.unit in ['deg', 'rad', 'turn'] and other.unit in ['deg', 'rad', 'turn']:
                # Convert to common unit
                self_deg = self._to_degrees()
                other_deg = other._to_degrees()
                return UnitValue(self_deg - other_deg, 'deg')
            else:
                raise ValueError(f"Cannot subtract incompatible units: {self.unit} and {other.unit}")
        elif isinstance(other, (int, float)):
            return UnitValue(self.value - other, self.unit)
        return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, UnitValue):
            if self.unit == other.unit:
                return self.value / other.value  # Division of same units yields dimensionless number
            else:
                return UnitValue(self.value / other.value, f"{self.unit}/{other.unit}")
        elif isinstance(other, (int, float)):
            return UnitValue(self.value / other, self.unit)
        return NotImplemented

    def _to_degrees(self):
        """Convert angle units to degrees"""
        if self.unit == 'deg':
            return self.value
        elif self.unit == 'rad':
            return math.degrees(self.value)
        elif self.unit == 'turn':
            return self.value * 360
        else:
            return self.value

@dataclass
class String(Expr):
    value: str

@dataclass
class InterpolatedString(Expr):
    parts: List[Union[str, Expr]]  # Mix of literal strings and expressions

@dataclass
class Var(Expr):
    name: str

@dataclass
class Boolean(Expr):
    value: bool

@dataclass
class BinOp(Expr):
    left: Expr
    op: str
    right: Expr

@dataclass
class TernaryOp(Expr):
    condition: Expr
    true_value: Expr
    false_value: Expr

@dataclass
class ArrayLiteral(Expr):
    elements: List[Expr]

@dataclass
class ArrayAccess(Expr):
    array: str
    index: Expr

@dataclass
class FunctionCall(Expr):
    module: str
    function: str
    arguments: list[Expr]  # Changed from single argument to list of arguments

@dataclass
class CanvasProperty(Expr):
    property: str  # 'width' or 'height'





# Statements
@dataclass
class Statement:
    pass

@dataclass
class Canvas(Statement):
    width: int
    height: int
    background: str = 'white'

@dataclass
class Circle(Statement):
    radius: Expr
    x: Expr
    y: Expr
    fill: str = 'none'
    stroke: str = 'black'
    stroke_width: Expr = field(default_factory=lambda: Number(1))
    opacity: Optional[Expr] = None
    transforms: List['Transform'] = field(default_factory=list)
    animation: Optional['AnimationBlock'] = None
    clip: Optional['ClipRef'] = None
    gradient: Optional['GradientRef'] = None

@dataclass
class Rect(Statement):
    width: Expr
    height: Expr
    x: Expr
    y: Expr
    fill: str = 'none'
    stroke: str = 'black'
    stroke_width: Expr = field(default_factory=lambda: Number(1))
    opacity: Optional[Expr] = None
    transforms: List['Transform'] = field(default_factory=list)
    rx: Optional[Expr] = None
    animation: Optional['AnimationBlock'] = None
    clip: Optional['ClipRef'] = None
    gradient: Optional['GradientRef'] = None

@dataclass
class Line(Statement):
    x1: Expr
    y1: Expr
    x2: Expr
    y2: Expr
    stroke: str = 'black'
    stroke_width: Expr = field(default_factory=lambda: Number(1))
    opacity: Optional[Expr] = None
    transforms: List['Transform'] = field(default_factory=list)

@dataclass
class VarDecl(Statement):
    name: str
    value: Union[Expr, Statement]  # Can be expression or shape statement

@dataclass
class Ellipse(Statement):
    rx: Expr
    ry: Expr
    x: Expr
    y: Expr
    fill: str = 'none'
    stroke: str = 'black'
    stroke_width: Expr = field(default_factory=lambda: Number(1))
    opacity: Optional[Expr] = None
    transforms: List['Transform'] = field(default_factory=list)
    animation: Optional['AnimationBlock'] = None
    clip: Optional['ClipRef'] = None

@dataclass
class Polygon(Statement):
    points: List[tuple[Expr, Expr]]
    fill: str = 'none'
    stroke: str = 'black'
    opacity: Optional[Expr] = None

@dataclass
class Text(Statement):
    content: str
    x: Expr
    y: Expr
    fill: str = 'black'
    stroke: str = 'none'
    stroke_width: Expr = field(default_factory=lambda: Number(1))
    font_size: Expr = field(default_factory=lambda: Number(16))
    opacity: Optional[Expr] = None
    transforms: List['Transform'] = field(default_factory=list)
    animation: Optional['AnimationBlock'] = None
    clip: Optional['ClipRef'] = None

@dataclass
class Path(Statement):
    path_data: str
    fill: str = 'none'
    stroke: str = 'black'
    stroke_width: Expr = field(default_factory=lambda: Number(1))
    opacity: Optional[Expr] = None
    transforms: list['Transform'] = field(default_factory=list)
    gradient: Optional['GradientRef'] = None
    clip: Optional['ClipRef'] = None

@dataclass
class Arc(Statement):
    rx: Expr
    ry: Expr
    x: Expr
    y: Expr
    start_angle: Expr
    end_angle: Expr
    fill: str = 'none'
    stroke: str = 'black'
    transforms: list['Transform'] = field(default_factory=list)
    gradient: Optional['GradientRef'] = None
    clip: Optional['ClipRef'] = None

@dataclass
class Curve(Statement):
    x1: Expr
    y1: Expr
    x2: Expr
    y2: Expr
    cx1: Expr
    cy1: Expr
    cx2: Expr
    cy2: Expr
    stroke: str = 'black'
    stroke_width: Expr = field(default_factory=lambda: Number(1))
    fill: str = 'none'
    transforms: list['Transform'] = field(default_factory=list)
    gradient: Optional['GradientRef'] = None
    clip: Optional['ClipRef'] = None

@dataclass
class GroupDef(Statement):
    name: str
    body: List[Statement]

@dataclass
class GroupUse(Statement):
    name: str
    x: Expr
    y: Expr
    fill: Optional[Expr] = None
    stroke: Optional[Expr] = None
    transforms: List['Transform'] = field(default_factory=list)



@dataclass
class Transform:
    pass

@dataclass
class Rotate(Transform):
    angle: Expr

@dataclass
class Scale(Transform):
    factor: Expr

@dataclass
class Translate(Transform):
    x: Expr
    y: Expr





@dataclass
class Repeat(Statement):
    times: int
    var_name: str
    body: List[Statement]

@dataclass
class While(Statement):
    condition: Expr
    body: List[Statement]

@dataclass
class For(Statement):
    var_name: str
    start: Expr
    end: Expr
    body: List[Statement]

@dataclass
class ForEach(Statement):
    var_name: str
    iterable: Expr
    index_name: str = None  # Optional index parameter
    body: List[Statement] = field(default_factory=list)

@dataclass
class If(Statement):
    condition: Expr
    if_body: List[Statement]
    else_body: List[Statement] = field(default_factory=list)

# Gradient nodes
@dataclass
class GradientRef(Expr):
    name: str

@dataclass
class ClipRef(Expr):
    name: str

@dataclass
class GradientStop:
    color: Expr
    offset: Expr

@dataclass
class LinearGradient(Statement):
    name: str
    x1: Expr
    y1: Expr
    x2: Expr
    y2: Expr
    stops: List[GradientStop]

@dataclass
class RadialGradient(Statement):
    name: str
    cx: Expr
    cy: Expr
    r: Expr
    stops: List[GradientStop]

@dataclass
class ConicGradient(Statement):
    name: str
    cx: Expr
    cy: Expr
    angle: Expr
    stops: List[GradientStop]

@dataclass
class ClipDef(Statement):
    name: str
    shapes: List[Statement]

# Animation nodes
@dataclass
class AnimationProperty:
    property_name: str
    from_value: Expr
    to_value: Expr
    duration: str
    repeat: str = "once"
    direction: str = "normal"
    easing: str = "linear"

@dataclass
class AnimationBlock:
    properties: List[AnimationProperty]

@dataclass
class LogicalOr(Expr):
    left: Expr
    right: Expr

@dataclass
class LogicalAnd(Expr):
    left: Expr
    right: Expr

@dataclass
class LogicalNot(Expr):
    operand: Expr


