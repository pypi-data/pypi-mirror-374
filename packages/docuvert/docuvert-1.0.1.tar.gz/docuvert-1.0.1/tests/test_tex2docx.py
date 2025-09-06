
import pytest
from converters.tex2docx import Tex2DocxConverter
import os

def test_tex2docx_conversion(tmp_path):
    """
    Tests the LaTeX to DOCX conversion.
    """
    input_tex = tmp_path / "dummy.tex"
    output_docx = tmp_path / "output.docx"
    
    with open(input_tex, 'w', encoding='utf-8') as f:
        f.write("\documentclass{article}\begin{document}Hello, World!\end{document}")

    converter = Tex2DocxConverter()
    converter.convert(str(input_tex), str(output_docx))

    assert os.path.exists(output_docx)
    assert os.path.getsize(output_docx) > 0

# TODO: Add tests for AST generation once implemented.

