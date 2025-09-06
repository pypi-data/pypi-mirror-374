

import pytest
from converters.csv2txt import Csv2TxtConverter
import os

def test_csv2txt_conversion(tmp_path):
    """
    Tests the CSV to plain text conversion.
    """
    input_csv = tmp_path / "dummy.csv"
    output_txt = tmp_path / "output.txt"
    
    with open(input_csv, 'w', encoding='utf-8') as f:
        f.write("col1,col2,col3\n1,2,3\n4,5,6")

    converter = Csv2TxtConverter()
    converter.convert(str(input_csv), str(output_txt))

    assert os.path.exists(output_txt)
    assert os.path.getsize(output_txt) > 0

# TODO: Add tests for AST generation once implemented.

