

import pytest
from converters.tex2md import Tex2MdConverter
import os

def test_tex2md_conversion(tmp_path):
    """
    Tests the LaTeX to Markdown conversion.
    """
    input_tex = tmp_path / "dummy.tex"
    output_md = tmp_path / "output.md"
    
    with open(input_tex, 'w', encoding='utf-8') as f:
        f.write("\documentclass{article}\begin{document}Hello, World!\end{document}")

    converter = Tex2MdConverter()
    converter.convert(str(input_tex), str(output_md))

    assert os.path.exists(output_md)
    assert os.path.getsize(output_md) > 0

# TODO: Add tests for AST generation once implemented.

