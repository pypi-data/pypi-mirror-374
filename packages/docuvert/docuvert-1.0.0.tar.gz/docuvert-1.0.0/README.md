# Docuvert

Docuvert is a command-line tool that supports converting documents from any format to any other format.

## Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-repo/docuvert.git
    cd docuvert
    ```

2.  **Run the setup script:**

    ```bash
    ./setup.sh
    ```
    This script will install the necessary dependencies and create a `docuvert` executable wrapper in your project directory. It will also provide instructions on how to set up an alias for easy command-line access.

## Usage

Docuvert converts files based on their extensions. The syntax is simple:

```bash
docuvert <input_file_path> <output_file_path>
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

## Contributing

See `instructions.md` for details on project organization and how to add new converters.