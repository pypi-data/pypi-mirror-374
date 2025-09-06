

import pytest
from converters.md2csv import Md2CsvConverter
import os

def test_md2csv_conversion(tmp_path):
    """
    Tests the Markdown to CSV conversion.
    """
    input_md = tmp_path / "dummy_table.md"
    output_csv = tmp_path / "output.csv"
    
    with open(input_md, 'w', encoding='utf-8') as f:
        f.write("| Header 1 | Header 2 |\n|----------|----------|\n| Row 1 Col 1 | Row 1 Col 2 |\n| Row 2 Col 1 | Row 2 Col 2 |")

    converter = Md2CsvConverter()
    converter.convert(str(input_md), str(output_csv))

    assert os.path.exists(output_csv)
    assert os.path.getsize(output_csv) > 0

# TODO: Add tests for AST generation once implemented.

