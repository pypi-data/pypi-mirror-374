
import sys
import os
# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.ast import ASTNode
import pypandoc

class Docx2MdConverter:
    """
    Converts a DOCX file to a Markdown file.
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

    def ast2md(self, ast_root: ASTNode, output_path: str):
        """
        Converts an AST to a Markdown file.

        Args:
            ast_root (ASTNode): The root of the AST.
            output_path (str): The path to the output Markdown file.
        """
        # TODO: Implement the logic to convert the AST to a Markdown document.
        print(f"Converting AST to Markdown at {output_path}")

    def convert(self, input_path: str, output_path: str):
        """
        Converts a DOCX file to a Markdown file.

        Args:
            input_path (str): The path to the input DOCX file.
            output_path (str): The path to the output Markdown file.
        """
        try:
            pypandoc.convert_file(input_path, 'markdown', outputfile=output_path)
            print(f"Successfully converted '{input_path}' to '{output_path}'")
        except Exception as e:
            print(f"Error converting DOCX to Markdown: {e}")
