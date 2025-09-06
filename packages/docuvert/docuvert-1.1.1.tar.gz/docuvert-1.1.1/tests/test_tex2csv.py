import pytest
from converters.tex2csv import Tex2CsvConverter
import os

def test_tex2csv_conversion(tmp_path):
    """
    Tests the LaTeX to CSV conversion.
    """
    input_tex = tmp_path / "dummy.tex"
    output_csv = tmp_path / "output.csv"
    
    # Create a dummy LaTeX file with simple text
    latex_content = """
\documentclass{article}
\begin{document}
Hello, World!
\end{document}
"""
    with open(input_tex, 'w', encoding='utf-8') as f:
        f.write(latex_content)

    converter = Tex2CsvConverter()
    converter.convert(str(input_tex), str(output_csv))

    # Since the dummy LaTeX has no tables, the output CSV should be empty or not created
    assert not os.path.exists(output_csv) or os.path.getsize(output_csv) == 0

# TODO: Add tests for AST generation once implemented.