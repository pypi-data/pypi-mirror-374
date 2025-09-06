
import sys
import os
# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.ast import ASTNode
import pandas as pd

class Txt2XlsxConverter:
    """
    Converts a plain text file to an XLSX file.
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
        Converts a plain text file to an XLSX file.
        
        Creates an Excel file with the text content in the first column,
        with each line as a separate row.

        Args:
            input_path (str): The path to the input plain text file.
            output_path (str): The path to the output XLSX file.
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Create a DataFrame with text content
            # Each line becomes a row in the first column
            text_data = []
            for line in lines:
                text_data.append([line.rstrip('\n\r')])
            
            df = pd.DataFrame(text_data, columns=['Text Content'])
            df.to_excel(output_path, index=False)
            
            print(f"Successfully converted '{input_path}' to '{output_path}'")
        except Exception as e:
            print(f"Error converting plain text to XLSX: {e}")
