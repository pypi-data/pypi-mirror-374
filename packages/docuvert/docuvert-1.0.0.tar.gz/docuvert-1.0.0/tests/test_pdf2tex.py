
import pytest
from converters.pdf2tex import Pdf2TexConverter
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Helper function to create a dummy PDF for testing
def create_dummy_pdf(file_path):
    c = canvas.Canvas(file_path, pagesize=letter)
    c.drawString(100, 750, "This is a dummy PDF for testing.")
    c.save()

def test_pdf2tex_conversion(tmp_path):
    """
    Tests the PDF to LaTeX conversion.
    """
    input_pdf = tmp_path / "dummy.pdf"
    output_tex = tmp_path / "output.tex"
    
    create_dummy_pdf(str(input_pdf))

    converter = Pdf2TexConverter()
    converter.convert(str(input_pdf), str(output_tex))

    assert os.path.exists(output_tex)
    assert os.path.getsize(output_tex) > 0

# TODO: Add tests for AST generation once implemented.
