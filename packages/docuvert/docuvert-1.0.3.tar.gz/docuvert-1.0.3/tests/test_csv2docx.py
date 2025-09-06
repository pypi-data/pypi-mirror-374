

import pytest
from converters.csv2docx import Csv2DocxConverter
import os

def test_csv2docx_conversion(tmp_path):
    """
    Tests the CSV to DOCX conversion.
    """
    input_csv = tmp_path / "dummy.csv"
    output_docx = tmp_path / "output.docx"
    
    with open(input_csv, 'w', encoding='utf-8') as f:
        f.write("col1,col2,col3\n1,2,3\n4,5,6")

    converter = Csv2DocxConverter()
    converter.convert(str(input_csv), str(output_docx))

    assert os.path.exists(output_docx)
    assert os.path.getsize(output_docx) > 0

# TODO: Add tests for AST generation once implemented.

