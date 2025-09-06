
import sys
import os
import re
# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.ast import ASTNode

class Txt2TexConverter:
    """
    Converts a plain text file to a LaTeX file.
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
        Converts a plain text file to a LaTeX file with proper formatting.

        Args:
            input_path (str): The path to the input plain text file.
            output_path (str): The path to the output LaTeX file.
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            result = []
            i = 0
            in_enumerate = False
            in_itemize = False
            
            while i < len(lines):
                line = lines[i]
                
                # Skip empty lines but preserve spacing
                if not line.strip():
                    result.append('')
                    i += 1
                    continue
                
                # Check for headers (standalone short lines)
                if self._is_header(line, lines, i):
                    # Close any open lists
                    if in_enumerate:
                        result.append('\\end{enumerate}')
                        in_enumerate = False
                    if in_itemize:
                        result.append('\\end{itemize}')
                        in_itemize = False
                    
                    result.append(f"\\section{{{self._escape_latex(line.strip())}}}")
                    i += 1
                    continue
                    
                # Check for numbered lists
                if re.match(r'^\s*\d+\.\s+', line):
                    if not in_enumerate:
                        if in_itemize:
                            result.append('\\end{itemize}')
                            in_itemize = False
                        result.append('\\begin{enumerate}')
                        in_enumerate = True
                    
                    content = re.sub(r'^\s*\d+\.\s+', '', line)
                    result.append(f'\\item {self._escape_latex(content)}')
                    i += 1
                    continue
                
                # Check for bullet lists
                if re.match(r'^\s*[-*+]\s+', line):
                    if not in_itemize:
                        if in_enumerate:
                            result.append('\\end{enumerate}')
                            in_enumerate = False
                        result.append('\\begin{itemize}')
                        in_itemize = True
                    
                    content = re.sub(r'^\s*[-*+]\s+', '', line)
                    result.append(f'\\item {self._escape_latex(content)}')
                    i += 1
                    continue
                
                # Check for code blocks (multiple consecutive indented lines)
                if line.startswith('    ') or line.startswith('\t'):
                    # Close any open lists
                    if in_enumerate:
                        result.append('\\end{enumerate}')
                        in_enumerate = False
                    if in_itemize:
                        result.append('\\end{itemize}')
                        in_itemize = False
                    
                    code_block, next_i = self._process_code_block(lines, i)
                    result.extend(code_block)
                    i = next_i
                    continue
                
                # Regular paragraph - close lists first
                if in_enumerate:
                    result.append('\\end{enumerate}')
                    in_enumerate = False
                if in_itemize:
                    result.append('\\end{itemize}')
                    in_itemize = False
                
                result.append(self._escape_latex(line) + '\\\\')
                i += 1
            
            # Close any remaining open lists
            if in_enumerate:
                result.append('\\end{enumerate}')
            if in_itemize:
                result.append('\\end{itemize}')
            
            # Create complete LaTeX document
            latex_content = r'''\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{geometry}
\usepackage{fancyhdr}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage{verbatim}

\geometry{a4paper, margin=1in}

\begin{document}

''' + '\n'.join(result) + r'''

\end{document}
'''
            
            # Write result
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            
            print(f"Successfully converted '{input_path}' to '{output_path}'")
            
        except Exception as e:
            print(f"Error converting plain text to LaTeX: {e}")
    
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
        
        result.append('\\begin{verbatim}')
        result.extend(code_lines)
        result.append('\\end{verbatim}')
        
        return result, i
    
    def _escape_latex(self, text: str) -> str:
        """
        Escape special LaTeX characters in text.
        
        Args:
            text (str): The text to escape
            
        Returns:
            str: The escaped text
        """
        # LaTeX special characters that need escaping
        replacements = {
            '\\': '\\textbackslash{}',
            '{': '\\{',
            '}': '\\}',
            '$': '\\$',
            '&': '\\&',
            '%': '\\%',
            '#': '\\#',
            '^': '\\textasciicircum{}',
            '_': '\\_',
            '~': '\\textasciitilde{}',
        }
        
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        
        return text
