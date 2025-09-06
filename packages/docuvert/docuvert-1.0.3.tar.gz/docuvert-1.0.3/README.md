# Docuvert

Docuvert is a command-line tool that supports converting documents from any format to any other format.

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install docuvert
```

After installation, the `docuvert` command will be globally available in your PATH:

```bash
docuvert --version
docuvert input.pdf output.docx
```

### Option 2: Development Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-repo/docuvert.git
    cd docuvert
    ```

2.  **Install in development mode:**

    ```bash
    pip install -e .
    ```

    Or use the setup script for local development:

    ```bash
    ./setup.sh
    ```

## Usage

Docuvert converts files based on their extensions. The syntax is simple:

```bash
docuvert <input_file_path> <output_file_path>
```

**Basic Commands:**

```bash
# Convert files
docuvert input.pdf output.docx

# Check version
docuvert --version

# Show detailed info (formats, examples, installation)
docuvert --info

# Show help
docuvert --help
```

**Examples:**

-   **Convert PDF to DOCX:**

    ```bash
    docuvert document.pdf document.docx
    ```

-   **Convert Markdown to PDF:**

    ```bash
    docuvert notes.md notes.pdf
    ```

-   **Convert PowerPoint to Obsidian Markdown (NEW!):**

    ```bash
    docuvert presentation.pptx notes.md
    ```

-   **Convert Legacy PowerPoint with automatic conversion:**

    ```bash
    docuvert lecture.ppt lecture.md
    ```

-   **Convert DOCX to Markdown:**

    ```bash
    docuvert report.docx report.md
    ```

## Supported Conversions

Docuvert supports 200+ format combinations with intelligent conversion routing. Key features include:

### 🎯 **PowerPoint Conversions (NEW!)**
-   **PPTX/PPT to Obsidian Markdown** (`pptx2md`, `ppt2md`) - **Featured Converter**
    - ✅ Automatic image extraction and embedding
    - ✅ Format preservation (bold, italic, colors)
    - ✅ Obsidian-specific features (YAML frontmatter, internal links, callouts)
    - ✅ Slide navigation with Previous/Next links
    - ✅ Table of contents generation
    - ✅ Legacy .ppt support via LibreOffice conversion
-   PPTX to PDF (`pptx2pdf`)
-   PPTX to HTML (`pptx2html`)
-   PPTX to Plain Text (`pptx2txt`)
-   Markdown to PPTX (`md2pptx`)

### 📄 **Document Conversions**

-   PDF to DOCX (`pdf2docx`)
-   PDF to Markdown (`pdf2md`)
-   PDF to LaTeX (`pdf2tex`)
-   PDF to Plain Text (`pdf2txt`)
-   PDF to CSV (`pdf2csv`)
-   PDF to XLSX (`pdf2xlsx`)
-   DOCX to PDF (`docx2pdf`)
-   DOCX to Markdown (`docx2md`)
-   DOCX to LaTeX (`docx2tex`)
-   DOCX to Plain Text (`docx2txt`)
-   DOCX to CSV (`docx2csv`)
-   DOCX to XLSX (`docx2xlsx`)
-   Markdown to PDF (`md2pdf`)
-   Markdown to DOCX (`md2docx`)
-   Markdown to LaTeX (`md2tex`)
-   Markdown to Plain Text (`md2txt`)
-   Markdown to CSV (`md2csv`)
-   Markdown to XLSX (`md2xlsx`)
-   LaTeX to PDF (`tex2pdf`)
-   LaTeX to DOCX (`tex2docx`)
-   LaTeX to Markdown (`tex2md`)
-   LaTeX to Plain Text (`tex2txt`)
-   LaTeX to CSV (`tex2csv`)
-   LaTeX to XLSX (`tex2xlsx`)
-   Plain Text to PDF (`txt2pdf`)
-   Plain Text to DOCX (`txt2docx`)
-   Plain Text to Markdown (`txt2md`)
-   Plain Text to LaTeX (`txt2tex`)
-   Plain Text to CSV (`txt2csv`)
-   Plain Text to XLSX (`txt2xlsx`)
-   CSV to PDF (`csv2pdf`)
-   CSV to DOCX (`csv2docx`)
-   CSV to Markdown (`csv2md`)
-   CSV to LaTeX (`csv2tex`)
-   CSV to Plain Text (`csv2txt`)
-   CSV to XLSX (`csv2xlsx`)
-   XLSX to PDF (`xlsx2pdf`)
-   XLSX to DOCX (`xlsx2docx`)
-   XLSX to Markdown (`xlsx2md`)
-   XLSX to LaTeX (`xlsx2tex`)
-   XLSX to Plain Text (`xlsx2txt`)
-   XLSX to CSV (`xlsx2csv`)

## 🔄 Legacy Format Support

Docuvert automatically handles legacy Microsoft Office formats:

### 📝 Legacy Word (.doc) Support
- **Automatic conversion**: `.doc` files are automatically converted to `.docx` format before processing
- **All format combinations supported**: Use any `.doc` to `format` conversion just like `.docx`
- **Examples:**
  ```bash
  docuvert old-document.doc new-document.pdf
  docuvert report.doc report.md
  docuvert legacy.doc modern.docx
  ```

### 📊 Legacy Excel (.xls) Support  
- **Automatic conversion**: `.xls` files are automatically converted to `.xlsx` format before processing
- **All format combinations supported**: Use any `.xls` to `format` conversion just like `.xlsx`
- **Examples:**
  ```bash
  docuvert old-spreadsheet.xls new-spreadsheet.pdf
  docuvert data.xls data.csv
  docuvert legacy.xls modern.xlsx
  ```

### 📋 Requirements for Legacy Formats
- **LibreOffice**: Recommended for best conversion quality
  - Install: [https://www.libreoffice.org/download/](https://www.libreoffice.org/download/)
  - Supports both `.doc` and `.xls` formats
- **Pandoc**: Alternative for `.doc` conversion
  - Install: [https://pandoc.org/installing.html](https://pandoc.org/installing.html)
- **xlrd**: Python library for `.xls` reading (automatically installed)

### 🔧 Conversion Process
1. Docuvert detects legacy format (`.doc` or `.xls`)
2. Creates temporary modern format file (`.docx` or `.xlsx`)
3. Processes conversion using existing converters  
4. Cleans up temporary files automatically
5. Returns final converted output

No additional configuration needed - just use legacy files like modern formats!

## Contributing

See `instructions.md` for details on project organization and how to add new converters.