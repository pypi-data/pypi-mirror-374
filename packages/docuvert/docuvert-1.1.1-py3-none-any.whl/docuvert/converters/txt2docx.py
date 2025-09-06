
import sys
import os
# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from core.ast import ASTNode
from docx import Document

class Txt2DocxConverter:
    """
    Converts a plain text file to a DOCX file.
    """
    def parse_txt2ast(self, input_path: str) -> ASTNode:
        """
        Parses a plain text file and converts it to an AST.

        Args:
            input_path (str): The path to the input plain text file.

        Returns:
            ASTNode: The root of the generated AST.
        """
        # TODO: Implement the logic to parse the plain text and build an AST.
        print(f"Parsing plain text at {input_path} and converting to AST.")
        return ASTNode(type="root")

    def ast2docx(self, ast_root: ASTNode, output_path: str):
        """
        Converts an AST to a DOCX file.

        Args:
            ast_root (ASTNode): The root of the AST.
            output_path (str): The path to the output DOCX file.
        """
        # TODO: Implement the logic to convert the AST to a DOCX document.
        print(f"Converting AST to DOCX at {output_path}")

    def convert(self, input_path: str, output_path: str):
        """
        Converts a plain text file to a DOCX file.

        Args:
            input_path (str): The path to the input plain text file.
            output_path (str): The path to the output DOCX file.
        """
        try:
            document = Document()
            with open(input_path, 'r', encoding='utf-8') as f:
                for line in f:
                    document.add_paragraph(line.strip())
            document.save(output_path)
            print(f"Successfully converted '{input_path}' to '{output_path}'")
        except Exception as e:
            print(f"Error converting plain text to DOCX: {e}")
