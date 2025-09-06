
import pytest
from converters.txt2tex import Txt2TexConverter
import os

def test_txt2tex_conversion(tmp_path):
    """
    Tests the plain text to LaTeX conversion.
    """
    input_txt = tmp_path / "dummy.txt"
    output_tex = tmp_path / "output.tex"
    
    with open(input_txt, 'w', encoding='utf-8') as f:
        f.write("This is a dummy text document.")

    converter = Txt2TexConverter()
    converter.convert(str(input_txt), str(output_tex))

    assert os.path.exists(output_tex)
    assert os.path.getsize(output_tex) > 0

# TODO: Add tests for AST generation once implemented.
