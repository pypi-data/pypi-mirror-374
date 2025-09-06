
import pytest
from converters.xlsx2docx import Xlsx2DocxConverter
import os
import pandas as pd

def test_xlsx2docx_conversion(tmp_path):
    """
    Tests the XLSX to DOCX conversion.
    """
    input_xlsx = tmp_path / "dummy.xlsx"
    output_docx = tmp_path / "output.docx"
    
    # Create a dummy XLSX file
    df = pd.DataFrame({'col1': [1, 4], 'col2': [2, 5], 'col3': [3, 6]})
    df.to_excel(input_xlsx, index=False)

    converter = Xlsx2DocxConverter()
    converter.convert(str(input_xlsx), str(output_docx))

    assert os.path.exists(output_docx)
    assert os.path.getsize(output_docx) > 0

# TODO: Add tests for AST generation once implemented.
