

import pytest
from converters.csv2pdf import Csv2PdfConverter
import os

def test_csv2pdf_conversion(tmp_path):
    """
    Tests the CSV to PDF conversion.
    """
    input_csv = tmp_path / "dummy.csv"
    output_pdf = tmp_path / "output.pdf"
    
    with open(input_csv, 'w', encoding='utf-8') as f:
        f.write("col1,col2,col3\n1,2,3\n4,5,6")

    converter = Csv2PdfConverter()
    converter.convert(str(input_csv), str(output_pdf))

    assert os.path.exists(output_pdf)
    assert os.path.getsize(output_pdf) > 0

# TODO: Add tests for AST generation once implemented.

