
import pytest
from converters.xlsx2csv import Xlsx2CsvConverter
import os
import pandas as pd

def test_xlsx2csv_conversion(tmp_path):
    """
    Tests the XLSX to CSV conversion.
    """
    input_xlsx = tmp_path / "dummy.xlsx"
    output_csv = tmp_path / "output.csv"
    
    # Create a dummy XLSX file
    df = pd.DataFrame({'col1': [1, 4], 'col2': [2, 5], 'col3': [3, 6]})
    df.to_excel(input_xlsx, index=False)

    converter = Xlsx2CsvConverter()
    converter.convert(str(input_xlsx), str(output_csv))

    assert os.path.exists(output_csv)
    assert os.path.getsize(output_csv) > 0

# TODO: Add tests for AST generation once implemented.
