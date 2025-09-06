"""
ODT (OpenDocument Text) to various format converters.
"""

import sys
import os
import zipfile
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.ast import ASTNode, NodeType, StyleInfo, DocumentMetadata, create_document, create_paragraph, create_heading
from core.exceptions import ConversionError, DependencyError


class Odt2MdConverter:
    """Converts ODT files to Markdown format."""

    def __init__(self):
        # ODT XML namespaces
        self.namespaces = {
            'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
            'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
            'style': 'urn:oasis:names:tc:opendocument:xmlns:style:1.0',
            'fo': 'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0',
            'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0'
        }

    def parse_odt2ast(self, input_path: str) -> ASTNode:
        """Parse ODT file and convert to AST representation."""
        
        try:
            # Method 1: Parse ODT XML directly
            return self._parse_odt_xml(input_path)
        except Exception as xml_error:
            try:
                # Method 2: Use odfpy library if available
                return self._parse_with_odfpy(input_path)
            except Exception as odfpy_error:
                raise ConversionError(
                    f"ODT parsing failed. XML: {xml_error}, odfpy: {odfpy_error}",
                    source_format="odt",
                    suggestions=[
                        "Install odfpy: pip install odfpy",
                        "Check that the ODT file is valid and not corrupted"
                    ]
                )

    def _parse_odt_xml(self, input_path: str) -> ASTNode:
        """Parse ODT by extracting and parsing XML content."""
        
        if not zipfile.is_zipfile(input_path):
            raise ConversionError("Invalid ODT file: not a valid ZIP archive")

        doc = create_document()
        
        with zipfile.ZipFile(input_path, 'r') as odt_zip:
            # Extract content.xml
            if 'content.xml' not in odt_zip.namelist():
                raise ConversionError("Invalid ODT file: missing content.xml")
            
            content_xml = odt_zip.read('content.xml').decode('utf-8')
            
            # Parse XML
            root = ET.fromstring(content_xml)
            
            # Find document body
            body = root.find('.//office:body/office:text', self.namespaces)
            if body is None:
                raise ConversionError("Invalid ODT file: no document body found")
            
            # Process document elements
            self._process_odt_elements(body, doc)
            
            # Extract metadata if available
            try:
                meta_xml = odt_zip.read('meta.xml').decode('utf-8')
                metadata = self._extract_odt_metadata(meta_xml)
                doc.metadata = metadata
            except:
                pass  # Metadata is optional
        
        return doc

    def _process_odt_elements(self, parent_element, ast_parent: ASTNode):
        """Process ODT XML elements and convert to AST nodes."""
        
        for element in parent_element:
            tag_name = element.tag.split('}')[-1] if '}' in element.tag else element.tag
            
            # Paragraphs
            if tag_name == 'p':
                text_content = self._extract_text_from_element(element)
                if text_content.strip():
                    # Check if it's a heading based on style
                    style_name = element.get('text:style-name', '')
                    if 'heading' in style_name.lower() or element.get('text:outline-level'):
                        level = int(element.get('text:outline-level', '1'))
                        ast_parent.add_child(create_heading(text_content, level))
                    else:
                        ast_parent.add_child(create_paragraph(text_content))
            
            # Headings
            elif tag_name == 'h':
                text_content = self._extract_text_from_element(element)
                level = int(element.get('text:outline-level', '1'))
                ast_parent.add_child(create_heading(text_content, level))
            
            # Lists
            elif tag_name == 'list':
                list_node = self._process_odt_list(element)
                if list_node:
                    ast_parent.add_child(list_node)
            
            # Tables
            elif tag_name == 'table':
                table_node = self._process_odt_table(element)
                if table_node:
                    ast_parent.add_child(table_node)
            
            # Sections - process children
            elif tag_name in ['section']:
                self._process_odt_elements(element, ast_parent)
            
            # Continue processing child elements
            else:
                self._process_odt_elements(element, ast_parent)

    def _process_odt_list(self, list_element) -> Optional[ASTNode]:
        """Process ODT list element."""
        
        # Determine list type (ODT doesn't clearly distinguish)
        # Check for numbering in the first item
        first_item = list_element.find('.//text:list-item', self.namespaces)
        is_ordered = False
        
        if first_item is not None:
            # Simple heuristic: if we find numbers, assume ordered
            item_text = self._extract_text_from_element(first_item)
            is_ordered = bool(re.search(r'^\s*\d+', item_text))
        
        list_type = NodeType.LIST_ORDERED if is_ordered else NodeType.LIST_UNORDERED
        list_node = ASTNode(list_type)
        
        # Process list items
        for item in list_element.findall('.//text:list-item', self.namespaces):
            item_text = self._extract_text_from_element(item)
            if item_text.strip():
                list_item = ASTNode(NodeType.LIST_ITEM, content=item_text)
                list_node.add_child(list_item)
        
        return list_node if list_node.children else None

    def _process_odt_table(self, table_element) -> Optional[ASTNode]:
        """Process ODT table element."""
        
        table_node = ASTNode(NodeType.TABLE)
        
        # Process table rows
        for row in table_element.findall('.//table:table-row', self.namespaces):
            row_node = ASTNode(NodeType.TABLE_ROW)
            
            # Process table cells
            for cell in row.findall('.//table:table-cell', self.namespaces):
                cell_text = self._extract_text_from_element(cell)
                cell_node = ASTNode(NodeType.TABLE_CELL, content=cell_text)
                row_node.add_child(cell_node)
            
            if row_node.children:
                table_node.add_child(row_node)
        
        return table_node if table_node.children else None

    def _extract_text_from_element(self, element) -> str:
        """Extract all text content from an XML element."""
        
        text_parts = []
        
        # Add element's own text
        if element.text:
            text_parts.append(element.text)
        
        # Process child elements
        for child in element:
            child_text = self._extract_text_from_element(child)
            if child_text:
                text_parts.append(child_text)
            
            # Add tail text
            if child.tail:
                text_parts.append(child.tail)
        
        return ' '.join(text_parts)

    def _extract_odt_metadata(self, meta_xml: str) -> Optional[DocumentMetadata]:
        """Extract metadata from ODT meta.xml."""
        
        try:
            root = ET.fromstring(meta_xml)
            metadata = DocumentMetadata()
            
            # Title
            title_elem = root.find('.//dc:title', {'dc': 'http://purl.org/dc/elements/1.1/'})
            if title_elem is not None and title_elem.text:
                metadata.title = title_elem.text
            
            # Author
            creator_elem = root.find('.//dc:creator', {'dc': 'http://purl.org/dc/elements/1.1/'})
            if creator_elem is not None and creator_elem.text:
                metadata.author = creator_elem.text
            
            # Subject
            subject_elem = root.find('.//dc:subject', {'dc': 'http://purl.org/dc/elements/1.1/'})
            if subject_elem is not None and subject_elem.text:
                metadata.subject = subject_elem.text
            
            return metadata
            
        except Exception:
            return None

    def _parse_with_odfpy(self, input_path: str) -> ASTNode:
        """Parse ODT using odfpy library."""
        
        try:
            from odf.opendocument import load
            from odf.text import P, H, List, ListItem
            from odf.table import Table, TableRow, TableCell
        except ImportError as e:
            raise DependencyError(
                "odfpy library is required for ODT parsing",
                missing_dependency="odfpy"
            ) from e

        odt_doc = load(input_path)
        doc = create_document()
        
        # Extract metadata
        meta = odt_doc.meta
        if meta:
            metadata = DocumentMetadata()
            if hasattr(meta, 'title') and meta.title:
                metadata.title = str(meta.title)
            if hasattr(meta, 'creator') and meta.creator:
                metadata.author = str(meta.creator)
            doc.metadata = metadata
        
        # Process document content
        for element in odt_doc.text.childNodes:
            if element.tagName == 'text:p':
                text = self._get_odfpy_text(element)
                if text.strip():
                    doc.add_child(create_paragraph(text))
            
            elif element.tagName == 'text:h':
                text = self._get_odfpy_text(element)
                level = int(element.getAttribute('text:outline-level') or '1')
                doc.add_child(create_heading(text, level))
        
        return doc

    def _get_odfpy_text(self, element) -> str:
        """Extract text content from odfpy element."""
        text_parts = []
        
        def extract_text(node):
            if hasattr(node, 'data'):
                text_parts.append(node.data)
            if hasattr(node, 'childNodes'):
                for child in node.childNodes:
                    extract_text(child)
        
        extract_text(element)
        return ' '.join(text_parts)

    def ast2md(self, ast_root: ASTNode, output_path: str) -> None:
        """Convert AST to Markdown format."""
        from core.mapper import ast2md
        ast2md(ast_root, output_path)

    def convert(self, input_path: str, output_path: str) -> None:
        """Convert ODT to Markdown."""
        
        try:
            # AST-based conversion
            ast_root = self.parse_odt2ast(input_path)
            self.ast2md(ast_root, output_path)
            print(f"Successfully converted '{input_path}' to '{output_path}'")
            
        except Exception as e:
            raise ConversionError(
                f"ODT to Markdown conversion failed: {e}",
                source_format="odt",
                target_format="md"
            )


class Odt2DocxConverter:
    """Converts ODT files to DOCX format."""

    def parse_odt2ast(self, input_path: str) -> ASTNode:
        """Parse ODT file and convert to AST representation."""
        odt_converter = Odt2MdConverter()
        return odt_converter.parse_odt2ast(input_path)

    def ast2docx(self, ast_root: ASTNode, output_path: str) -> None:
        """Convert AST to DOCX format."""
        from core.mapper import ast2docx
        ast2docx(ast_root, output_path)

    def convert(self, input_path: str, output_path: str) -> None:
        """Convert ODT to DOCX."""
        
        try:
            # Method 1: AST-based conversion
            ast_root = self.parse_odt2ast(input_path)
            self.ast2docx(ast_root, output_path)
            print(f"Successfully converted '{input_path}' to '{output_path}' (AST method)")
            
        except Exception as ast_error:
            try:
                # Method 2: Pandoc fallback
                self._convert_with_pandoc(input_path, output_path)
                print(f"Successfully converted '{input_path}' to '{output_path}' (pandoc fallback)")
                
            except Exception as pandoc_error:
                raise ConversionError(
                    f"ODT to DOCX conversion failed. AST: {ast_error}, Pandoc: {pandoc_error}",
                    source_format="odt",
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


class Odt2PdfConverter:
    """Converts ODT files to PDF format."""

    def parse_odt2ast(self, input_path: str) -> ASTNode:
        """Parse ODT file and convert to AST representation."""
        odt_converter = Odt2MdConverter()
        return odt_converter.parse_odt2ast(input_path)

    def ast2pdf(self, ast_root: ASTNode, output_path: str) -> None:
        """Convert AST to PDF via HTML intermediate."""
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as temp_html:
            from core.mapper import ast2html
            ast2html(ast_root, temp_html.name)
            
            try:
                from .html2pdf import Html2PdfConverter
                pdf_converter = Html2PdfConverter()
                pdf_converter.convert(temp_html.name, output_path)
            finally:
                os.unlink(temp_html.name)

    def convert(self, input_path: str, output_path: str) -> None:
        """Convert ODT to PDF."""
        
        try:
            # Method 1: AST-based conversion via HTML
            ast_root = self.parse_odt2ast(input_path)
            self.ast2pdf(ast_root, output_path)
            print(f"Successfully converted '{input_path}' to '{output_path}' (AST method)")
            
        except Exception as ast_error:
            try:
                # Method 2: LibreOffice headless conversion
                self._convert_with_libreoffice(input_path, output_path)
                print(f"Successfully converted '{input_path}' to '{output_path}' (LibreOffice)")
                
            except Exception as lo_error:
                raise ConversionError(
                    f"ODT to PDF conversion failed. AST: {ast_error}, LibreOffice: {lo_error}",
                    source_format="odt",
                    target_format="pdf",
                    suggestions=[
                        "Install LibreOffice for native ODT support",
                        "Install HTML to PDF dependencies for fallback conversion"
                    ]
                )

    def _convert_with_libreoffice(self, input_path: str, output_path: str) -> None:
        """Convert using LibreOffice headless mode."""
        import subprocess
        import shutil
        
        if not shutil.which("libreoffice"):
            raise ConversionError("LibreOffice not found in PATH")
        
        # Get output directory
        output_dir = os.path.dirname(os.path.abspath(output_path))
        
        # Run LibreOffice conversion
        result = subprocess.run([
            "libreoffice", "--headless", "--convert-to", "pdf",
            "--outdir", output_dir, input_path
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            raise ConversionError(f"LibreOffice conversion failed: {result.stderr}")
        
        # LibreOffice creates file with same name but .pdf extension
        input_name = os.path.splitext(os.path.basename(input_path))[0]
        generated_pdf = os.path.join(output_dir, f"{input_name}.pdf")
        
        # Rename to desired output name if different
        if generated_pdf != output_path and os.path.exists(generated_pdf):
            os.rename(generated_pdf, output_path)


# Reverse converters (other formats to ODT)

class Md2OdtConverter:
    """Converts Markdown files to ODT format."""

    def parse_md2ast(self, input_path: str) -> ASTNode:
        """Parse Markdown to AST representation."""
        from .md2html import Md2HtmlConverter
        md_converter = Md2HtmlConverter()
        return md_converter.parse_md2ast(input_path)

    def ast2odt(self, ast_root: ASTNode, output_path: str) -> None:
        """Convert AST to ODT format (requires external tool)."""
        # ODT creation from AST is complex - use pandoc as intermediate
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as temp_md:
            from core.mapper import ast2md
            ast2md(ast_root, temp_md.name)
            
            try:
                self._convert_with_pandoc(temp_md.name, output_path)
            finally:
                os.unlink(temp_md.name)

    def convert(self, input_path: str, output_path: str) -> None:
        """Convert Markdown to ODT."""
        
        try:
            # Method 1: Direct pandoc conversion
            self._convert_with_pandoc(input_path, output_path)
            print(f"Successfully converted '{input_path}' to '{output_path}' (pandoc)")
            
        except Exception as pandoc_error:
            try:
                # Method 2: AST-based conversion
                ast_root = self.parse_md2ast(input_path)
                self.ast2odt(ast_root, output_path)
                print(f"Successfully converted '{input_path}' to '{output_path}' (AST method)")
                
            except Exception as ast_error:
                raise ConversionError(
                    f"Markdown to ODT conversion failed. Pandoc: {pandoc_error}, AST: {ast_error}",
                    source_format="md",
                    target_format="odt"
                )

    def _convert_with_pandoc(self, input_path: str, output_path: str) -> None:
        """Convert using pandoc."""
        try:
            import pypandoc
            pypandoc.convert_file(input_path, 'odt', outputfile=output_path)
        except ImportError as e:
            raise DependencyError(
                "pypandoc is required for ODT conversion",
                missing_dependency="pypandoc"
            ) from e


class Docx2OdtConverter:
    """Converts DOCX files to ODT format."""

    def parse_docx2ast(self, input_path: str) -> ASTNode:
        """Parse DOCX to AST representation."""
        from .md2html import Docx2HtmlConverter
        docx_converter = Docx2HtmlConverter()
        return docx_converter.parse_docx2ast(input_path)

    def convert(self, input_path: str, output_path: str) -> None:
        """Convert DOCX to ODT."""
        
        try:
            # Method 1: Pandoc conversion
            self._convert_with_pandoc(input_path, output_path)
            print(f"Successfully converted '{input_path}' to '{output_path}' (pandoc)")
            
        except Exception as pandoc_error:
            try:
                # Method 2: LibreOffice conversion
                self._convert_with_libreoffice(input_path, output_path)
                print(f"Successfully converted '{input_path}' to '{output_path}' (LibreOffice)")
                
            except Exception as lo_error:
                raise ConversionError(
                    f"DOCX to ODT conversion failed. Pandoc: {pandoc_error}, LibreOffice: {lo_error}",
                    source_format="docx",
                    target_format="odt"
                )

    def _convert_with_pandoc(self, input_path: str, output_path: str) -> None:
        """Convert using pandoc."""
        try:
            import pypandoc
            pypandoc.convert_file(input_path, 'odt', outputfile=output_path)
        except ImportError as e:
            raise DependencyError(
                "pypandoc is required for pandoc conversion",
                missing_dependency="pypandoc"
            ) from e

    def _convert_with_libreoffice(self, input_path: str, output_path: str) -> None:
        """Convert using LibreOffice."""
        import subprocess
        import shutil
        
        if not shutil.which("libreoffice"):
            raise ConversionError("LibreOffice not found in PATH")
        
        output_dir = os.path.dirname(os.path.abspath(output_path))
        
        result = subprocess.run([
            "libreoffice", "--headless", "--convert-to", "odt",
            "--outdir", output_dir, input_path
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            raise ConversionError(f"LibreOffice conversion failed: {result.stderr}")
        
        # Rename generated file if needed
        input_name = os.path.splitext(os.path.basename(input_path))[0]
        generated_odt = os.path.join(output_dir, f"{input_name}.odt")
        
        if generated_odt != output_path and os.path.exists(generated_odt):
            os.rename(generated_odt, output_path)