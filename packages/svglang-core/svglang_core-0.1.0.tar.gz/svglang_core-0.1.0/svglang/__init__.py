"""SVG Language - A domain-specific language for creating dynamic SVG graphics."""

from __future__ import annotations

from .execution.interpreter import SVGInterpreter
from .parsing.parser import parser
from .parsing.transformer import SVGTransformer

__version__ = '0.1.0'
__author__ = 'Florian Scholz'


class SVGLangError(Exception):
    """Custom exception for SVGLang compilation errors."""


def compile_svgl(code: str) -> str:
    """Compile SVGLang code to SVG output.
    
    Args:
        code: SVGLang source code as string
        
    Returns:
        Generated SVG as string
        
    Raises:
        SVGLangError: If compilation fails due to syntax or runtime errors
    """
    try:
        # Parse the code into AST
        tree = parser.parse(code)
        
        # Transform parse tree to AST
        transformer = SVGTransformer()
        ast = transformer.transform(tree)
        
        # Ensure ast is always a list (from CLI example)
        if not isinstance(ast, (list, tuple)):
            ast = [ast]
        
        # Execute AST and generate SVG
        interpreter = SVGInterpreter(ast)
        interpreter.run()
        return interpreter.get_svg()
        
    except Exception as e:
        msg = f'SVGLang compilation failed: {e!s}'
        raise SVGLangError(msg) from e


__all__ = [
    'SVGInterpreter',
    'SVGLangError',
    'SVGTransformer',
    'compile_svgl',
    'parser',
]