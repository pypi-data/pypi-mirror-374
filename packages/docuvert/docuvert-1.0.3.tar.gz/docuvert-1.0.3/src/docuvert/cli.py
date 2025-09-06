import argparse
import importlib
import sys
import os
import tempfile
from docuvert.utils.legacy_converter import LegacyFormatConverter

HEIC_DEFAULT_TARGET = 'jpg'

def get_version():
    """Get the version from pyproject.toml or package metadata."""
    try:
        # Try to get version from importlib.metadata (Python 3.8+)
        from importlib.metadata import version
        return version('docuvert')
    except ImportError:
        # Fallback for older Python versions
        try:
            import pkg_resources
            return pkg_resources.get_distribution('docuvert').version
        except:
            pass
    except:
        pass
    
    # If package isn't installed, try to read from pyproject.toml
    try:
        import re
        # Go up to project root (assuming we're in src/docuvert/)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        pyproject_path = os.path.join(project_root, 'pyproject.toml')
        
        if os.path.exists(pyproject_path):
            with open(pyproject_path, 'r') as f:
                content = f.read()
            match = re.search(r'version = "([^"]+)"', content)
            if match:
                return match.group(1)
    except:
        pass
    
    return "unknown"

def show_info():
    """Display comprehensive package information."""
    version = get_version()
    
    info_text = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                 DOCUVERT                                     ║
║                    Universal Document Converter v{version:<8}                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎯 DESCRIPTION:
   Docuvert supports converting documents between 200+ format combinations.
   Features PowerPoint to Obsidian Markdown with image extraction, format 
   preservation, and navigation links.

📋 SUPPORTED FORMATS:
   📄 Documents: PDF, DOCX, DOC*, ODT, RTF, TXT, MD, HTML, TEX, EPUB
   📊 Spreadsheets: XLSX, XLS*, CSV
   🎨 Presentations: PPTX, PPT*
   🖼️ Images: HEIC, HEIF, JPG, JPEG, PNG, GIF, WEBP, TIFF, SVG
   📝 Data: JSON, YAML, XML
   
   * Legacy formats (.doc, .xls, .ppt) automatically converted

🚀 BASIC USAGE:
   docuvert input.pdf output.docx        # Convert PDF to Word
   docuvert data.csv report.pdf          # Convert CSV to PDF  
   docuvert slides.pptx notes.md         # PowerPoint to Markdown
   docuvert old.doc modern.docx          # Legacy Word conversion
   docuvert image.heic photo.jpg         # HEIC to JPG

🔄 LEGACY FORMAT SUPPORT:
   • .doc files → automatically converted to .docx
   • .xls files → automatically converted to .xlsx  
   • .ppt files → automatically converted to .pptx
   • Requires LibreOffice or Pandoc for best results

⭐ FEATURED CONVERSIONS:
   • PPTX/PPT → Obsidian Markdown (with image extraction)
   • PDF → DOCX (with formatting preservation)
   • Any format → Any format (200+ combinations)

🔧 OPTIONS:
   --version, -v    Show version information
   --info, -i       Show this information screen
   --help, -h       Show usage help

📖 EXAMPLES:
   # Document conversions
   docuvert report.pdf report.docx
   docuvert notes.md presentation.pptx
   docuvert data.xlsx summary.pdf
   
   # Legacy format handling
   docuvert old-document.doc new-document.pdf
   docuvert legacy-data.xls modern-data.csv
   
   # Image conversions  
   docuvert photo.heic photo.jpg
   docuvert image.png document.pdf

🌟 POWERPOINT TO OBSIDIAN MARKDOWN:
   docuvert presentation.pptx notes.md
   • Extracts and embeds images automatically
   • Preserves formatting (bold, italic, colors)
   • Creates navigation links between slides
   • Generates table of contents
   • Obsidian-compatible YAML frontmatter

📦 INSTALLATION:
   pip install docuvert                  # Global installation
   pip install -e .                     # Development mode

🔗 MORE INFO:
   Homepage: https://github.com/avanomme/docuvert
   PyPI: https://pypi.org/project/docuvert/
   License: MIT (with third-party licenses included)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    print(info_text)

def main():
    """Main function for the Docuvert CLI."""
    parser = argparse.ArgumentParser(description="Convert documents from one format to another.")
    parser.add_argument("input_file", nargs='?', help="The input file path.")
    parser.add_argument("output_file", nargs='?', help="The output file path.")
    parser.add_argument("--version", "-v", action="version", version=f"docuvert {get_version()}")
    parser.add_argument("--info", "-i", action="store_true", help="Show detailed package information")

    args = parser.parse_args()
    
    # Handle --info flag
    if args.info:
        show_info()
        sys.exit(0)
    
    # Check if input and output files are provided (unless special flags were used)
    if not args.input_file or not args.output_file:
        parser.print_help()
        sys.exit(1)

    input_ext = os.path.splitext(args.input_file)[1].lstrip('.').lower()
    output_ext = os.path.splitext(args.output_file)[1].lstrip('.').lower()

    # Allow calling with just output filename sans extension for HEIC convenience
    if input_ext in {"heic", "heif"} and not output_ext:
        output_ext = HEIC_DEFAULT_TARGET

    from_format = input_ext
    to_format = output_ext
    original_input_file = args.input_file
    temp_converted_file = None

    # Normalize heif to heic naming for converter module
    if from_format == 'heif':
        from_format = 'heic'

    # Handle legacy formats by auto-converting them
    if from_format == 'doc':
        print(f"Auto-converting .doc to .docx format...")
        try:
            temp_converted_file = LegacyFormatConverter.convert_doc_to_docx(args.input_file)
            args.input_file = temp_converted_file
            from_format = 'docx'
            print(f"Successfully converted to temporary .docx file")
        except Exception as e:
            print(f"Error converting .doc file: {e}")
            print("Please install LibreOffice or Pandoc for .doc file support")
            return
    
    elif from_format == 'xls':
        print(f"Auto-converting .xls to .xlsx format...")
        try:
            temp_converted_file = LegacyFormatConverter.convert_xls_to_xlsx(args.input_file)
            args.input_file = temp_converted_file
            from_format = 'xlsx'
            print(f"Successfully converted to temporary .xlsx file")
        except Exception as e:
            print(f"Error converting .xls file: {e}")
            print("Please install LibreOffice or ensure xlrd is available for .xls file support")
            return

    try:
        # Import the converter module from the package
        converter_module_name = f"{from_format}2{to_format}"
        module_path = f"docuvert.converters.{converter_module_name}"
        
        try:
            converter_module = importlib.import_module(module_path)
        except ImportError:
            print(f"Error: No converter found for {from_format} to {to_format}")
            return
        
        class_name = f"{from_format.capitalize()}2{to_format.capitalize()}Converter"
        converter_class = getattr(converter_module, class_name)
        
        converter = converter_class()
        converter.convert(args.input_file, args.output_file)
        
        print(f"Successfully converted {original_input_file} to {args.output_file}")

    except AttributeError as e:
        print(f"Error: Converter class '{class_name}' not found in {module_path}")
        print(f"Debug: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up temporary converted file if it was created
        if temp_converted_file:
            LegacyFormatConverter.cleanup_temp_file(temp_converted_file)

if __name__ == "__main__":
    main()