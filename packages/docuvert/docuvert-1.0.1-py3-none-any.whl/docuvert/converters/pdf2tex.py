
import sys
import os
# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.ast import ASTNode
import pdfplumber
import pypandoc

class Pdf2TexConverter:
    """
    Converts a PDF file to a LaTeX file.
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

    def ast2tex(self, ast_root: ASTNode, output_path: str):
        """
        Converts an AST to a LaTeX file.

        Args:
            ast_root (ASTNode): The root of the AST.
            output_path (str): The path to the output LaTeX file.
        """
        # TODO: Implement the logic to convert the AST to a LaTeX document.
        print(f"Converting AST to LaTeX at {output_path}")

    def convert(self, input_path: str, output_path: str):
        """
        Converts a PDF file to a LaTeX file.

        Args:
            input_path (str): The path to the input PDF file.
            output_path (str): The path to the output LaTeX file.
        """
        try:
            text = ""
            with pdfplumber.open(input_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n\n"
            
            # Use pypandoc to convert text to LaTeX
            latex_content = pypandoc.convert_text(text, 'latex', format='markdown')
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            
            print(f"Successfully converted '{input_path}' to '{output_path}'")
        except Exception as e:
            print(f"Error converting PDF to LaTeX: {e}")
