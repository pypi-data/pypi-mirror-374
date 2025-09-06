
import sys
import os
# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.ast import ASTNode
import pypandoc
import pandas as pd

class Md2CsvConverter:
    """
    Converts a Markdown file to a CSV file.
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
        Converts a Markdown file to a CSV file.

        Args:
            input_path (str): The path to the input Markdown file.
            output_path (str): The path to the output CSV file.
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            table_data = []
            in_table = False
            for line in lines:
                line = line.strip()
                if line.startswith('|') and '---' not in line:
                    # This is a table row
                    in_table = True
                    # Remove leading/trailing | and split by |
                    row_values = [cell.strip() for cell in line.strip('|').split('|')]
                    table_data.append(row_values)
                elif '---' in line and in_table:
                    # This is the separator line, ignore it
                    continue
                elif in_table and not line.startswith('|'):
                    # End of table
                    in_table = False
                    
            if table_data:
                # The first row is the header
                df = pd.DataFrame(table_data[1:], columns=table_data[0])
                df.to_csv(output_path, index=False)
                print(f"Successfully converted '{input_path}' to '{output_path}'")
            else:
                print(f"No tables found in '{input_path}' to convert to CSV.")
        except Exception as e:
            print(f"Error converting Markdown to CSV: {e}")
