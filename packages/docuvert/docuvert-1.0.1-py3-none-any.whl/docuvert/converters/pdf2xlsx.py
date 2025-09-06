
import sys
import os
# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.ast import ASTNode
import pdfplumber
import pandas as pd

class Pdf2XlsxConverter:
    """
    Converts a PDF file to an XLSX file.
    """
    def parse_pdf2ast(self, input_path: str) -> ASTNode:
        """
        Parses a PDF file and converts it to an AST.

        Args:
            input_path (str): The path to the input PDF file.

        Returns:
            ASTNode: The root of the generated AST.
        """
        # TODO: Implement the logic to parse the PDF and build an AST.
        print(f"Parsing PDF at {input_path} and converting to AST.")
        return ASTNode(type="root")

    def ast2xlsx(self, ast_root: ASTNode, output_path: str):
        """
        Converts an AST to an XLSX file.

        Args:
            ast_root (ASTNode): The root of the AST.
            output_path (str): The path to the output XLSX file.
        """
        # TODO: Implement the logic to convert the AST to an XLSX document.
        print(f"Converting AST to XLSX at {output_path}")

    def convert(self, input_path: str, output_path: str):
        """
        Converts a PDF file to an XLSX file.

        Args:
            input_path (str): The path to the input PDF file.
            output_path (str): The path to the output XLSX file.
        """
        try:
            all_tables = []
            with pdfplumber.open(input_path) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for table in tables:
                        df = pd.DataFrame(table[1:], columns=table[0])
                        all_tables.append(df)
            
            if all_tables:
                # Concatenate all tables into a single DataFrame
                combined_df = pd.concat(all_tables)
                combined_df.to_excel(output_path, index=False)
                print(f"Successfully converted '{input_path}' to '{output_path}'")
            else:
                print(f"No tables found in '{input_path}' to convert to XLSX.")
        except Exception as e:
            print(f"Error converting PDF to XLSX: {e}")
