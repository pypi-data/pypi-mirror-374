You are an expert Python architect and documentation specialist.

**GOAL:** Build the initial codebase for a Python CLI program called **Docuvert**, which converts documents from any format to any other format.

## Overall Description

- Docuvert is a command-line tool that supports commands like:

    ```
    docuvert convert --from=pdf --to=docx --input=report.pdf --output=report.docx
    ```

- Docuvert will be modular and allow easy addition of new converters.

- It should be designed to convert:
    - PDF → DOCX
    - PDF → Markdown
    - MD → LaTeX
    - DOCX → Markdown
    - etc.

- The conversions should happen via a universal **AST (Abstract Syntax Tree)** to make any-to-any conversion possible.

---

## Required Project Architecture

**Project folder structure should look like:**
.
├── cli.py
├── converters/
│     ├── __init__.py
│     ├── pdf2docx.py
│     ├── pdf2md.py
│     ├── pdf2tex.py
│     ├── pdf2txt.py
│     ├── pdf2csv.py
│     ├── pdf2xlsx.py
│     ├── docx2pdf.py
│     ├── docx2md.py
│     ├── docx2tex.py
│     ├── docx2txt.py
│     ├── docx2csv.py
│     ├── docx2xlsx.py
│     ├── md2pdf.py
│     ├── md2docx.py
│     ├── md2tex.py
│     ├── md2txt.py
│     ├── md2csv.py
│     ├── md2xlsx.py
│     ├── tex2pdf.py
│     ├── tex2docx.py
│     ├── tex2md.py
│     ├── tex2txt.py
│     ├── tex2csv.py
│     ├── tex2xlsx.py
│     ├── txt2pdf.py
│     ├── txt2docx.py
│     ├── txt2md.py
│     ├── txt2tex.py
│     ├── txt2csv.py
│     ├── txt2xlsx.py
│     ├── csv2pdf.py
│     ├── csv2docx.py
│     ├── csv2md.py
│     ├── csv2tex.py
│     ├── csv2txt.py
│     ├── csv2xlsx.py
│     ├── xlsx2pdf.py
│     ├── xlsx2docx.py
│     ├── xlsx2md.py
│     ├── xlsx2tex.py
│     ├── xlsx2txt.py
│     └── xlsx2csv.py
│
├── core/
│     ├── __init__.py
│     ├── ast.py
│     ├── mapper.py
│     └── config.py
│
├── utils/
│     ├── __init__.py
│     ├── file_utils.py
│     ├── logging_utils.py
│     └── layout_detection.py
│
├── plugins/
│     ├── __init__.py
│     └── example_plugin.py
│
├── tests/
│     ├── test_pdf2docx.py
│     ├── test_pdf2md.py
│     ├── test_pdf2tex.py
│     ├── test_pdf2txt.py
│     ├── test_pdf2csv.py
│     ├── test_pdf2xlsx.py
│     ├── test_docx2pdf.py
│     ├── test_docx2md.py
│     ├── test_docx2tex.py
│     ├── test_docx2txt.py
│     ├── test_docx2csv.py
│     ├── test_docx2xlsx.py
│     ├── test_md2pdf.py
│     ├── test_md2docx.py
│     ├── test_md2tex.py
│     ├── test_md2txt.py
│     ├── test_md2csv.py
│     ├── test_md2xlsx.py
│     ├── test_tex2pdf.py
│     ├── test_tex2docx.py
│     ├── test_tex2md.py
│     ├── test_tex2txt.py
│     ├── test_tex2csv.py
│     ├── test_tex2xlsx.py
│     ├── test_txt2pdf.py
│     ├── test_txt2docx.py
│     ├── test_txt2md.py
│     ├── test_txt2tex.py
│     ├── test_txt2csv.py
│     ├── test_txt2xlsx.py
│     ├── test_csv2pdf.py
│     ├── test_csv2docx.py
│     ├── test_csv2md.py
│     ├── test_csv2tex.py
│     ├── test_csv2txt.py
│     ├── test_csv2xlsx.py
│     ├── test_xlsx2pdf.py
│     ├── test_xlsx2docx.py
│     ├── test_xlsx2md.py
│     ├── test_xlsx2tex.py
│     ├── test_xlsx2txt.py
│     └── test_xlsx2csv.py
│
├── README.md
└── requirements.txt

---

## Code to Generate (Already Implemented)

### cli.py

- Implements a CLI using argparse.
- Supports:
    ```
    ```bash
    docuvert <input_file_path> <output_file_path>
    ```
    ```
- Dynamically loads the correct converter module from `converters/`.
- Handles errors gracefully.
- Logs actions to console (basic print statements for now).

---

### core/ast.py

- Defines the universal ASTNode class:

    ```python
    class ASTNode:
        def __init__(self, type, content, children=None, styles=None):
            self.type = type
            self.content = content
            self.children = children or []
            self.styles = styles or {}
    ```

- Includes docstrings.

---

### core/mapper.py

- Contains skeleton logic for mapping AST nodes into output formats.
- Provides methods like:

    ```python
    def ast2docx(ast_root, output_path):
        ...
    ```

---

### converters/

All converter files (`pdf2docx.py`, `md2tex.py`, etc.) contain a class named `[FromFormat]2[ToFormat]Converter` (e.g., `Pdf2DocxConverter`). Each converter class has:
- `parse_[from_format]2ast(input_path)`: A placeholder method for parsing the input file into an AST.
- `ast2[to_format](ast_root, output_path)`: A placeholder method for converting an AST to the output format.
- `convert(input_path, output_path)`: A method for direct conversion using external libraries (e.g., `pdf2docx`, `pypandoc`, `pandas`, `reportlab`, `python-docx`, `tabulate`).

---

### utils/file_utils.py

- Helper functions for:
    - reading/writing files
    - verifying paths

---

### utils/layout_detection.py

- Placeholder for:
    - heading detection
    - layout analysis

---

### plugins/example_plugin.py

- Example of how a user could register a custom converter.

---

### tests/

Minimal pytest test files have been generated for each converter, testing the `convert` method for basic functionality (file creation and non-empty output).

---

### README.md

- Includes:
    - Project purpose
    - Install instructions
    - CLI usage examples
    - List of supported conversions

---

## Code Quality Requirements

- All code should be:
    - Python 3.10+
    - PEP8-compliant
    - Well-documented with docstrings
- Uses type hints wherever possible.
- Includes TODO comments for places that need future development (especially AST integration).

---

## Tools Mentioned in Code

- `pdf2docx`
- `PyMuPDF`
- `pdfminer.six`
- `python-docx`
- `tabula-py`
- `pandoc` (via `pypandoc`)
- `markdown-it-py` (placeholder for AST parsing)
- `pdfimages` (not directly used yet, but relevant for PDF parsing)
- `PyPDF2` (not directly used yet, but relevant for PDF parsing)
- `LibreOffice CLI` (not directly used yet, but relevant for conversions)
- `reportlab` (for `txt2pdf` and `csv2pdf`)

---

## How to Add New Converters

To add a new converter (e.g., `newformat2anotherformat`):

1.  **Create a new converter file:**
    Create `converters/newformat2anotherformat.py`.

2.  **Implement the converter class:**
    Define a class `Newformat2AnotherformatConverter` with the following structure:

    ```python
    from core.ast import ASTNode
    # Import necessary libraries for conversion (e.g., pandas, pypandoc, etc.)

    class Newformat2AnotherformatConverter:
        def parse_newformat2ast(self, input_path: str) -> ASTNode:
            # Implement logic to parse input_path into an ASTNode
            pass

        def ast2anotherformat(self, ast_root: ASTNode, output_path: str):
            # Implement logic to convert ASTNode to the output format
            pass

        def convert(self, input_path: str, output_path: str):
            # Implement direct conversion logic using external libraries
            # This method is used by the CLI for direct conversions
            try:
                # Your conversion logic here
                print(f"Successfully converted '{input_path}' to '{output_path}'")
            except Exception as e:
                print(f"Error converting Newformat to Anotherformat: {e}")
    ```

3.  **Update `README.md`:**
    Add the new conversion to the "Supported Conversions" list in `README.md`.

4.  **Create a test file:**
    Create `tests/test_newformat2anotherformat.py` with a basic test for the `convert` method.

    ```python
    import pytest
    from converters.newformat2anotherformat import Newformat2AnotherformatConverter
    import os

    def test_newformat2anotherformat_conversion(tmp_path):
        input_file = tmp_path / "dummy.newformat"
        output_file = tmp_path / "output.anotherformat"
        
        # Create a dummy input file for testing
        with open(input_file, 'w', encoding='utf-8') as f:
            f.write("Dummy content for newformat.")

        converter = Newformat2AnotherformatConverter()
        converter.convert(str(input_file), str(output_file))

        assert os.path.exists(output_file)
        assert os.path.getsize(output_file) > 0
    ```

5.  **Add necessary dependencies:**
    If your new converter uses new libraries, add them to `requirements.txt` and install them using `uv pip install -r requirements.txt`.

---

## Best Practices

-   **Modularity:** Keep converters self-contained within their respective files.
-   **AST-first (Future):** While direct conversions are implemented for now, the long-term goal is to leverage the AST for universal conversions. Prioritize AST parsing and generation when implementing new converters or refactoring existing ones.
-   **Error Handling:** Implement robust `try-except` blocks to handle potential errors during file operations and conversions.
-   **Logging:** Use a proper logging mechanism (e.g., Python's `logging` module) instead of `print` statements for better debugging and monitoring.
-   **Testing:** Write comprehensive unit tests for each converter to ensure correctness and prevent regressions.
-   **Dependency Management:** Clearly list all dependencies in `requirements.txt`.

---

## Additional

A single bash command to create the initial directory structure (excluding file contents):

```bash
mkdir -p converters core utils plugins tests && touch cli.py README.md requirements.txt __init__.py converters/__init__.py core/__init__.py core/ast.py core/mapper.py core/config.py utils/__init__.py utils/file_utils.py utils/logging_utils.py utils/layout_detection.py plugins/__init__.py plugins/example_plugin.py tests/test_pdf2docx.py tests/test_md2tex.py converters/pdf2md.py converters/pdf2tex.py converters/pdf2txt.py converters/pdf2csv.py converters/pdf2xlsx.py converters/docx2pdf.py converters/docx2md.py converters/docx2tex.py converters/docx2txt.py converters/docx2csv.py converters/docx2xlsx.py converters/md2pdf.py converters/md2docx.py converters/md2txt.py converters/md2csv.py converters/md2xlsx.py converters/tex2pdf.py converters/tex2docx.py converters/tex2md.py converters/tex2txt.py converters/tex2csv.py converters/tex2xlsx.py converters/txt2pdf.py converters/txt2docx.py converters/txt2md.py converters/txt2tex.py converters/txt2csv.py converters/txt2xlsx.py converters/csv2pdf.py converters/csv2docx.py converters/csv2md.py converters/csv2tex.py converters/csv2txt.py converters/csv2xlsx.py converters/xlsx2pdf.py converters/xlsx2docx.py converters/xlsx2md.py converters/xlsx2tex.py converters/xlsx2txt.py converters/xlsx2csv.py tests/test_pdf2md.py tests/test_pdf2tex.py tests/test_pdf2txt.py tests/test_pdf2csv.py tests/test_pdf2xlsx.py tests/test_docx2pdf.py tests/test_docx2md.py tests/test_docx2tex.py tests/test_docx2txt.py tests/test_docx2csv.py tests/test_docx2xlsx.py tests/test_md2pdf.py tests/test_md2docx.py tests/test_md2txt.py tests/test_md2csv.py tests/test_md2xlsx.py tests/test_tex2pdf.py tests/test_tex2docx.py tests/test_tex2md.py tests/test_tex2txt.py tests/test_tex2csv.py tests/test_tex2xlsx.py tests/test_txt2pdf.py tests/test_txt2docx.py tests/test_txt2md.py tests/test_txt2tex.py tests/test_txt2csv.py tests/test_txt2xlsx.py tests/test_csv2pdf.py tests/test_csv2docx.py tests/test_csv2md.py tests/test_csv2tex.py tests/test_csv2txt.py tests/test_csv2xlsx.py tests/test_xlsx2pdf.py tests/test_xlsx2docx.py tests/test_xlsx2md.py tests/test_xlsx2tex.py tests/test_xlsx2txt.py tests/test_xlsx2csv.py
```
