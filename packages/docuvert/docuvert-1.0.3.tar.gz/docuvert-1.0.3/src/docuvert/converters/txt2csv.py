
import sys
import os
# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.ast import ASTNode
import pandas as pd
from io import StringIO

class Txt2CsvConverter:
    """
    Converts a plain text file to a CSV file.
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
        Converts a plain text file to a CSV file.

        Args:
            input_path (str): The path to the input plain text file.
            output_path (str): The path to the output CSV file.
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
            
            df = pd.read_csv(StringIO(text_content))
            df.to_csv(output_path, index=False)
            
            print(f"Successfully converted '{input_path}' to '{output_path}'")
        except pd.errors.EmptyDataError:
            print(f"No data found in '{input_path}' to convert to CSV.")
        except Exception as e:
            print(f"Error converting plain text to CSV: {e}")
