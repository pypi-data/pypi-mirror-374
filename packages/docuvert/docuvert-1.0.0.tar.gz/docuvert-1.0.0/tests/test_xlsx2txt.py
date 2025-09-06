
import pytest
from converters.xlsx2txt import Xlsx2TxtConverter
import os
import pandas as pd

def test_xlsx2txt_conversion(tmp_path):
    """
    Tests the XLSX to plain text conversion.
    """
    input_xlsx = tmp_path / "dummy.xlsx"
    output_txt = tmp_path / "output.txt"
    
    # Create a dummy XLSX file
    df = pd.DataFrame({'col1': [1, 4], 'col2': [2, 5], 'col3': [3, 6]})
    df.to_excel(input_xlsx, index=False)

    converter = Xlsx2TxtConverter()
    converter.convert(str(input_xlsx), str(output_txt))

    assert os.path.exists(output_txt)
    assert os.path.getsize(output_txt) > 0

# TODO: Add tests for AST generation once implemented.
