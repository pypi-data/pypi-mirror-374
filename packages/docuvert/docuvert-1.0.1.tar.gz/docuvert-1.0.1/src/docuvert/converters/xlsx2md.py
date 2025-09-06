
import sys
import os
# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.ast import ASTNode
import pandas as pd

class Xlsx2MdConverter:
    """
    Converts an XLSX file to a Markdown file.
    """
    def parse_xlsx2ast(self, input_path: str) -> ASTNode:
        """
        Parses an XLSX file and converts it to an AST.

        Args:
            input_path (str): The path to the input XLSX file.

        Returns:
            ASTNode: The root of the generated AST.
        """
        # TODO: Implement the logic to parse the XLSX and build an AST.
        print(f"Parsing XLSX at {input_path} and converting to AST.")
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
        Converts an XLSX file to a Markdown file.

        Args:
            input_path (str): The path to the input XLSX file.
            output_path (str): The path to the output Markdown file.
        """
        try:
            df = pd.read_excel(input_path)
            markdown_table = df.to_markdown(index=False)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_table)
            
            print(f"Successfully converted '{input_path}' to '{output_path}'")
        except Exception as e:
            print(f"Error converting XLSX to Markdown: {e}")
