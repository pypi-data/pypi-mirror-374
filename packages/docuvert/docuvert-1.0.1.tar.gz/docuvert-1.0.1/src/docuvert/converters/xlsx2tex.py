
import sys
import os
# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.ast import ASTNode
import pandas as pd
from tabulate import tabulate

class Xlsx2TexConverter:
    """
    Converts an XLSX file to a LaTeX file.
    """
    def parse_xlsx2ast(self, input_path: str) -> ASTNode:
        """
        Parses an XLSX file and converts it to an AST.

        Args:
            input_path (str): The path to the input XLSX file.

        Returns:
            ASTNode: The root of the generated AST.
        """
        # TODO: Implement the logic to parse the XLSX and build an AST.
        print(f"Parsing XLSX at {input_path} and converting to AST.")
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
        Converts an XLSX file to a LaTeX file with proper table formatting.
        
        Converts the first sheet of the XLSX file to a LaTeX table
        within a complete LaTeX document structure.

        Args:
            input_path (str): The path to the input XLSX file.
            output_path (str): The path to the output LaTeX file.
        """
        try:
            # Read the first sheet of the Excel file
            df = pd.read_excel(input_path, sheet_name=0)
            
            # Create LaTeX table using pandas to_latex method
            latex_table = df.to_latex(index=False, escape=True, 
                                     column_format='|' + 'c|' * len(df.columns))
            
            # Create complete LaTeX document
            latex_content = r'''\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{geometry}
\usepackage{longtable}
\usepackage{array}
\usepackage{booktabs}

\geometry{a4paper, margin=1in}

\begin{document}

\title{Excel Data Table}
\maketitle

''' + latex_table + r'''

\end{document}
'''
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(latex_content)
                
            print(f"Successfully converted '{input_path}' to '{output_path}'")
        except Exception as e:
            print(f"Error converting XLSX to LaTeX: {e}")
