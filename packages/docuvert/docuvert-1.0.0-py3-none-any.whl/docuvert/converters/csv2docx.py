
import sys
import os
# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.ast import ASTNode
import pandas as pd
from docx import Document
from docx.shared import Inches

class Csv2DocxConverter:
    """
    Converts a CSV file to a DOCX file.
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
        Converts a CSV file to a DOCX file.

        Args:
            input_path (str): The path to the input CSV file.
            output_path (str): The path to the output DOCX file.
        """
        try:
            df = pd.read_csv(input_path)
            document = Document()
            
            # Add a table to the document
            table = document.add_table(rows=1, cols=len(df.columns))
            table.autofit = True
            
            # Add header row
            hdr_cells = table.rows[0].cells
            for i, col_name in enumerate(df.columns):
                hdr_cells[i].text = str(col_name)
            
            # Add data rows
            for index, row in df.iterrows():
                row_cells = table.add_row().cells
                for i, cell_value in enumerate(row):
                    row_cells[i].text = str(cell_value)
            
            document.save(output_path)
            print(f"Successfully converted '{input_path}' to '{output_path}'")
        except Exception as e:
            print(f"Error converting CSV to DOCX: {e}")
