
import sys
import os
# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.ast import ASTNode
from docx import Document

class Docx2TxtConverter:
    """
    Converts a DOCX file to a plain text file.
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

    def ast2txt(self, ast_root: ASTNode, output_path: str):
        """
        Converts an AST to a plain text file.

        Args:
            ast_root (ASTNode): The root of the AST.
            output_path (str): The path to the output plain text file.
        """
        # TODO: Implement the logic to convert the AST to a plain text document.
        print(f"Converting AST to plain text at {output_path}")

    def convert(self, input_path: str, output_path: str):
        """
        Converts a DOCX file to a plain text file.

        Args:
            input_path (str): The path to the input DOCX file.
            output_path (str): The path to the output plain text file.
        """
        try:
            document = Document(input_path)
            text_content = []
            for paragraph in document.paragraphs:
                text_content.append(paragraph.text)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(text_content))
            
            print(f"Successfully converted '{input_path}' to '{output_path}'")
        except Exception as e:
            print(f"Error converting DOCX to plain text: {e}")
