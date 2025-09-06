"""
RTF to Markdown converter with formatting preservation.
"""

import sys
import os
import re
from typing import Optional, List, Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.ast import ASTNode, NodeType, StyleInfo, DocumentMetadata, create_document, create_paragraph, create_heading
from core.exceptions import ConversionError, DependencyError


class Rtf2MdConverter:
    """Converts RTF files to Markdown format."""

    def __init__(self):
        self.rtf_commands = {
            'b': 'bold',
            'i': 'italic', 
            'ul': 'underline',
            'strike': 'strikethrough'
        }

    def parse_rtf2ast(self, input_path: str) -> ASTNode:
        """Parse RTF file and convert to AST representation."""
        
        try:
            # Method 1: Use striprtf library if available
            return self._parse_with_striprtf(input_path)
        except Exception as striprtf_error:
            try:
                # Method 2: Basic RTF parsing
                return self._parse_rtf_basic(input_path)
            except Exception as basic_error:
                raise ConversionError(
                    f"RTF parsing failed. striprtf: {striprtf_error}, basic: {basic_error}",
                    source_format="rtf",
                    suggestions=[
                        "Install striprtf: pip install striprtf",
                        "Check that the RTF file is valid and not corrupted"
                    ]
                )

    def _parse_with_striprtf(self, input_path: str) -> ASTNode:
        """Parse RTF using striprtf library."""
        try:
            from striprtf.striprtf import rtf_to_text
        except ImportError as e:
            raise DependencyError(
                "striprtf library is required for RTF parsing",
                missing_dependency="striprtf"
            ) from e

        with open(input_path, 'r', encoding='utf-8') as f:
            rtf_content = f.read()

        # Extract plain text
        plain_text = rtf_to_text(rtf_content)
        
        # Create basic AST structure
        doc = create_document()
        
        # Split into paragraphs and create nodes
        paragraphs = plain_text.split('\\n\\n')
        for para_text in paragraphs:
            para_text = para_text.strip()
            if para_text:
                doc.add_child(create_paragraph(para_text))

        return doc

    def _parse_rtf_basic(self, input_path: str) -> ASTNode:
        """Basic RTF parsing without external libraries."""
        
        with open(input_path, 'r', encoding='utf-8') as f:
            rtf_content = f.read()

        # Remove RTF control codes and extract text
        # This is a simplified parser - RTF is complex
        text_content = self._extract_text_from_rtf(rtf_content)
        
        doc = create_document()
        
        # Basic paragraph splitting
        paragraphs = text_content.split('\\n\\n')
        for para_text in paragraphs:
            para_text = para_text.strip()
            if para_text:
                doc.add_child(create_paragraph(para_text))

        return doc

    def _extract_text_from_rtf(self, rtf_content: str) -> str:
        """Extract plain text from RTF content."""
        
        # Remove RTF header
        content = rtf_content
        
        # Remove control words and groups
        # This is very basic - real RTF parsing is much more complex
        content = re.sub(r'\\[a-zA-Z]+\d*[ ]?', '', content)  # Control words
        content = re.sub(r'\\[\'\\][\da-fA-F]{2}', '', content)  # Hex codes
        content = re.sub(r'[{}]', '', content)  # Braces
        content = re.sub(r'\\[^a-zA-Z]', '', content)  # Other escape sequences
        
        # Clean up whitespace
        content = re.sub(r'\\s+', ' ', content)
        content = re.sub(r'\\n+', '\\n', content)
        
        return content.strip()

    def ast2md(self, ast_root: ASTNode, output_path: str) -> None:
        """Convert AST to Markdown format."""
        from core.mapper import ast2md
        ast2md(ast_root, output_path)

    def convert(self, input_path: str, output_path: str) -> None:
        """Convert RTF to Markdown."""
        
        try:
            # AST-based conversion
            ast_root = self.parse_rtf2ast(input_path)
            self.ast2md(ast_root, output_path)
            print(f"Successfully converted '{input_path}' to '{output_path}'")
            
        except Exception as e:
            raise ConversionError(
                f"RTF to Markdown conversion failed: {e}",
                source_format="rtf",
                target_format="md"
            )


class Rtf2DocxConverter:
    """Converts RTF files to DOCX format."""

    def parse_rtf2ast(self, input_path: str) -> ASTNode:
        """Parse RTF file and convert to AST representation."""
        rtf_converter = Rtf2MdConverter()
        return rtf_converter.parse_rtf2ast(input_path)

    def ast2docx(self, ast_root: ASTNode, output_path: str) -> None:
        """Convert AST to DOCX format."""
        from core.mapper import ast2docx
        ast2docx(ast_root, output_path)

    def convert(self, input_path: str, output_path: str) -> None:
        """Convert RTF to DOCX."""
        
        try:
            # Method 1: AST-based conversion
            ast_root = self.parse_rtf2ast(input_path)
            self.ast2docx(ast_root, output_path)
            print(f"Successfully converted '{input_path}' to '{output_path}' (AST method)")
            
        except Exception as ast_error:
            try:
                # Method 2: Pandoc fallback
                self._convert_with_pandoc(input_path, output_path)
                print(f"Successfully converted '{input_path}' to '{output_path}' (pandoc fallback)")
                
            except Exception as pandoc_error:
                raise ConversionError(
                    f"RTF to DOCX conversion failed. AST: {ast_error}, Pandoc: {pandoc_error}",
                    source_format="rtf",
                    target_format="docx"
                )

    def _convert_with_pandoc(self, input_path: str, output_path: str) -> None:
        """Fallback conversion using pandoc."""
        try:
            import pypandoc
            pypandoc.convert_file(input_path, 'docx', outputfile=output_path)
        except ImportError as e:
            raise DependencyError(
                "pypandoc is required for pandoc fallback conversion",
                missing_dependency="pypandoc"
            ) from e


class Rtf2PdfConverter:
    """Converts RTF files to PDF format."""

    def parse_rtf2ast(self, input_path: str) -> ASTNode:
        """Parse RTF file and convert to AST representation."""
        rtf_converter = Rtf2MdConverter()
        return rtf_converter.parse_rtf2ast(input_path)

    def ast2pdf(self, ast_root: ASTNode, output_path: str) -> None:
        """Convert AST to PDF via HTML intermediate."""
        import tempfile
        
        # Create temporary HTML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as temp_html:
            from core.mapper import ast2html
            ast2html(ast_root, temp_html.name)
            
            # Convert HTML to PDF
            try:
                from .html2pdf import Html2PdfConverter
                pdf_converter = Html2PdfConverter()
                pdf_converter.convert(temp_html.name, output_path)
            finally:
                os.unlink(temp_html.name)

    def convert(self, input_path: str, output_path: str) -> None:
        """Convert RTF to PDF."""
        
        try:
            # AST-based conversion via HTML
            ast_root = self.parse_rtf2ast(input_path)
            self.ast2pdf(ast_root, output_path)
            print(f"Successfully converted '{input_path}' to '{output_path}'")
            
        except Exception as e:
            raise ConversionError(
                f"RTF to PDF conversion failed: {e}",
                source_format="rtf",
                target_format="pdf"
            )


class Rtf2TxtConverter:
    """Converts RTF files to plain text format."""

    def parse_rtf2ast(self, input_path: str) -> ASTNode:
        """Parse RTF file and convert to AST representation."""
        rtf_converter = Rtf2MdConverter()
        return rtf_converter.parse_rtf2ast(input_path)

    def ast2txt(self, ast_root: ASTNode, output_path: str) -> None:
        """Convert AST to plain text format."""
        from core.mapper import ast2txt
        ast2txt(ast_root, output_path)

    def convert(self, input_path: str, output_path: str) -> None:
        """Convert RTF to plain text."""
        
        try:
            # Method 1: Direct striprtf conversion
            self._convert_direct(input_path, output_path)
            print(f"Successfully converted '{input_path}' to '{output_path}' (direct method)")
            
        except Exception as direct_error:
            try:
                # Method 2: AST-based conversion
                ast_root = self.parse_rtf2ast(input_path)
                self.ast2txt(ast_root, output_path)
                print(f"Successfully converted '{input_path}' to '{output_path}' (AST method)")
                
            except Exception as ast_error:
                raise ConversionError(
                    f"RTF to TXT conversion failed. Direct: {direct_error}, AST: {ast_error}",
                    source_format="rtf",
                    target_format="txt"
                )

    def _convert_direct(self, input_path: str, output_path: str) -> None:
        """Direct RTF to text conversion."""
        try:
            from striprtf.striprtf import rtf_to_text
        except ImportError as e:
            raise DependencyError(
                "striprtf library is required for direct RTF conversion",
                missing_dependency="striprtf"
            ) from e

        with open(input_path, 'r', encoding='utf-8') as f:
            rtf_content = f.read()

        plain_text = rtf_to_text(rtf_content)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(plain_text)


class Rtf2HtmlConverter:
    """Converts RTF files to HTML format."""

    def parse_rtf2ast(self, input_path: str) -> ASTNode:
        """Parse RTF file and convert to AST representation."""
        rtf_converter = Rtf2MdConverter()
        return rtf_converter.parse_rtf2ast(input_path)

    def ast2html(self, ast_root: ASTNode, output_path: str) -> None:
        """Convert AST to HTML format."""
        from core.mapper import ast2html
        ast2html(ast_root, output_path)

    def convert(self, input_path: str, output_path: str) -> None:
        """Convert RTF to HTML."""
        
        try:
            # AST-based conversion
            ast_root = self.parse_rtf2ast(input_path)
            self.ast2html(ast_root, output_path)
            print(f"Successfully converted '{input_path}' to '{output_path}'")
            
        except Exception as e:
            raise ConversionError(
                f"RTF to HTML conversion failed: {e}",
                source_format="rtf",
                target_format="html"
            )


# Reverse converters (other formats to RTF)

class Md2RtfConverter:
    """Converts Markdown files to RTF format."""

    def parse_md2ast(self, input_path: str) -> ASTNode:
        """Parse Markdown to AST representation."""
        from .md2html import Md2HtmlConverter
        md_converter = Md2HtmlConverter()
        return md_converter.parse_md2ast(input_path)

    def ast2rtf(self, ast_root: ASTNode, output_path: str) -> None:
        """Convert AST to RTF format."""
        from core.mapper import ast2rtf
        ast2rtf(ast_root, output_path)

    def convert(self, input_path: str, output_path: str) -> None:
        """Convert Markdown to RTF."""
        
        try:
            # AST-based conversion
            ast_root = self.parse_md2ast(input_path)
            self.ast2rtf(ast_root, output_path)
            print(f"Successfully converted '{input_path}' to '{output_path}'")
            
        except Exception as ast_error:
            try:
                # Pandoc fallback
                self._convert_with_pandoc(input_path, output_path)
                print(f"Successfully converted '{input_path}' to '{output_path}' (pandoc fallback)")
                
            except Exception as pandoc_error:
                raise ConversionError(
                    f"Markdown to RTF conversion failed. AST: {ast_error}, Pandoc: {pandoc_error}",
                    source_format="md",
                    target_format="rtf"
                )

    def _convert_with_pandoc(self, input_path: str, output_path: str) -> None:
        """Fallback conversion using pandoc."""
        try:
            import pypandoc
            pypandoc.convert_file(input_path, 'rtf', outputfile=output_path)
        except ImportError as e:
            raise DependencyError(
                "pypandoc is required for pandoc fallback conversion",
                missing_dependency="pypandoc"
            ) from e


class Docx2RtfConverter:
    """Converts DOCX files to RTF format."""

    def parse_docx2ast(self, input_path: str) -> ASTNode:
        """Parse DOCX to AST representation."""
        from .md2html import Docx2HtmlConverter
        docx_converter = Docx2HtmlConverter()
        return docx_converter.parse_docx2ast(input_path)

    def ast2rtf(self, ast_root: ASTNode, output_path: str) -> None:
        """Convert AST to RTF format.""" 
        from core.mapper import ast2rtf
        ast2rtf(ast_root, output_path)

    def convert(self, input_path: str, output_path: str) -> None:
        """Convert DOCX to RTF."""
        
        try:
            # Method 1: AST-based conversion
            ast_root = self.parse_docx2ast(input_path)
            self.ast2rtf(ast_root, output_path)
            print(f"Successfully converted '{input_path}' to '{output_path}' (AST method)")
            
        except Exception as ast_error:
            try:
                # Method 2: Pandoc fallback  
                self._convert_with_pandoc(input_path, output_path)
                print(f"Successfully converted '{input_path}' to '{output_path}' (pandoc fallback)")
                
            except Exception as pandoc_error:
                raise ConversionError(
                    f"DOCX to RTF conversion failed. AST: {ast_error}, Pandoc: {pandoc_error}",
                    source_format="docx",
                    target_format="rtf"
                )

    def _convert_with_pandoc(self, input_path: str, output_path: str) -> None:
        """Fallback conversion using pandoc."""
        try:
            import pypandoc
            pypandoc.convert_file(input_path, 'rtf', outputfile=output_path)
        except ImportError as e:
            raise DependencyError(
                "pypandoc is required for pandoc fallback conversion",
                missing_dependency="pypandoc"
            ) from e