
import pytest
from converters.pdf2md import Pdf2MdConverter
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Helper function to create a dummy PDF for testing
def create_dummy_pdf(file_path):
    c = canvas.Canvas(file_path, pagesize=letter)
    c.drawString(100, 750, "This is a dummy PDF for testing.")
    c.save()

def test_pdf2md_conversion(tmp_path):
    """
    Tests the PDF to Markdown conversion.
    """
    input_pdf = tmp_path / "dummy.pdf"
    output_md = tmp_path / "output.md"
    
    create_dummy_pdf(str(input_pdf))

    converter = Pdf2MdConverter()
    converter.convert(str(input_pdf), str(output_md))

    assert os.path.exists(output_md)
    assert os.path.getsize(output_md) > 0

# TODO: Add tests for AST generation once implemented.
