"""
HTML to Markdown converter with comprehensive formatting support.
"""

import sys
import os
import re
from typing import Optional, List, Dict, Any

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.ast import ASTNode, NodeType, StyleInfo, DocumentMetadata, create_document, create_paragraph, create_heading
from core.exceptions import ConversionError, DependencyError

try:
    from bs4 import BeautifulSoup, Tag, NavigableString
    import html2text
except ImportError as e:
    raise DependencyError(
        "BeautifulSoup4 and html2text are required for HTML conversion",
        missing_dependency="beautifulsoup4 html2text"
    ) from e


class Html2MdConverter:
    """Converts HTML files to Markdown format."""
    
    def __init__(self):
        # Configure html2text processor
        self.html2text_processor = html2text.HTML2Text()
        self.html2text_processor.ignore_links = False
        self.html2text_processor.ignore_images = False
        self.html2text_processor.ignore_emphasis = False
        self.html2text_processor.body_width = 0  # Don't wrap lines
        self.html2text_processor.unicode_snob = True
        self.html2text_processor.mark_code = True
    
    def parse_html2ast(self, input_path: str) -> ASTNode:
        """Parse HTML file and convert to AST representation."""
        
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
        except UnicodeDecodeError:
            # Try different encodings
            for encoding in ['latin1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(input_path, 'r', encoding=encoding) as f:
                        html_content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ConversionError(f"Could not decode HTML file: {input_path}")
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract metadata
        metadata = self._extract_metadata(soup)
        
        # Create document root
        doc = create_document(metadata)
        
        # Find body content or use entire document
        body = soup.find('body')
        if body is None:
            body = soup
            
        # Convert body content to AST
        for element in body.children:
            if isinstance(element, Tag):
                ast_node = self._convert_element_to_ast(element)
                if ast_node:
                    doc.add_child(ast_node)
        
        return doc
    
    def ast2md(self, ast_root: ASTNode, output_path: str) -> None:
        """Convert AST to Markdown file."""
        from core.mapper import ast2md
        ast2md(ast_root, output_path)
    
    def convert(self, input_path: str, output_path: str) -> None:
        """Convert HTML to Markdown using both direct and AST approaches."""
        
        try:
            # Method 1: Direct conversion using html2text (fast)
            self._convert_direct(input_path, output_path)
            
        except Exception as direct_error:
            try:
                # Method 2: AST-based conversion (more accurate)
                ast_root = self.parse_html2ast(input_path)
                self.ast2md(ast_root, output_path)
                print(f"Successfully converted '{input_path}' to '{output_path}' (AST method)")
                
            except Exception as ast_error:
                raise ConversionError(
                    f"HTML to Markdown conversion failed. Direct: {direct_error}, AST: {ast_error}",
                    source_format="html",
                    target_format="md"
                )
    
    def _convert_direct(self, input_path: str, output_path: str) -> None:
        """Direct HTML to Markdown conversion using html2text."""
        
        with open(input_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Convert HTML to Markdown
        markdown_content = self.html2text_processor.handle(html_content)
        
        # Clean up the output
        markdown_content = self._clean_markdown(markdown_content)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
            
        print(f"Successfully converted '{input_path}' to '{output_path}' (direct method)")
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Optional[DocumentMetadata]:
        \"\"\"Extract document metadata from HTML.\"\"\"
        
        metadata = DocumentMetadata()
        
        # Title
        title_tag = soup.find('title')
        if title_tag:
            metadata.title = title_tag.get_text().strip()
            
        # Meta tags
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            name = meta.get('name', '').lower()
            content = meta.get('content', '')
            
            if name == 'author':
                metadata.author = content
            elif name == 'description':
                metadata.subject = content
            elif name == 'keywords':
                metadata.keywords = [k.strip() for k in content.split(',')]
            elif name == 'language' or name == 'lang':
                metadata.language = content
        
        # HTML lang attribute
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            metadata.language = html_tag.get('lang')
            
        return metadata if any([metadata.title, metadata.author, metadata.subject, metadata.keywords]) else None
    
    def _convert_element_to_ast(self, element: Tag) -> Optional[ASTNode]:
        \"\"\"Convert HTML element to AST node.\"\"\"
        
        tag_name = element.name.lower()
        
        # Headings
        if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(tag_name[1])
            text = self._get_text_content(element)
            return create_heading(text, level)
        
        # Paragraphs
        elif tag_name == 'p':
            text = self._get_text_content(element)
            para = create_paragraph(text)
            # Add inline formatting children
            self._process_inline_elements(para, element)
            return para
        
        # Lists
        elif tag_name in ['ul', 'ol']:
            list_type = NodeType.LIST_UNORDERED if tag_name == 'ul' else NodeType.LIST_ORDERED
            list_node = ASTNode(list_type)
            
            for li in element.find_all('li', recursive=False):
                item_text = self._get_text_content(li)
                list_item = ASTNode(NodeType.LIST_ITEM, content=item_text)
                list_node.add_child(list_item)
            
            return list_node
        
        # Tables
        elif tag_name == 'table':
            return self._convert_table_to_ast(element)
        
        # Code blocks
        elif tag_name == 'pre':
            code_element = element.find('code')
            if code_element:
                code_text = code_element.get_text()
            else:
                code_text = element.get_text()
            return ASTNode(NodeType.CODE_BLOCK, content=code_text)
        
        # Divisions and sections - process children
        elif tag_name in ['div', 'section', 'article', 'main', 'aside', 'nav', 'header', 'footer']:
            section = ASTNode(NodeType.SECTION)
            for child in element.children:
                if isinstance(child, Tag):
                    child_ast = self._convert_element_to_ast(child)
                    if child_ast:
                        section.add_child(child_ast)
            return section if section.children else None
        
        # Line breaks
        elif tag_name == 'br':
            return ASTNode(NodeType.LINE_BREAK)
        
        # Images
        elif tag_name == 'img':
            src = element.get('src', '')
            alt = element.get('alt', '')
            title = element.get('title', '')
            
            attributes = {'src': src}
            if alt:
                attributes['alt'] = alt
            if title:
                attributes['title'] = title
                
            return ASTNode(NodeType.IMAGE, attributes=attributes)
        
        # Links
        elif tag_name == 'a':
            href = element.get('href', '')
            text = self._get_text_content(element)
            title = element.get('title', '')
            
            attributes = {'href': href}
            if title:
                attributes['title'] = title
                
            return ASTNode(NodeType.LINK, content=text, attributes=attributes)
        
        # Other elements - try to extract text content
        else:
            text = self._get_text_content(element)
            if text.strip():
                return create_paragraph(text)
        
        return None
    
    def _convert_table_to_ast(self, table: Tag) -> ASTNode:
        \"\"\"Convert HTML table to AST table node.\"\"\"
        
        table_node = ASTNode(NodeType.TABLE)
        
        # Process table rows
        rows = table.find_all('tr')
        
        for row_index, tr in enumerate(rows):
            row_node = ASTNode(NodeType.TABLE_ROW)
            
            # Find cells (th or td)
            cells = tr.find_all(['th', 'td'])
            
            for cell in cells:
                # Determine cell type
                is_header = cell.name == 'th' or (row_index == 0 and table.find('thead'))
                cell_type = NodeType.TABLE_HEADER if is_header else NodeType.TABLE_CELL
                
                cell_text = self._get_text_content(cell)
                cell_node = ASTNode(cell_type, content=cell_text)
                
                # Handle colspan and rowspan
                if cell.get('colspan'):
                    cell_node.attributes['colspan'] = int(cell.get('colspan'))
                if cell.get('rowspan'):
                    cell_node.attributes['rowspan'] = int(cell.get('rowspan'))
                
                row_node.add_child(cell_node)
            
            table_node.add_child(row_node)
        
        return table_node
    
    def _process_inline_elements(self, parent_node: ASTNode, element: Tag) -> None:
        \"\"\"Process inline formatting elements within a parent node.\"\"\"
        
        for child in element.children:
            if isinstance(child, Tag):
                inline_node = self._convert_inline_element(child)
                if inline_node:
                    parent_node.add_child(inline_node)
            elif isinstance(child, NavigableString):
                text = str(child).strip()
                if text:
                    text_node = ASTNode(NodeType.TEXT, content=text)
                    parent_node.add_child(text_node)
    
    def _convert_inline_element(self, element: Tag) -> Optional[ASTNode]:
        \"\"\"Convert inline HTML elements to AST nodes.\"\"\"
        
        tag_name = element.name.lower()
        text = self._get_text_content(element)
        
        if not text.strip():
            return None
        
        # Bold/Strong
        if tag_name in ['b', 'strong']:
            return ASTNode(NodeType.BOLD, content=text)
        
        # Italic/Emphasis
        elif tag_name in ['i', 'em']:
            return ASTNode(NodeType.ITALIC, content=text)
        
        # Underline
        elif tag_name == 'u':
            return ASTNode(NodeType.UNDERLINE, content=text)
        
        # Strikethrough
        elif tag_name in ['s', 'del', 'strike']:
            return ASTNode(NodeType.STRIKETHROUGH, content=text)
        
        # Code
        elif tag_name == 'code':
            return ASTNode(NodeType.CODE_INLINE, content=text)
        
        # Superscript/Subscript
        elif tag_name == 'sup':
            return ASTNode(NodeType.SUPERSCRIPT, content=text)
        elif tag_name == 'sub':
            return ASTNode(NodeType.SUBSCRIPT, content=text)
        
        # Links
        elif tag_name == 'a':
            href = element.get('href', '')
            title = element.get('title', '')
            
            attributes = {'href': href}
            if title:
                attributes['title'] = title
                
            return ASTNode(NodeType.LINK, content=text, attributes=attributes)
        
        # Default to text
        else:
            return ASTNode(NodeType.TEXT, content=text)
    
    def _get_text_content(self, element: Tag) -> str:
        \"\"\"Get clean text content from HTML element.\"\"\"
        
        # Handle special cases
        if element.name in ['br']:
            return '\\n'
        
        # Get text content
        text = element.get_text(separator=' ', strip=True)
        
        # Clean up whitespace
        text = re.sub(r'\\s+', ' ', text)
        
        return text
    
    def _clean_markdown(self, content: str) -> str:
        \"\"\"Clean up markdown content from html2text conversion.\"\"\"
        
        # Remove excessive blank lines
        content = re.sub(r'\\n{3,}', '\\n\\n', content)
        
        # Clean up list formatting
        content = re.sub(r'^\\s*\\*\\s*\\*\\s*', '* ', content, flags=re.MULTILINE)
        
        # Clean up link formatting
        content = re.sub(r'\\[\\s*\\]\\(([^)]+)\\)', r'[\\1](\\1)', content)
        
        # Remove trailing whitespace
        content = '\\n'.join(line.rstrip() for line in content.split('\\n'))
        
        return content.strip() + '\\n'