
import pytest
from converters.txt2md import Txt2MdConverter
import os

def test_txt2md_conversion(tmp_path):
    """
    Tests the plain text to Markdown conversion.
    """
    input_txt = tmp_path / "dummy.txt"
    output_md = tmp_path / "output.md"
    
    with open(input_txt, 'w', encoding='utf-8') as f:
        f.write("This is a dummy text document.")

    converter = Txt2MdConverter()
    converter.convert(str(input_txt), str(output_md))

    assert os.path.exists(output_md)
    assert os.path.getsize(output_md) > 0

# TODO: Add tests for AST generation once implemented.
