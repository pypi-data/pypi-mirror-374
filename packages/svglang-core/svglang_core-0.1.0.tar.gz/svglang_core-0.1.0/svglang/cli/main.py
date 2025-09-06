from __future__ import annotations

import os

from ..execution.interpreter import SVGInterpreter
from ..parsing.parser import parser


def read_script_file(filename: str):
    """Read SVG language script from file"""
    # Use the filename directly - support both relative and absolute paths
    if os.path.isabs(filename):
        script_path = filename
    else:
        # Try current directory first, then scripts directory
        current_dir_path = filename
        if os.path.exists(current_dir_path):
            script_path = current_dir_path
        else:
            script_path = os.path.join(os.path.dirname(__file__), 'scripts', filename)
    
    with open(script_path, 'r') as f:
        return f.read()

def run_script(script: str):
    """Run SVG language script and return SVG output"""
    ast = parser.parse(script)
    # Ensure ast is always a list
    if not isinstance(ast, (list, tuple)):
        ast = [ast]
    interpreter = SVGInterpreter(ast)
    interpreter.run()

    # Print SVG output to console
    print("=== GENERATED SVG ===")
    print(interpreter.get_svg())
    print("=== END SVG ===")

    return interpreter.get_svg()

if __name__ == '__main__':
    import sys

    # Get script filename from command line or use default
    if len(sys.argv) > 1:
        script_filename = sys.argv[1]
        # If it's a full path, use it directly
        if os.path.isabs(script_filename) or script_filename.startswith('./'):
            with open(script_filename, 'r') as f:
                script = f.read()
        elif os.path.dirname(script_filename):
            # It's a relative path like "scripts/test.svgl", open it directly
            with open(script_filename, 'r') as f:
                script = f.read()
        else:
            # Otherwise, it's just a filename (e.g., "test.svgl", "showcase.svgl"),
            # so look for it in the 'scripts' directory relative to script.py
            script = read_script_file(script_filename)
    else:
        # Default to showcase.svgl
        script = read_script_file('showcase.svgl')

    # Parse and execute
    ast = parser.parse(script)
    # Ensure ast is always a list
    if not isinstance(ast, (list, tuple)):
        ast = [ast]
    interpreter = SVGInterpreter(ast)
    interpreter.run()

    # Print SVG output to console
    print("=== GENERATED SVG ===")
    print(interpreter.get_svg())
    print("=== END SVG ===")

    interpreter.save('example.svg')
