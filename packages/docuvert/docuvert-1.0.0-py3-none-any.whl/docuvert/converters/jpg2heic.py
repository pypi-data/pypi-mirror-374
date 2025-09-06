"""
JPEG to HEIC converter with quality optimization.
"""

import sys
import os
import subprocess
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.exceptions import ConversionError, DependencyError

try:
    from PIL import Image
except ImportError as e:
    raise DependencyError(
        "Pillow is required for image conversion",
        missing_dependency="pillow"
    ) from e


class Jpg2HeicConverter:
    """Convert JPEG to HEIC format with quality preservation."""

    def parse_jpg2ast(self, input_path: str):
        """Parse JPEG to AST representation (placeholder)."""
        return None  # Images don't have complex AST structure

    def ast2heic(self, ast_root, output_path: str):
        """Convert AST to HEIC (placeholder).""" 
        pass

    def convert(self, input_path: str, output_path: str) -> None:
        """Convert JPEG to HEIC using available methods."""
        
        if not os.path.exists(input_path):
            raise ConversionError(f"Input file not found: {input_path}")

        if not output_path.lower().endswith((".heic", ".heif")):
            output_path += ".heic"

        errors = []

        # Method 1: pillow-heif (best option)
        try:
            import pillow_heif
            pillow_heif.register_heif_opener()
            
            with Image.open(input_path) as img:
                # Ensure RGB mode for HEIC
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Save with high quality settings
                img.save(output_path, format='HEIF', quality=95, optimize=True)
            
            print(f"Converted via pillow-heif: {output_path}")
            return
            
        except ImportError as e:
            errors.append(f"pillow-heif not available: {e}")
        except Exception as e:
            errors.append(f"pillow-heif conversion failed: {e}")

        # Method 2: ImageMagick
        try:
            import shutil
            if shutil.which("magick"):
                result = subprocess.run([
                    "magick", input_path, "-quality", "95", output_path
                ], capture_output=True, text=True)
                
                if result.returncode == 0 and os.path.exists(output_path):
                    print(f"Converted via ImageMagick: {output_path}")
                    return
                    
                errors.append(f"ImageMagick failed: {result.stderr.strip()}")
            else:
                errors.append("ImageMagick 'magick' not found")
        except Exception as e:
            errors.append(f"ImageMagick invocation failed: {e}")

        # Method 3: macOS sips (if available)
        if sys.platform == "darwin":
            try:
                import shutil
                if shutil.which("sips"):
                    result = subprocess.run([
                        "sips", "-s", "format", "heif", input_path, "--out", output_path
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0 and os.path.exists(output_path):
                        print(f"Converted via sips: {output_path}")
                        return
                        
                    errors.append(f"sips failed: {result.stderr.strip()}")
                else:
                    errors.append("sips not found")
            except Exception as e:
                errors.append(f"sips invocation failed: {e}")

        raise ConversionError(
            "JPEG→HEIC conversion failed with all methods.\n" +
            "Errors: " + " | ".join(errors) + 
            "\nInstall pillow-heif (recommended) or ImageMagick/sips.",
            source_format="jpeg",
            target_format="heic",
            suggestions=[
                "pip install pillow-heif (recommended)",
                "Install ImageMagick with HEIF support", 
                "On macOS, use built-in sips command"
            ]
        )


class Jpg2PngConverter:
    """Convert JPEG to PNG format."""

    def parse_jpg2ast(self, input_path: str):
        """Parse JPEG to AST representation (placeholder)."""
        return None

    def ast2png(self, ast_root, output_path: str):
        """Convert AST to PNG (placeholder)."""
        pass

    def convert(self, input_path: str, output_path: str) -> None:
        """Convert JPEG to PNG."""
        
        if not os.path.exists(input_path):
            raise ConversionError(f"Input file not found: {input_path}")

        if not output_path.lower().endswith(".png"):
            output_path += ".png"

        try:
            with Image.open(input_path) as img:
                # Convert to RGBA to preserve any transparency
                if img.mode not in ('RGBA', 'LA'):
                    img = img.convert('RGBA')
                
                img.save(output_path, "PNG", optimize=True)
            
            print(f"Successfully converted '{input_path}' to '{output_path}'")
            
        except Exception as e:
            raise ConversionError(
                f"JPEG to PNG conversion failed: {e}",
                source_format="jpeg", 
                target_format="png"
            )