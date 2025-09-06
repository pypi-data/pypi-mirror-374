import argparse
import importlib
import sys
import os

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

    # Normalize heif to heic naming for converter module
    if from_format == 'heif':
        from_format = 'heic'

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

    except AttributeError as e:
        print(f"Error: Converter class '{class_name}' not found in {module_path}")
        print(f"Debug: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()