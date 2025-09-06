
import pytest
from converters.pdf2txt import Pdf2TxtConverter
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Helper function to create a dummy PDF for testing
def create_dummy_pdf(file_path):
    c = canvas.Canvas(file_path, pagesize=letter)
    c.drawString(100, 750, "This is a dummy PDF for testing.")
    c.save()

def test_pdf2txt_conversion(tmp_path):
    """
    Tests the PDF to plain text conversion.
    """
    input_pdf = tmp_path / "dummy.pdf"
    output_txt = tmp_path / "output.txt"
    
    create_dummy_pdf(str(input_pdf))

    converter = Pdf2TxtConverter()
    converter.convert(str(input_pdf), str(output_txt))

    assert os.path.exists(output_txt)
    assert os.path.getsize(output_txt) > 0

# TODO: Add tests for AST generation once implemented.
