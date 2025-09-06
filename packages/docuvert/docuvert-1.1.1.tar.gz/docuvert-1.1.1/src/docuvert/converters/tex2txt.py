
import sys
import os
# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.ast import ASTNode
import pypandoc

class Tex2TxtConverter:
    """
    Converts a LaTeX file to a plain text file.
    """
    def parse_tex2ast(self, input_path: str) -> ASTNode:
        """
        Parses a LaTeX file and converts it to an AST.

        Args:
            input_path (str): The path to the input LaTeX file.

        Returns:
            ASTNode: The root of the generated AST.
        """
        # TODO: Implement the logic to parse the LaTeX and build an AST.
        print(f"Parsing LaTeX at {input_path} and converting to AST.")
        return ASTNode(type="root")

    def ast2txt(self, ast_root: ASTNode, output_path: str):
        """
        Converts an AST to a plain text file.

        Args:
            ast_root (ASTNode): The root of the AST.
            output_path (str): The path to the output plain text file.
        """
        # TODO: Implement the logic to convert the AST to a plain text document.
        print(f"Converting AST to plain text at {output_path}")

    def convert(self, input_path: str, output_path: str):
        """
        Converts a LaTeX file to a plain text file.

        Args:
            input_path (str): The path to the input LaTeX file.
            output_path (str): The path to the output plain text file.
        """
        try:
            pypandoc.convert_file(input_path, 'plain', outputfile=output_path)
            print(f"Successfully converted '{input_path}' to '{output_path}'")
        except Exception as e:
            print(f"Error converting LaTeX to plain text: {e}")
