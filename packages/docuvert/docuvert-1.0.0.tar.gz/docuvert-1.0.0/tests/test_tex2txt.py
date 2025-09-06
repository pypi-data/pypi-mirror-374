

import pytest
from converters.tex2txt import Tex2TxtConverter
import os

def test_tex2txt_conversion(tmp_path):
    """
    Tests the LaTeX to plain text conversion.
    """
    input_tex = tmp_path / "dummy.tex"
    output_txt = tmp_path / "output.txt"
    
    with open(input_tex, 'w', encoding='utf-8') as f:
        f.write("\documentclass{article}\begin{document}Hello, World!\end{document}")

    converter = Tex2TxtConverter()
    converter.convert(str(input_tex), str(output_txt))

    assert os.path.exists(output_txt)
    assert os.path.getsize(output_txt) > 0

# TODO: Add tests for AST generation once implemented.

