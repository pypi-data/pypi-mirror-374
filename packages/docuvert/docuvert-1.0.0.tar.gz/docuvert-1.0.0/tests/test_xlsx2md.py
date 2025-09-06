
import pytest
from converters.xlsx2md import Xlsx2MdConverter
import os
import pandas as pd

def test_xlsx2md_conversion(tmp_path):
    """
    Tests the XLSX to Markdown conversion.
    """
    input_xlsx = tmp_path / "dummy.xlsx"
    output_md = tmp_path / "output.md"
    
    # Create a dummy XLSX file
    df = pd.DataFrame({'col1': [1, 4], 'col2': [2, 5], 'col3': [3, 6]})
    df.to_excel(input_xlsx, index=False)

    converter = Xlsx2MdConverter()
    converter.convert(str(input_xlsx), str(output_md))

    assert os.path.exists(output_md)
    assert os.path.getsize(output_md) > 0

# TODO: Add tests for AST generation once implemented.
