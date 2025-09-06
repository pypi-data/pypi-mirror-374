
import sys
import os
# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.ast import ASTNode
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class Tex2PdfConverter:
    """
    Converts a LaTeX file to a PDF file.
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
        Converts a LaTeX file to a PDF file.

        Args:
            input_path (str): The path to the input LaTeX file.
            output_path (str): The path to the output PDF file.
        """
        try:
            c = canvas.Canvas(output_path, pagesize=letter)
            with open(input_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            textobject = c.beginText()
            textobject.setTextOrigin(50, 750) # Starting position
            textobject.setFont('Helvetica', 12)

            for line in lines:
                textobject.textLine(line.strip())
            
            c.drawText(textobject)
            c.save()
            print(f"Successfully converted '{input_path}' to '{output_path}'")
        except Exception as e:
            print(f"Error converting LaTeX to PDF: {e}")
