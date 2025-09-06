# SVGLang Core

A domain-specific language (DSL) for generating SVG graphics with a focus on simplicity and expressiveness.

## Installation

```bash
pip install svglang-core
```

## Quick Start

```python
from svglang import compile_svgl

# Compile SVGLang code to SVG
code = """
canvas width 400 height 300 background "lightblue"

let radius = 50
let center_x = 200
let center_y = 150

circle radius radius at (center_x, center_y) fill "red"
"""

svg_output = compile_svgl(code)
print(svg_output)
```

## Command Line Usage

After installation, you can use the `svglang` command:

```bash
# Compile a .svgl file to SVG
svglang my_drawing.svgl

# Output to specific file
svglang input.svgl --output output.svg
```

## Language Features

- **Simple Syntax**: Clean, declarative syntax for SVG creation
- **String Interpolation**: Use variables with `{variable}` syntax
- **Canvas Properties**: Set dimensions, viewBox, and styling
- **Shapes**: Rectangles, circles, ellipses, lines, polygons
- **Animations**: Built-in animation support
- **Gradients**: Linear and radial gradients
- **Control Flow**: Loops, conditionals, and functions

## Example

```svgl
canvas width 400 height 300 background "lightblue"

let radius = 50
let center_x = 200
let center_y = 150

circle radius radius at (center_x, center_y) fill "red"

# Animation
circle radius radius at (center_x, center_y) fill "red" animate {
    x from 0 to 100 duration 2s repeat once direction normal
}
```

## Documentation

For complete language documentation and examples, visit: https://github.com/SVGLang/svglang

## License

MIT License - see LICENSE file for details.