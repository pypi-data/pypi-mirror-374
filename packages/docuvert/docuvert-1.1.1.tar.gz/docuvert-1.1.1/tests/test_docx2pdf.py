
import pytest
from converters.docx2pdf import Docx2PdfConverter
import os
from docx import Document

# Helper function to create a dummy DOCX for testing
def create_dummy_docx(file_path):
    document = Document()
    document.add_paragraph("This is a dummy DOCX for testing.")
    document.save(file_path)

def test_docx2pdf_conversion(tmp_path):
    """
    Tests the DOCX to PDF conversion.
    """
    input_docx = tmp_path / "dummy.docx"
    output_pdf = tmp_path / "output.pdf"
    
    create_dummy_docx(input_docx)

    converter = Docx2PdfConverter()
    converter.convert(str(input_docx), str(output_pdf))

    assert os.path.exists(output_pdf)
    assert os.path.getsize(output_pdf) > 0

# TODO: Add tests for AST generation once implemented.
