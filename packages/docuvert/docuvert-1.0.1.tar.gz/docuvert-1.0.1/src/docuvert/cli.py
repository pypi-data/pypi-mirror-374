import argparse
import importlib
import sys
import os
import tempfile
from docuvert.utils.legacy_converter import LegacyFormatConverter

HEIC_DEFAULT_TARGET = 'jpg'

def main():
    """Main function for the Docuvert CLI."""
    parser = argparse.ArgumentParser(description="Convert documents from one format to another.")
    parser.add_argument("input_file", help="The input file path.")
    parser.add_argument("output_file", help="The output file path.")

    args = parser.parse_args()

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