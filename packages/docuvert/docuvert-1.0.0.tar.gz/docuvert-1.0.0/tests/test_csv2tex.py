

import pytest
from converters.csv2tex import Csv2TexConverter
import os

def test_csv2tex_conversion(tmp_path):
    """
    Tests the CSV to LaTeX conversion.
    """
    input_csv = tmp_path / "dummy.csv"
    output_tex = tmp_path / "output.tex"
    
    with open(input_csv, 'w', encoding='utf-8') as f:
        f.write("col1,col2,col3\n1,2,3\n4,5,6")

    converter = Csv2TexConverter()
    converter.convert(str(input_csv), str(output_tex))

    assert os.path.exists(output_tex)
    assert os.path.getsize(output_tex) > 0

# TODO: Add tests for AST generation once implemented.

