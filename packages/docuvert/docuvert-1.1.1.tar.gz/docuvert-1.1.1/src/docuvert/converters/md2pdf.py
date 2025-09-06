
import sys
import os
# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.ast import ASTNode
import pypandoc

class Md2PdfConverter:
    """
    Converts a Markdown file to a PDF file.
    """
    def parse_md2ast(self, input_path: str) -> ASTNode:
        """
        Parses a Markdown file and converts it to an AST.

        Args:
            input_path (str): The path to the input Markdown file.

        Returns:
            ASTNode: The root of the generated AST.
        """
        # TODO: Implement the logic to parse the Markdown and build an AST.
        print(f"Parsing Markdown at {input_path} and converting to AST.")
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
        Converts a Markdown file to a PDF file.

        Args:
            input_path (str): The path to the input Markdown file.
            output_path (str): The path to the output PDF file.
        """
        try:
            pypandoc.convert_file(input_path, 'pdf', outputfile=output_path)
            print(f"Successfully converted '{input_path}' to '{output_path}'")
        except Exception as e:
            print(f"Error converting Markdown to PDF: {e}")
