
import pytest
from converters.docx2tex import Docx2TexConverter
import os
from docx import Document

# Helper function to create a dummy DOCX for testing
def create_dummy_docx(file_path):
    document = Document()
    document.add_paragraph("This is a dummy DOCX for testing.")
    document.save(file_path)

def test_docx2tex_conversion(tmp_path):
    """
    Tests the DOCX to LaTeX conversion.
    """
    input_docx = tmp_path / "dummy.docx"
    output_tex = tmp_path / "output.tex"
    
    create_dummy_docx(input_docx)

    converter = Docx2TexConverter()
    converter.convert(str(input_docx), str(output_tex))

    assert os.path.exists(output_tex)
    assert os.path.getsize(output_tex) > 0

# TODO: Add tests for AST generation once implemented.
