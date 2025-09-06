"""
HTML to DOCX converter with comprehensive formatting support.
"""

import sys
import os
import tempfile
from typing import Optional

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.ast import ASTNode, NodeType
from core.exceptions import ConversionError, DependencyError


class Html2DocxConverter:
    """Converts HTML files to DOCX format."""
    
    def parse_html2ast(self, input_path: str) -> ASTNode:
        """Parse HTML to AST representation."""
        from .html2md import Html2MdConverter
        html_converter = Html2MdConverter()
        return html_converter.parse_html2ast(input_path)
    
    def ast2docx(self, ast_root: ASTNode, output_path: str) -> None:
        """Convert AST to DOCX format."""
        from core.mapper import ast2docx
        ast2docx(ast_root, output_path)
    
    def convert(self, input_path: str, output_path: str) -> None:
        """Convert HTML to DOCX using AST-based conversion."""
        
        try:
            # Use AST-based conversion for best formatting preservation
            ast_root = self.parse_html2ast(input_path)
            self.ast2docx(ast_root, output_path)
            print(f"Successfully converted '{input_path}' to '{output_path}'")
            
        except Exception as ast_error:
            try:
                # Fallback: Convert via pandoc if available
                self._convert_with_pandoc(input_path, output_path)
                print(f"Successfully converted '{input_path}' to '{output_path}' (pandoc fallback)")
                
            except Exception as pandoc_error:
                raise ConversionError(
                    f"HTML to DOCX conversion failed. AST: {ast_error}, Pandoc: {pandoc_error}",
                    source_format="html",
                    target_format="docx",
                    suggestions=[
                        "Check that the HTML file is valid and well-formed",
                        "Install python-docx: pip install python-docx",
                        "Install pandoc as fallback: pip install pypandoc"
                    ]
                )
    
    def _convert_with_pandoc(self, input_path: str, output_path: str) -> None:
        """Fallback conversion using pandoc."""
        try:
            import pypandoc
        except ImportError as e:
            raise DependencyError(
                "pypandoc is required for pandoc fallback conversion",
                missing_dependency="pypandoc"
            ) from e
        
        pypandoc.convert_file(input_path, 'docx', outputfile=output_path)


class Html2TxtConverter:
    """Converts HTML files to plain text format."""
    
    def parse_html2ast(self, input_path: str) -> ASTNode:
        """Parse HTML to AST representation."""
        from .html2md import Html2MdConverter
        html_converter = Html2MdConverter()
        return html_converter.parse_html2ast(input_path)
    
    def ast2txt(self, ast_root: ASTNode, output_path: str) -> None:
        """Convert AST to plain text format."""
        from core.mapper import ast2txt
        ast2txt(ast_root, output_path)
    
    def convert(self, input_path: str, output_path: str) -> None:
        """Convert HTML to plain text."""
        
        try:
            # Method 1: AST-based conversion
            ast_root = self.parse_html2ast(input_path)
            self.ast2txt(ast_root, output_path)
            print(f"Successfully converted '{input_path}' to '{output_path}'")
            
        except Exception as ast_error:
            try:
                # Method 2: Direct BeautifulSoup conversion
                self._convert_direct(input_path, output_path)
                print(f"Successfully converted '{input_path}' to '{output_path}' (direct method)")
                
            except Exception as direct_error:
                raise ConversionError(
                    f"HTML to TXT conversion failed. AST: {ast_error}, Direct: {direct_error}",
                    source_format="html",
                    target_format="txt"
                )
    
    def _convert_direct(self, input_path: str, output_path: str) -> None:
        """Direct HTML to text conversion using BeautifulSoup."""
        try:
            from bs4 import BeautifulSoup
        except ImportError as e:
            raise DependencyError(
                "BeautifulSoup4 is required for HTML conversion",
                missing_dependency="beautifulsoup4"
            ) from e
        
        with open(input_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract text content
        text_content = soup.get_text(separator='\\n', strip=True)
        
        # Clean up excessive whitespace
        import re
        text_content = re.sub(r'\\n{3,}', '\\n\\n', text_content)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text_content)


class Html2TexConverter:
    """Converts HTML files to LaTeX format."""
    
    def parse_html2ast(self, input_path: str) -> ASTNode:
        """Parse HTML to AST representation."""
        from .html2md import Html2MdConverter
        html_converter = Html2MdConverter()
        return html_converter.parse_html2ast(input_path)
    
    def ast2tex(self, ast_root: ASTNode, output_path: str) -> None:
        """Convert AST to LaTeX format."""
        from core.mapper import ast2tex
        ast2tex(ast_root, output_path)
    
    def convert(self, input_path: str, output_path: str) -> None:
        """Convert HTML to LaTeX."""
        
        try:
            # AST-based conversion
            ast_root = self.parse_html2ast(input_path)
            self.ast2tex(ast_root, output_path)
            print(f"Successfully converted '{input_path}' to '{output_path}'")
            
        except Exception as e:
            raise ConversionError(
                f"HTML to LaTeX conversion failed: {e}",
                source_format="html",
                target_format="tex",
                suggestions=[
                    "Check that the HTML file is valid",
                    "Install required dependencies for AST conversion"
                ]
            )


class Html2CsvConverter:
    """Converts HTML tables to CSV format."""
    
    def parse_html2ast(self, input_path: str) -> ASTNode:
        """Parse HTML to AST representation."""
        from .html2md import Html2MdConverter
        html_converter = Html2MdConverter()
        return html_converter.parse_html2ast(input_path)
    
    def ast2csv(self, ast_root: ASTNode, output_path: str) -> None:
        """Convert AST tables to CSV format."""
        import csv
        
        # Find all tables in the AST
        tables = ast_root.find_all(NodeType.TABLE)
        
        if not tables:
            raise ConversionError(
                "No tables found in HTML document",
                suggestions=["Ensure the HTML contains <table> elements"]
            )
        
        # Use the first table (or could process all tables)
        table = tables[0]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            for row in table.find_children(NodeType.TABLE_ROW):
                row_data = []
                for cell in row.children:
                    if cell.type in [NodeType.TABLE_CELL, NodeType.TABLE_HEADER]:
                        row_data.append(cell.content or '')
                writer.writerow(row_data)
    
    def convert(self, input_path: str, output_path: str) -> None:
        """Convert HTML tables to CSV."""
        
        try:
            # AST-based conversion
            ast_root = self.parse_html2ast(input_path)
            self.ast2csv(ast_root, output_path)
            print(f"Successfully converted '{input_path}' to '{output_path}'")
            
        except Exception as ast_error:
            try:
                # Fallback: Direct pandas conversion
                self._convert_with_pandas(input_path, output_path)
                print(f"Successfully converted '{input_path}' to '{output_path}' (pandas method)")
                
            except Exception as pandas_error:
                raise ConversionError(
                    f"HTML to CSV conversion failed. AST: {ast_error}, Pandas: {pandas_error}",
                    source_format="html",
                    target_format="csv",
                    suggestions=["Ensure the HTML contains valid table elements"]
                )
    
    def _convert_with_pandas(self, input_path: str, output_path: str) -> None:
        """Convert HTML tables to CSV using pandas."""
        try:
            import pandas as pd
        except ImportError as e:
            raise DependencyError(
                "pandas is required for HTML table conversion",
                missing_dependency="pandas"
            ) from e
        
        # Read HTML tables
        tables = pd.read_html(input_path)
        
        if not tables:
            raise ConversionError("No tables found in HTML document")
        
        # Save first table as CSV
        tables[0].to_csv(output_path, index=False)


class Html2XlsxConverter:
    """Converts HTML tables to Excel format."""
    
    def parse_html2ast(self, input_path: str) -> ASTNode:
        """Parse HTML to AST representation."""
        from .html2md import Html2MdConverter
        html_converter = Html2MdConverter()
        return html_converter.parse_html2ast(input_path)
    
    def ast2xlsx(self, ast_root: ASTNode, output_path: str) -> None:
        """Convert AST tables to Excel format."""
        try:
            import pandas as pd
        except ImportError as e:
            raise DependencyError(
                "pandas and openpyxl are required for Excel conversion",
                missing_dependency="pandas openpyxl"
            ) from e
        
        # Find all tables in the AST
        tables = ast_root.find_all(NodeType.TABLE)
        
        if not tables:
            raise ConversionError(
                "No tables found in HTML document",
                suggestions=["Ensure the HTML contains <table> elements"]
            )
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for table_idx, table in enumerate(tables):
                # Convert table to list of lists
                table_data = []
                
                for row in table.find_children(NodeType.TABLE_ROW):
                    row_data = []
                    for cell in row.children:
                        if cell.type in [NodeType.TABLE_CELL, NodeType.TABLE_HEADER]:
                            row_data.append(cell.content or '')
                    if row_data:  # Only add non-empty rows
                        table_data.append(row_data)
                
                if table_data:
                    # Create DataFrame
                    df = pd.DataFrame(table_data[1:], columns=table_data[0] if table_data else None)
                    
                    # Write to Excel sheet
                    sheet_name = f'Table_{table_idx + 1}' if len(tables) > 1 else 'Sheet1'
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    def convert(self, input_path: str, output_path: str) -> None:
        """Convert HTML tables to Excel."""
        
        try:
            # AST-based conversion
            ast_root = self.parse_html2ast(input_path)
            self.ast2xlsx(ast_root, output_path)
            print(f"Successfully converted '{input_path}' to '{output_path}'")
            
        except Exception as ast_error:
            try:
                # Fallback: Direct pandas conversion
                self._convert_with_pandas(input_path, output_path)
                print(f"Successfully converted '{input_path}' to '{output_path}' (pandas method)")
                
            except Exception as pandas_error:
                raise ConversionError(
                    f"HTML to Excel conversion failed. AST: {ast_error}, Pandas: {pandas_error}",
                    source_format="html",
                    target_format="xlsx"
                )
    
    def _convert_with_pandas(self, input_path: str, output_path: str) -> None:
        """Convert HTML tables to Excel using pandas."""
        try:
            import pandas as pd
        except ImportError as e:
            raise DependencyError(
                "pandas is required for HTML table conversion",
                missing_dependency="pandas openpyxl"
            ) from e
        
        # Read HTML tables
        tables = pd.read_html(input_path)
        
        if not tables:
            raise ConversionError("No tables found in HTML document")
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for idx, table in enumerate(tables):
                sheet_name = f'Table_{idx + 1}' if len(tables) > 1 else 'Sheet1'
                table.to_excel(writer, sheet_name=sheet_name, index=False)