
import sys
import os
# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.ast import ASTNode
import pandas as pd

class Csv2MdConverter:
    """
    Converts a CSV file to a Markdown file.
    """
    def parse_csv2ast(self, input_path: str) -> ASTNode:
        """
        Parses a CSV file and converts it to an AST.

        Args:
            input_path (str): The path to the input CSV file.

        Returns:
            ASTNode: The root of the generated AST.
        """
        # TODO: Implement the logic to parse the CSV and build an AST.
        print(f"Parsing CSV at {input_path} and converting to AST.")
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
        Converts a CSV file to a Markdown file.

        Args:
            input_path (str): The path to the input CSV file.
            output_path (str): The path to the output Markdown file.
        """
        try:
            df = pd.read_csv(input_path)
            markdown_table = df.to_markdown(index=False)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_table)
            
            print(f"Successfully converted '{input_path}' to '{output_path}'")
        except Exception as e:
            print(f"Error converting CSV to Markdown: {e}")
