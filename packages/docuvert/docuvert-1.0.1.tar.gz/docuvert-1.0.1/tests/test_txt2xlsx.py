

import pytest
from converters.txt2xlsx import Txt2XlsxConverter
import os

def test_txt2xlsx_conversion(tmp_path):
    """
    Tests the plain text to XLSX conversion.
    """
    input_txt = tmp_path / "dummy.txt"
    output_xlsx = tmp_path / "output.xlsx"
    
    with open(input_txt, 'w', encoding='utf-8') as f:
        f.write("col1,col2,col3\n1,2,3\n4,5,6")

    converter = Txt2XlsxConverter()
    converter.convert(str(input_txt), str(output_xlsx))

    assert os.path.exists(output_xlsx)
    assert os.path.getsize(output_xlsx) > 0

# TODO: Add tests for AST generation once implemented.

