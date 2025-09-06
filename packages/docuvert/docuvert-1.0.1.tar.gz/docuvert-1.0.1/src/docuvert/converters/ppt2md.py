"""
PPT (Legacy PowerPoint) to Markdown converter.
Handles old .ppt format by converting to .pptx first, then using enhanced Obsidian converter.
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import Optional
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.exceptions import ConversionError, DependencyError


class Ppt2MdConverter:
    """Converts PPT files to Markdown format with Obsidian optimization."""

    def __init__(self):
        """Initialize the converter."""
        self.temp_files = []

    def convert(self, input_path: str, output_path: str) -> None:
        """Convert PPT to Markdown via PPTX intermediate."""
        
        try:
            # First convert PPT to PPTX
            pptx_path = self._convert_ppt_to_pptx(input_path)
            
            # Then use the enhanced PPTX to Markdown converter
            from .pptx2md_obsidian import Pptx2MdObsidianConverter
            
            obsidian_converter = Pptx2MdObsidianConverter()
            obsidian_converter.convert(pptx_path, output_path)
            
            # Clean up temporary file if we created one
            if pptx_path != input_path and pptx_path in self.temp_files:
                try:
                    os.unlink(pptx_path)
                    self.temp_files.remove(pptx_path)
                except:
                    pass  # Best effort cleanup
                    
        except Exception as e:
            raise ConversionError(
                f"PPT to Markdown conversion failed: {e}",
                source_format="ppt",
                target_format="md",
                suggestions=[
                    "Install LibreOffice for PPT to PPTX conversion: brew install libreoffice",
                    "Alternatively, manually save the PPT file as PPTX format",
                    "Ensure python-pptx is installed: pip install python-pptx",
                    "Check that the PPT file is valid and not corrupted"
                ]
            )

    def _convert_ppt_to_pptx(self, input_path: str) -> str:
        """Convert PPT to PPTX using LibreOffice or other methods."""
        
        # First check if the file is actually already PPTX
        if input_path.lower().endswith('.pptx'):
            return input_path
        
        # Method 1: Try LibreOffice conversion
        pptx_path = self._try_libreoffice_conversion(input_path)
        if pptx_path:
            return pptx_path
        
        # Method 2: Try looking for existing PPTX version
        pptx_candidate = input_path + 'x'
        if os.path.exists(pptx_candidate):
            print(f"Found existing PPTX file: {pptx_candidate}")
            return pptx_candidate
            
        # Method 3: Create PPTX name and hope it exists
        base_path = Path(input_path)
        pptx_candidate2 = base_path.with_suffix('.pptx')
        if pptx_candidate2.exists():
            print(f"Found existing PPTX file: {pptx_candidate2}")
            return str(pptx_candidate2)
        
        # If we get here, we couldn't convert
        raise ConversionError(
            f"Cannot convert PPT to PPTX. LibreOffice not available and no existing PPTX found.",
            source_format="ppt",
            target_format="pptx",
            suggestions=[
                "Install LibreOffice: brew install libreoffice (macOS) or apt install libreoffice (Linux)",
                "Manually convert the PPT file to PPTX using Microsoft PowerPoint",
                "Use an online converter to create a PPTX version"
            ]
        )

    def _try_libreoffice_conversion(self, input_path: str) -> Optional[str]:
        """Try converting using LibreOffice."""
        try:
            import shutil
            
            # Check if LibreOffice is available
            if not shutil.which("libreoffice"):
                print("LibreOffice not found in PATH")
                return None
            
            # Create output directory for conversion
            input_dir = os.path.dirname(os.path.abspath(input_path))
            
            print(f"Converting PPT to PPTX using LibreOffice...")
            
            # Run LibreOffice conversion
            result = subprocess.run([
                "libreoffice", 
                "--headless", 
                "--convert-to", "pptx",
                "--outdir", input_dir,
                input_path
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                print(f"LibreOffice conversion failed: {result.stderr}")
                return None
            
            # Determine the output file path
            input_name = os.path.splitext(os.path.basename(input_path))[0]
            pptx_path = os.path.join(input_dir, f"{input_name}.pptx")
            
            if os.path.exists(pptx_path):
                print(f"Successfully converted to: {pptx_path}")
                self.temp_files.append(pptx_path)  # Track for cleanup
                return pptx_path
            else:
                print("LibreOffice conversion completed but output file not found")
                return None
                
        except subprocess.TimeoutExpired:
            print("LibreOffice conversion timed out")
            return None
        except Exception as e:
            print(f"LibreOffice conversion error: {e}")
            return None

    def __del__(self):
        """Cleanup temporary files."""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except:
                pass


# Alias for backward compatibility and CLI integration
class PptxToMdConverter(Ppt2MdConverter):
    """Alias for PPT to MD converter."""
    pass


# Additional converters that might be expected by the system
class Ppt2TxtConverter:
    """Convert PPT to plain text."""
    
    def convert(self, input_path: str, output_path: str) -> None:
        # Convert to PPTX first, then to text
        ppt_converter = Ppt2MdConverter()
        pptx_path = ppt_converter._convert_ppt_to_pptx(input_path)
        
        from .pptx2md import Pptx2TxtConverter
        txt_converter = Pptx2TxtConverter()
        txt_converter.convert(pptx_path, output_path)


class Ppt2PdfConverter:
    """Convert PPT to PDF."""
    
    def convert(self, input_path: str, output_path: str) -> None:
        # Convert to PPTX first, then to PDF
        ppt_converter = Ppt2MdConverter()
        pptx_path = ppt_converter._convert_ppt_to_pptx(input_path)
        
        from .pptx2md import Pptx2PdfConverter
        pdf_converter = Pptx2PdfConverter()
        pdf_converter.convert(pptx_path, output_path)


class Ppt2HtmlConverter:
    """Convert PPT to HTML."""
    
    def convert(self, input_path: str, output_path: str) -> None:
        # Convert to PPTX first, then to HTML
        ppt_converter = Ppt2MdConverter()
        pptx_path = ppt_converter._convert_ppt_to_pptx(input_path)
        
        from .pptx2md import Pptx2HtmlConverter
        html_converter = Pptx2HtmlConverter()
        html_converter.convert(pptx_path, output_path)