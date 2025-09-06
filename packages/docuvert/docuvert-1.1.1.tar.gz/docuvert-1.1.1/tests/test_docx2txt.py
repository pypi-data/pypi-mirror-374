
import pytest
from converters.docx2txt import Docx2TxtConverter
import os
from docx import Document

# Helper function to create a dummy DOCX for testing
def create_dummy_docx(file_path):
    document = Document()
    document.add_paragraph("This is a dummy DOCX for testing.")
    document.save(file_path)

def test_docx2txt_conversion(tmp_path):
    """
    Tests the DOCX to plain text conversion.
    """
    input_docx = tmp_path / "dummy.docx"
    output_txt = tmp_path / "output.txt"
    
    create_dummy_docx(input_docx)

    converter = Docx2TxtConverter()
    converter.convert(str(input_docx), str(output_txt))

    assert os.path.exists(output_txt)
    assert os.path.getsize(output_txt) > 0

# TODO: Add tests for AST generation once implemented.
