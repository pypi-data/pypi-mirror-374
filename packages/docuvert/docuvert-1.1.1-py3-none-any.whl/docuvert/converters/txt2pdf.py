
import sys
import os
import re
# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.ast import ASTNode
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.units import inch
import pypandoc

class Txt2PdfConverter:
    """
    Converts a plain text file to a PDF file with proper formatting.
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
        Converts a plain text file to a PDF file with proper formatting.
        
        This method uses a two-step approach:
        1. Convert text to Markdown for better structure detection
        2. Convert Markdown to PDF for proper formatting

        Args:
            input_path (str): The path to the input plain text file.
            output_path (str): The path to the output PDF file.
        """
        try:
            # Method 1: Use the improved txt2md converter, then md2pdf
            import tempfile
            import os
            
            # Get the txt2md converter
            try:
                # Add the converters directory to path
                converters_dir = os.path.dirname(__file__)
                sys.path.insert(0, converters_dir)
                from txt2md import Txt2MdConverter
                sys.path.remove(converters_dir)
            except ImportError:
                # If import fails, skip to ReportLab fallback
                raise ImportError("Could not import txt2md converter")
            
            # Create temporary markdown file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_md:
                temp_md_path = temp_md.name
            
            try:
                # Convert txt to md with proper formatting
                txt2md_converter = Txt2MdConverter()
                txt2md_converter.convert(input_path, temp_md_path)
                
                # Convert md to pdf (which works well with formatting)
                pypandoc.convert_file(
                    temp_md_path, 
                    'pdf', 
                    outputfile=output_path,
                    extra_args=['--pdf-engine=xelatex', '--variable', 'geometry:margin=1in']
                )
                
                print(f"Successfully converted '{input_path}' to '{output_path}'")
                
            except Exception as pandoc_error:
                # Fallback to basic pypandoc if XeLaTeX fails
                try:
                    pypandoc.convert_file(temp_md_path, 'pdf', outputfile=output_path)
                    print(f"Successfully converted '{input_path}' to '{output_path}' (basic format)")
                except Exception:
                    # Final fallback: use ReportLab with better formatting
                    self._convert_with_reportlab(input_path, output_path)
                    
            finally:
                # Clean up temporary file
                if os.path.exists(temp_md_path):
                    os.unlink(temp_md_path)
                    
        except Exception as e:
            print(f"Error converting plain text to PDF: {e}")
            # Last resort: basic ReportLab conversion
            try:
                self._convert_with_reportlab(input_path, output_path)
            except Exception as e2:
                print(f"Final fallback also failed: {e2}")

    def _convert_with_reportlab(self, input_path: str, output_path: str):
        """
        Fallback method using ReportLab with better text formatting.
        """
        doc = SimpleDocTemplate(output_path, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Create custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=12
        )
        
        normal_style = styles['Normal']
        code_style = ParagraphStyle(
            'Code',
            parent=styles['Normal'],
            fontName='Courier',
            fontSize=10,
            backColor='#f0f0f0'
        )
        
        story = []
        
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        i = 0
        while i < len(lines):
            line = lines[i].rstrip()
            
            if not line:
                story.append(Spacer(1, 6))
                i += 1
                continue
                
            # Check for headers (simple heuristic)
            if (len(line) < 60 and 
                (i == 0 or not lines[i-1].strip()) and
                (i+1 >= len(lines) or not lines[i+1].strip()) and
                not line[0].isdigit() and not line.startswith('-')):
                story.append(Paragraph(line, title_style))
                i += 1
                continue
            
            # Check for code blocks
            if line.startswith('    ') or line.startswith('\t'):
                code_lines = []
                while i < len(lines) and (lines[i].startswith('    ') or lines[i].startswith('\t')):
                    clean_line = lines[i][4:] if lines[i].startswith('    ') else lines[i][1:]
                    code_lines.append(clean_line.rstrip())
                    i += 1
                story.append(Preformatted('\n'.join(code_lines), code_style))
                continue
                
            # Regular text
            story.append(Paragraph(line, normal_style))
            i += 1
        
        doc.build(story)
        print(f"Successfully converted '{input_path}' to '{output_path}' using ReportLab")
