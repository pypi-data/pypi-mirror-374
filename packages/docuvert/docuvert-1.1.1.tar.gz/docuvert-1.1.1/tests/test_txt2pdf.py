
import pytest
from converters.txt2pdf import Txt2PdfConverter
import os

def test_txt2pdf_conversion(tmp_path):
    """
    Tests the plain text to PDF conversion.
    """
    input_txt = tmp_path / "dummy.txt"
    output_pdf = tmp_path / "output.pdf"
    
    with open(input_txt, 'w', encoding='utf-8') as f:
        f.write("This is a dummy text document.")

    converter = Txt2PdfConverter()
    converter.convert(str(input_txt), str(output_pdf))

    assert os.path.exists(output_pdf)
    assert os.path.getsize(output_pdf) > 0

# TODO: Add tests for AST generation once implemented.
