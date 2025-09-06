
import sys
import os
# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.ast import ASTNode
from docx import Document
import pandas as pd

class Docx2CsvConverter:
    """
    Converts a DOCX file to a CSV file.
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
        Converts a DOCX file to a CSV file.

        Args:
            input_path (str): The path to the input DOCX file.
            output_path (str): The path to the output CSV file.
        """
        try:
            document = Document(input_path)
            all_tables = []
            for table in document.tables:
                data = []
                keys = None
                for i, row in enumerate(table.rows):
                    text = [cell.text for cell in row.cells]
                    if i == 0:
                        keys = text
                    else:
                        data.append(text)
                if keys:
                    df = pd.DataFrame(data, columns=keys)
                    all_tables.append(df)
            
            if all_tables:
                combined_df = pd.concat(all_tables)
                combined_df.to_csv(output_path, index=False)
                print(f"Successfully converted '{input_path}' to '{output_path}'")
            else:
                print(f"No tables found in '{input_path}' to convert to CSV.")
        except Exception as e:
            print(f"Error converting DOCX to CSV: {e}")
