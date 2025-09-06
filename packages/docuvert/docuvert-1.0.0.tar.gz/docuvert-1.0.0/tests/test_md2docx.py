
import pytest
from converters.md2docx import Md2DocxConverter
import os

def test_md2docx_conversion(tmp_path):
    """
    Tests the Markdown to DOCX conversion.
    """
    input_md = tmp_path / "dummy.md"
    output_docx = tmp_path / "output.docx"
    
    with open(input_md, 'w', encoding='utf-8') as f:
        f.write("# Test Markdown\n\nThis is a test markdown document.")

    converter = Md2DocxConverter()
    converter.convert(str(input_md), str(output_docx))

    assert os.path.exists(output_docx)
    assert os.path.getsize(output_docx) > 0

# TODO: Add tests for AST generation once implemented.

