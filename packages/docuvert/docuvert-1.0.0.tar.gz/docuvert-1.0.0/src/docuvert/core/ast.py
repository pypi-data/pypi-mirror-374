
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime


class NodeType(Enum):
    """Enumeration of all supported AST node types."""
    # Document structure
    DOCUMENT = "document"
    SECTION = "section"
    CHAPTER = "chapter"
    
    # Text elements
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    TEXT = "text"
    LINE_BREAK = "line_break"
    PAGE_BREAK = "page_break"
    
    # Formatting
    BOLD = "bold"
    ITALIC = "italic"
    UNDERLINE = "underline"
    STRIKETHROUGH = "strikethrough"
    SUPERSCRIPT = "superscript"
    SUBSCRIPT = "subscript"
    CODE_INLINE = "code_inline"
    
    # Lists
    LIST_ORDERED = "list_ordered"
    LIST_UNORDERED = "list_unordered"
    LIST_ITEM = "list_item"
    
    # Tables
    TABLE = "table"
    TABLE_ROW = "table_row"
    TABLE_CELL = "table_cell"
    TABLE_HEADER = "table_header"
    
    # Media
    IMAGE = "image"
    LINK = "link"
    
    # Code
    CODE_BLOCK = "code_block"
    
    # Metadata
    METADATA = "metadata"
    
    # Special
    RAW = "raw"
    UNKNOWN = "unknown"


@dataclass
class DocumentMetadata:
    """Document metadata information."""
    title: Optional[str] = None
    author: Optional[str] = None
    created: Optional[datetime] = None
    modified: Optional[datetime] = None
    subject: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    language: Optional[str] = None
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    custom_properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StyleInfo:
    """Comprehensive styling information."""
    # Font properties
    font_family: Optional[str] = None
    font_size: Optional[Union[int, float]] = None
    font_weight: Optional[str] = None  # normal, bold, etc.
    font_style: Optional[str] = None   # normal, italic, etc.
    
    # Text properties
    color: Optional[str] = None
    background_color: Optional[str] = None
    text_align: Optional[str] = None   # left, center, right, justify
    text_decoration: Optional[str] = None
    line_height: Optional[Union[int, float]] = None
    
    # Spacing
    margin_top: Optional[Union[int, float]] = None
    margin_bottom: Optional[Union[int, float]] = None
    margin_left: Optional[Union[int, float]] = None
    margin_right: Optional[Union[int, float]] = None
    padding_top: Optional[Union[int, float]] = None
    padding_bottom: Optional[Union[int, float]] = None
    padding_left: Optional[Union[int, float]] = None
    padding_right: Optional[Union[int, float]] = None
    
    # Border
    border_width: Optional[Union[int, float]] = None
    border_style: Optional[str] = None
    border_color: Optional[str] = None
    
    # List properties
    list_style_type: Optional[str] = None
    
    # Table properties
    cell_span: Optional[int] = None
    row_span: Optional[int] = None
    
    # Custom properties
    custom: Dict[str, Any] = field(default_factory=dict)


class ASTNode:
    """
    Enhanced AST node with comprehensive document representation capabilities.
    
    This class represents a node in the Abstract Syntax Tree (AST) that serves
    as a universal document format, enabling conversion between any two formats
    while preserving structure, content, and formatting.
    """
    
    def __init__(
        self, 
        node_type: Union[NodeType, str],
        content: Optional[str] = None,
        children: Optional[List['ASTNode']] = None,
        styles: Optional[Union[StyleInfo, Dict[str, Any]]] = None,
        attributes: Optional[Dict[str, Any]] = None,
        metadata: Optional[DocumentMetadata] = None
    ):
        # Convert string types to NodeType enum
        if isinstance(node_type, str):
            try:
                self.type = NodeType(node_type)
            except ValueError:
                self.type = NodeType.UNKNOWN
        else:
            self.type = node_type
            
        self.content = content
        self.children = children or []
        
        # Handle styles - convert dict to StyleInfo if needed
        if isinstance(styles, dict):
            self.styles = StyleInfo(**{k: v for k, v in styles.items() if hasattr(StyleInfo, k)})
        else:
            self.styles = styles or StyleInfo()
            
        self.attributes = attributes or {}
        self.metadata = metadata
        
    def add_child(self, child: 'ASTNode') -> None:
        """Add a child node."""
        self.children.append(child)
        
    def find_children(self, node_type: NodeType) -> List['ASTNode']:
        """Find all direct children of a specific type."""
        return [child for child in self.children if child.type == node_type]
        
    def find_all(self, node_type: NodeType) -> List['ASTNode']:
        """Find all descendants of a specific type (recursive)."""
        results = []
        if self.type == node_type:
            results.append(self)
        for child in self.children:
            results.extend(child.find_all(node_type))
        return results
        
    def get_text_content(self) -> str:
        """Get all text content from this node and its children."""
        text_parts = []
        if self.content:
            text_parts.append(self.content)
        for child in self.children:
            text_parts.append(child.get_text_content())
        return ''.join(text_parts)
        
    def clone(self) -> 'ASTNode':
        """Create a deep copy of this node."""
        return ASTNode(
            node_type=self.type,
            content=self.content,
            children=[child.clone() for child in self.children],
            styles=self.styles,
            attributes=self.attributes.copy(),
            metadata=self.metadata
        )
        
    def __repr__(self) -> str:
        content_preview = self.content[:30] + "..." if self.content and len(self.content) > 30 else self.content
        return f"ASTNode(type={self.type.value}, content='{content_preview}', children={len(self.children)})"
        
    def __str__(self) -> str:
        return self.__repr__()


# Factory functions for common node types
def create_document(metadata: Optional[DocumentMetadata] = None) -> ASTNode:
    """Create a document root node."""
    return ASTNode(NodeType.DOCUMENT, metadata=metadata)

def create_paragraph(text: str, styles: Optional[StyleInfo] = None) -> ASTNode:
    """Create a paragraph node."""
    return ASTNode(NodeType.PARAGRAPH, content=text, styles=styles)

def create_heading(text: str, level: int = 1, styles: Optional[StyleInfo] = None) -> ASTNode:
    """Create a heading node."""
    return ASTNode(
        NodeType.HEADING, 
        content=text, 
        styles=styles, 
        attributes={'level': level}
    )

def create_table(rows: List[List[str]], has_header: bool = False) -> ASTNode:
    """Create a table node with rows and cells."""
    table = ASTNode(NodeType.TABLE)
    
    for i, row_data in enumerate(rows):
        row = ASTNode(NodeType.TABLE_ROW)
        
        for cell_data in row_data:
            cell_type = NodeType.TABLE_HEADER if has_header and i == 0 else NodeType.TABLE_CELL
            cell = ASTNode(cell_type, content=cell_data)
            row.add_child(cell)
            
        table.add_child(row)
        
    return table

def create_image(src: str, alt: Optional[str] = None, title: Optional[str] = None) -> ASTNode:
    """Create an image node."""
    attributes = {'src': src}
    if alt:
        attributes['alt'] = alt
    if title:
        attributes['title'] = title
    return ASTNode(NodeType.IMAGE, attributes=attributes)

def create_link(url: str, text: str, title: Optional[str] = None) -> ASTNode:
    """Create a link node."""
    attributes = {'href': url}
    if title:
        attributes['title'] = title
    return ASTNode(NodeType.LINK, content=text, attributes=attributes)
