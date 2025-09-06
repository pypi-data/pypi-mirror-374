
import pytest
from converters.txt2csv import Txt2CsvConverter
import os

def test_txt2csv_conversion(tmp_path):
    """
    Tests the plain text to CSV conversion.
    """
    input_txt = tmp_path / "dummy.txt"
    output_csv = tmp_path / "output.csv"
    
    with open(input_txt, 'w', encoding='utf-8') as f:
        f.write("col1,col2,col3\n1,2,3\n4,5,6")

    converter = Txt2CsvConverter()
    converter.convert(str(input_txt), str(output_csv))

    assert os.path.exists(output_csv)
    assert os.path.getsize(output_csv) > 0

# TODO: Add tests for AST generation once implemented.

