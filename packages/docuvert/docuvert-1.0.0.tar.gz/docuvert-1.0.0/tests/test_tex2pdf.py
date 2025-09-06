

import pytest
from converters.tex2pdf import Tex2PdfConverter
import os

def test_tex2pdf_conversion(tmp_path):
    """
    Tests the LaTeX to PDF conversion.
    """
    input_tex = tmp_path / "dummy.tex"
    output_pdf = tmp_path / "output.pdf"
    
    with open(input_tex, 'w', encoding='utf-8') as f:
        f.write("\documentclass{article}\begin{document}Hello, World!\end{document}")

    converter = Tex2PdfConverter()
    converter.convert(str(input_tex), str(output_pdf))

    assert os.path.exists(output_pdf)
    assert os.path.getsize(output_pdf) > 0

# TODO: Add tests for AST generation once implemented.

