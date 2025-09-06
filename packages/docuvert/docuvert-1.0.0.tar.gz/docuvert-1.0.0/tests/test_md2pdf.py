

import pytest
from converters.md2pdf import Md2PdfConverter
import os

def test_md2pdf_conversion(tmp_path):
    """
    Tests the Markdown to PDF conversion.
    """
    input_md = tmp_path / "dummy.md"
    output_pdf = tmp_path / "output.pdf"
    
    with open(input_md, 'w', encoding='utf-8') as f:
        f.write("# Test Markdown\n\nThis is a test markdown document.")

    converter = Md2PdfConverter()
    converter.convert(str(input_md), str(output_pdf))

    assert os.path.exists(output_pdf)
    assert os.path.getsize(output_pdf) > 0

# TODO: Add tests for AST generation once implemented.

