
import sys
import os
# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.ast import ASTNode
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

class Csv2PdfConverter:
    """
    Converts a CSV file to a PDF file.
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

    def ast2pdf(self, ast_root: ASTNode, output_path: str):
        """
        Converts an AST to a PDF file.

        Args:
            ast_root (ASTNode): The root of the AST.
            output_path (str): The path to the output PDF file.
        """
        # TODO: Implement the logic to convert the AST to a PDF document.
        print(f"Converting AST to PDF at {output_path}")

    def convert(self, input_path: str, output_path: str):
        """
        Converts a CSV file to a PDF file.

        Args:
            input_path (str): The path to the input CSV file.
            output_path (str): The path to the output PDF file.
        """
        try:
            df = pd.read_csv(input_path)
            data = [df.columns.tolist()] + df.values.tolist()

            doc = SimpleDocTemplate(output_path, pagesize=letter)
            table = Table(data)
            
            # Add style to the table
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                ('GRID', (0,0), (-1,-1), 1, colors.black)
            ]))

            elements = []
            elements.append(table)
            doc.build(elements)
            
            print(f"Successfully converted '{input_path}' to '{output_path}'")
        except Exception as e:
            print(f"Error converting CSV to PDF: {e}")
