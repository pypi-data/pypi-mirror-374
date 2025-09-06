

import pytest
from converters.md2tex import Md2TexConverter
import os

def test_md2tex_conversion(tmp_path):
    """
    Tests the Markdown to LaTeX conversion.
    """
    input_md = tmp_path / "dummy.md"
    output_tex = tmp_path / "output.tex"
    
    with open(input_md, 'w', encoding='utf-8') as f:
        f.write("# Test Markdown\n\nThis is a test markdown document.")

    converter = Md2TexConverter()
    converter.convert(str(input_md), str(output_tex))

    assert os.path.exists(output_tex)
    assert os.path.getsize(output_tex) > 0

# TODO: Add tests for AST generation once implemented.

