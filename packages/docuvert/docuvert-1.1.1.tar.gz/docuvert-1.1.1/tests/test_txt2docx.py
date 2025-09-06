
import pytest
from converters.txt2docx import Txt2DocxConverter
import os

def test_txt2docx_conversion(tmp_path):
    """
    Tests the plain text to DOCX conversion.
    """
    input_txt = tmp_path / "dummy.txt"
    output_docx = tmp_path / "output.docx"
    
    with open(input_txt, 'w', encoding='utf-8') as f:
        f.write("This is a dummy text document.")

    converter = Txt2DocxConverter()
    converter.convert(str(input_txt), str(output_docx))

    assert os.path.exists(output_docx)
    assert os.path.getsize(output_docx) > 0

# TODO: Add tests for AST generation once implemented.
