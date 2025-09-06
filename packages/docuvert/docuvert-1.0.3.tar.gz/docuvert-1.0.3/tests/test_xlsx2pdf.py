
import pytest
from converters.xlsx2pdf import Xlsx2PdfConverter
import os
import pandas as pd

def test_xlsx2pdf_conversion(tmp_path):
    """
    Tests the XLSX to PDF conversion.
    """
    input_xlsx = tmp_path / "dummy.xlsx"
    output_pdf = tmp_path / "output.pdf"
    
    # Create a dummy XLSX file
    df = pd.DataFrame({'col1': [1, 4], 'col2': [2, 5], 'col3': [3, 6]})
    df.to_excel(input_xlsx, index=False)

    converter = Xlsx2PdfConverter()
    converter.convert(str(input_xlsx), str(output_pdf))

    assert os.path.exists(output_pdf)
    assert os.path.getsize(output_pdf) > 0

# TODO: Add tests for AST generation once implemented.
