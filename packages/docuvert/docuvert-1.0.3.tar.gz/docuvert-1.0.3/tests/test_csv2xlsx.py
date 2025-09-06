
import pytest
from converters.csv2xlsx import Csv2XlsxConverter
import os

def test_csv2xlsx_conversion(tmp_path):
    """
    Tests the CSV to XLSX conversion.
    """
    input_csv = tmp_path / "dummy.csv"
    output_xlsx = tmp_path / "output.xlsx"
    
    with open(input_csv, 'w', encoding='utf-8') as f:
        f.write("col1,col2,col3\n1,2,3\n4,5,6")

    converter = Csv2XlsxConverter()
    converter.convert(str(input_csv), str(output_xlsx))

    assert os.path.exists(output_xlsx)
    assert os.path.getsize(output_xlsx) > 0

# TODO: Add tests for AST generation once implemented.

