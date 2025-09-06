
import sys
import os
# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.ast import ASTNode
import pypandoc

class Docx2PdfConverter:
    """
    Converts a DOCX file to a PDF file.
    """
    def parse_docx2ast(self, input_path: str) -> ASTNode:
        """
        Parses a DOCX file and converts it to an AST.

        Args:
            input_path (str): The path to the input DOCX file.

        Returns:
            ASTNode: The root of the generated AST.
        """
        # TODO: Implement the logic to parse the DOCX and build an AST.
        print(f"Parsing DOCX at {input_path} and converting to AST.")
        return ASTNode(type="root")

    def ast2pdf(self, ast_root: ASTNode, output_path: str):
        """
        Converts an AST to a PDF file.

        Args:
            ast_root (ASTNode): The root of the AST.
            output_path (str): The path to the output PDF file.
        """
        # TODO: Implement the logic to convert the AST to a PDF document.
        print(f"Converting AST to PDF at {output_path}")

    def convert(self, input_path: str, output_path: str):
        """
        Converts a DOCX file to a PDF file with preserved formatting.

        Args:
            input_path (str): The path to the input DOCX file.
            output_path (str): The path to the output PDF file.
        """
        try:
            # Use pypandoc with PDF engine options to preserve formatting
            pypandoc.convert_file(
                input_path, 
                'pdf', 
                outputfile=output_path,
                extra_args=['--pdf-engine=xelatex', '--variable', 'geometry:margin=1in']
            )
            print(f"Successfully converted '{input_path}' to '{output_path}'")
        except Exception as e:
            # Fallback to basic conversion if XeLaTeX is not available
            try:
                pypandoc.convert_file(input_path, 'pdf', outputfile=output_path)
                print(f"Successfully converted '{input_path}' to '{output_path}' (basic format)")
            except Exception as e2:
                print(f"Error converting DOCX to PDF: {e2}")
