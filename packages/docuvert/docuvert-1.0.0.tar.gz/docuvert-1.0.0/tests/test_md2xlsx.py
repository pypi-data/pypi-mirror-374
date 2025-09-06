

import pytest
from converters.md2xlsx import Md2XlsxConverter
import os

def test_md2xlsx_conversion(tmp_path):
    """
    Tests the Markdown to XLSX conversion.
    """
    input_md = tmp_path / "dummy_table.md"
    output_xlsx = tmp_path / "output.xlsx"
    
    with open(input_md, 'w', encoding='utf-8') as f:
        f.write("| Header 1 | Header 2 |\n|----------|----------|\n| Row 1 Col 1 | Row 1 Col 2 |\n| Row 2 Col 1 | Row 2 Col 2 |")

    converter = Md2XlsxConverter()
    converter.convert(str(input_md), str(output_xlsx))

    assert os.path.exists(output_xlsx)
    assert os.path.getsize(output_xlsx) > 0

# TODO: Add tests for AST generation once implemented.

