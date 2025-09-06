
import sys
import os
# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.ast import ASTNode
import pypandoc
import pandas as pd

class Tex2XlsxConverter:
    """
    Converts a LaTeX file to an XLSX file.
    """
    def parse_tex2ast(self, input_path: str) -> ASTNode:
        """
        Parses a LaTeX file and converts it to an AST.

        Args:
            input_path (str): The path to the input LaTeX file.

        Returns:
            ASTNode: The root of the generated AST.
        """
        # TODO: Implement the logic to parse the LaTeX and build an AST.
        print(f"Parsing LaTeX at {input_path} and converting to AST.")
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
        Converts a LaTeX file to an XLSX file.

        Args:
            input_path (str): The path to the input LaTeX file.
            output_path (str): The path to the output XLSX file.
        """
        try:
            # Convert LaTeX to plain text
            plain_text = pypandoc.convert_file(input_path, 'plain', format='latex')
            
            # Attempt to read the plain text as CSV and then save as XLSX
            from io import StringIO
            df = pd.read_csv(StringIO(plain_text))
            df.to_excel(output_path, index=False)
            
            print(f"Successfully converted '{input_path}' to '{output_path}'")
        except pd.errors.EmptyDataError:
            print(f"No data found in '{input_path}' to convert to XLSX.")
        except Exception as e:
            print(f"Error converting LaTeX to XLSX: {e}")
