

import pytest
from converters.md2txt import Md2TxtConverter
import os

def test_md2txt_conversion(tmp_path):
    """
    Tests the Markdown to plain text conversion.
    """
    input_md = tmp_path / "dummy.md"
    output_txt = tmp_path / "output.txt"
    
    with open(input_md, 'w', encoding='utf-8') as f:
        f.write("# Test Markdown\n\nThis is a test markdown document.")

    converter = Md2TxtConverter()
    converter.convert(str(input_md), str(output_txt))

    assert os.path.exists(output_txt)
    assert os.path.getsize(output_txt) > 0

# TODO: Add tests for AST generation once implemented.

