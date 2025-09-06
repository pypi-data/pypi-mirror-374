import pytest
from converters.pdf2docx import Pdf2DocxConverter
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Helper function to create a dummy PDF for testing
def create_dummy_pdf(file_path):
    c = canvas.Canvas(file_path, pagesize=letter)
    c.drawString(100, 750, "This is a dummy PDF for testing.")
    c.save()

def test_pdf2docx_conversion(tmp_path):
    """
    Tests the PDF to DOCX conversion.
    """
    input_pdf = tmp_path / "dummy.pdf"
    output_docx = tmp_path / "output.docx"
    
    create_dummy_pdf(str(input_pdf))

    converter = Pdf2DocxConverter()
    converter.convert(str(input_pdf), str(output_docx))

    assert os.path.exists(output_docx)
    assert os.path.getsize(output_docx) > 0

# TODO: Add tests for AST generation once implemented.