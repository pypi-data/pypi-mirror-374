

import pytest
from converters.csv2md import Csv2MdConverter
import os

def test_csv2md_conversion(tmp_path):
    """
    Tests the CSV to Markdown conversion.
    """
    input_csv = tmp_path / "dummy.csv"
    output_md = tmp_path / "output.md"
    
    with open(input_csv, 'w', encoding='utf-8') as f:
        f.write("col1,col2,col3\n1,2,3\n4,5,6")

    converter = Csv2MdConverter()
    converter.convert(str(input_csv), str(output_md))

    assert os.path.exists(output_md)
    assert os.path.getsize(output_md) > 0

# TODO: Add tests for AST generation once implemented.

