
import sys
import os
import re
# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from core.ast import ASTNode

class Txt2MdConverter:
    """
    Converts a plain text file to a Markdown file.
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

    def ast2md(self, ast_root: ASTNode, output_path: str):
        """
        Converts an AST to a Markdown file.

        Args:
            ast_root (ASTNode): The root of the AST.
            output_path (str): The path to the output Markdown file.
        """
        # TODO: Implement the logic to convert the AST to a Markdown document.
        print(f"Converting AST to Markdown at {output_path}")

    def convert(self, input_path: str, output_path: str):
        """
        Converts a plain text file to a Markdown file using smart formatting.

        Args:
            input_path (str): The path to the input plain text file.
            output_path (str): The path to the output Markdown file.
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            result = []
            i = 0
            
            while i < len(lines):
                line = lines[i]
                
                # Skip empty lines but preserve spacing
                if not line.strip():
                    result.append('')
                    i += 1
                    continue
                
                # Check for headers (standalone short lines)
                if self._is_header(line, lines, i):
                    result.append(f"# {line.strip()}")
                    i += 1
                    continue
                    
                # Check for numbered lists
                if re.match(r'^\s*\d+\.\s+', line):
                    list_item, next_i = self._process_numbered_list_item(lines, i)
                    result.extend(list_item)
                    i = next_i
                    continue
                
                # Check for bullet lists
                if re.match(r'^\s*[-*+]\s+', line):
                    result.append(line)
                    i += 1
                    continue
                
                # Check for code blocks (multiple consecutive indented lines)
                if line.startswith('    ') or line.startswith('\t'):
                    code_block, next_i = self._process_code_block(lines, i)
                    result.extend(code_block)
                    i = next_i
                    continue
                
                # Regular paragraph
                result.append(line)
                i += 1
            
            # Write result
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(result))
            
            print(f"Successfully converted '{input_path}' to '{output_path}'")
            
        except Exception as e:
            print(f"Error converting plain text to Markdown: {e}")
    
    def _is_header(self, line, lines, index):
        """Check if a line should be treated as a header."""
        stripped = line.strip()
        if not stripped or len(stripped) > 60:
            return False
            
        # Must be preceded and followed by empty lines (or start/end of file)
        prev_empty = index == 0 or not lines[index - 1].strip()
        next_empty = index + 1 >= len(lines) or not lines[index + 1].strip()
        
        if not (prev_empty and next_empty):
            return False
        
        # Don't treat command examples, file paths, or bullet points as headers
        if (stripped[0].isdigit() or 
            stripped.startswith(('-', '*', '+', './', 'docuvert')) or
            stripped.endswith(('.', ',', ':')) or
            '/' in stripped or
            '<' in stripped and '>' in stripped):  # Command syntax
            return False
        
        # Only treat clear section names as headers
        header_words = ['docuvert', 'installation', 'usage', 'examples', 'supported', 'conversions']
        return any(word in stripped.lower() for word in header_words) and len(stripped.split()) <= 4
    
    def _process_numbered_list_item(self, lines, start_index):
        """Process a numbered list item and its indented content."""
        result = []
        i = start_index
        
        # Add the list item itself
        result.append(lines[i])
        i += 1
        
        # Process any indented content that follows
        while i < len(lines):
            line = lines[i]
            
            # Empty line - include it and continue
            if not line.strip():
                result.append('')
                i += 1
                continue
            
            # Indented content belongs to the list item
            if line.startswith('    ') or line.startswith('\t'):
                # Check if this looks like code
                clean_line = line[4:] if line.startswith('    ') else line[1:]
                if self._looks_like_code(clean_line):
                    # Collect code block
                    code_lines = []
                    while i < len(lines) and (lines[i].startswith('    ') or lines[i].startswith('\t')):
                        code_line = lines[i]
                        clean = code_line[4:] if code_line.startswith('    ') else code_line[1:]
                        code_lines.append(clean)
                        i += 1
                    
                    result.append('')
                    result.append('    ```')
                    result.extend([f'    {line}' for line in code_lines])
                    result.append('    ```')
                    result.append('')
                else:
                    # Regular indented text
                    result.append(f'    {clean_line}')
                    i += 1
            else:
                # Not indented, we're done with this list item
                break
        
        return result, i
    
    def _process_code_block(self, lines, start_index):
        """Process a standalone code block."""
        result = []
        code_lines = []
        i = start_index
        
        # Collect all consecutive indented lines
        while i < len(lines) and (lines[i].startswith('    ') or lines[i].startswith('\t') or not lines[i].strip()):
            if lines[i].strip():  # Skip empty lines in code blocks
                clean = lines[i][4:] if lines[i].startswith('    ') else lines[i][1:]
                code_lines.append(clean)
            i += 1
        
        result.append('```')
        result.extend(code_lines)
        result.append('```')
        
        return result, i
    
    def _looks_like_code(self, line):
        """Determine if a line looks like code."""
        line = line.strip()
        if not line:
            return False
        
        # Command-like patterns
        code_indicators = [
            line.startswith('./'),
            line.startswith('git '),
            line.startswith('cd '),
            line.startswith('docuvert '),
            line.startswith('uv '),
            line.startswith('pip '),
            '/' in line and not line.endswith('/'),  # File paths but not directories
            line.count('.') >= 2,  # Filenames with extensions
            line.startswith('http'),  # URLs
        ]
        
        return any(code_indicators)
