
import sys
import os
# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.ast import ASTNode
import pandas as pd

class Xlsx2CsvConverter:
    """
    Converts an XLSX file to a CSV file.
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

    def ast2csv(self, ast_root: ASTNode, output_path: str):
        """
        Converts an AST to a CSV file.

        Args:
            ast_root (ASTNode): The root of the AST.
            output_path (str): The path to the output CSV file.
        """
        # TODO: Implement the logic to convert the AST to a CSV document.
        print(f"Converting AST to CSV at {output_path}")

    def convert(self, input_path: str, output_path: str):
        """
        Converts an XLSX file to a CSV file.

        Args:
            input_path (str): The path to the input XLSX file.
            output_path (str): The path to the output CSV file.
        """
        try:
            df = pd.read_excel(input_path)
            df.to_csv(output_path, index=False)
            
            print(f"Successfully converted '{input_path}' to '{output_path}'")
        except Exception as e:
            print(f"Error converting XLSX to CSV: {e}")
