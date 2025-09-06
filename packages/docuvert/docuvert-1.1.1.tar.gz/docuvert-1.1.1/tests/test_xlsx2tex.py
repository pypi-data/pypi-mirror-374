
import pytest
from converters.xlsx2tex import Xlsx2TexConverter
import os
import pandas as pd

def test_xlsx2tex_conversion(tmp_path):
    """
    Tests the XLSX to LaTeX conversion.
    """
    input_xlsx = tmp_path / "dummy.xlsx"
    output_tex = tmp_path / "output.tex"
    
    # Create a dummy XLSX file
    df = pd.DataFrame({'col1': [1, 4], 'col2': [2, 5], 'col3': [3, 6]})
    df.to_excel(input_xlsx, index=False)

    converter = Xlsx2TexConverter()
    converter.convert(str(input_xlsx), str(output_tex))

    assert os.path.exists(output_tex)
    assert os.path.getsize(output_tex) > 0

# TODO: Add tests for AST generation once implemented.
