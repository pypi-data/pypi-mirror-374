"""
Format detection utilities for automatic file type identification.
"""

import os
import mimetypes
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum
# import magic  # Optional dependency
import zipfile
import xml.etree.ElementTree as ET


class DocumentFormat(Enum):
    """Enumeration of supported document formats."""
    PDF = "pdf"
    DOCX = "docx"
    DOC = "doc"
    ODT = "odt"
    RTF = "rtf"
    TXT = "txt"
    MD = "md"
    HTML = "html"
    XML = "xml"
    TEX = "tex"
    CSV = "csv"
    XLSX = "xlsx"
    XLS = "xls"
    PPTX = "pptx"
    PPT = "ppt"
    EPUB = "epub"
    JSON = "json"
    YAML = "yaml"
    HEIC = "heic"
    HEIF = "heif"
    JPG = "jpg"
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    WEBP = "webp"
    TIFF = "tiff"
    SVG = "svg"
    UNKNOWN = "unknown"


class FormatDetector:
    """Advanced format detection using multiple methods."""
    
    # MIME type mappings
    MIME_TYPE_MAP = {
        'application/pdf': DocumentFormat.PDF,
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': DocumentFormat.DOCX,
        'application/msword': DocumentFormat.DOC,
        'application/vnd.oasis.opendocument.text': DocumentFormat.ODT,
        'application/rtf': DocumentFormat.RTF,
        'text/plain': DocumentFormat.TXT,
        'text/markdown': DocumentFormat.MD,
        'text/html': DocumentFormat.HTML,
        'application/xml': DocumentFormat.XML,
        'text/xml': DocumentFormat.XML,
        'application/x-latex': DocumentFormat.TEX,
        'text/csv': DocumentFormat.CSV,
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': DocumentFormat.XLSX,
        'application/vnd.ms-excel': DocumentFormat.XLS,
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': DocumentFormat.PPTX,
        'application/vnd.ms-powerpoint': DocumentFormat.PPT,
        'application/epub+zip': DocumentFormat.EPUB,
        'application/json': DocumentFormat.JSON,
        'application/x-yaml': DocumentFormat.YAML,
        'text/yaml': DocumentFormat.YAML,
        'image/heic': DocumentFormat.HEIC,
        'image/heif': DocumentFormat.HEIF,
        'image/jpeg': DocumentFormat.JPEG,
        'image/png': DocumentFormat.PNG,
        'image/gif': DocumentFormat.GIF,
        'image/webp': DocumentFormat.WEBP,
        'image/tiff': DocumentFormat.TIFF,
        'image/svg+xml': DocumentFormat.SVG,
    }
    
    # Magic number signatures for binary format detection
    MAGIC_SIGNATURES = {
        b'%PDF-': DocumentFormat.PDF,
        b'PK\x03\x04': None,  # ZIP-based formats (need deeper inspection)
        b'{\\\rtf': DocumentFormat.RTF,
        b'\xff\xd8\xff': DocumentFormat.JPEG,
        b'\x89PNG\r\n\x1a\n': DocumentFormat.PNG,
        b'GIF8': DocumentFormat.GIF,
        b'RIFF': None,  # RIFF-based formats (need deeper inspection)
        b'\x00\x00\x00 ftypheic': DocumentFormat.HEIC,
        b'\x00\x00\x00 ftypheif': DocumentFormat.HEIF,
        b'WEBP': DocumentFormat.WEBP,
    }
    
    # Extension fallback mapping
    EXTENSION_MAP = {
        'pdf': DocumentFormat.PDF,
        'docx': DocumentFormat.DOCX,
        'doc': DocumentFormat.DOC,
        'odt': DocumentFormat.ODT,
        'rtf': DocumentFormat.RTF,
        'txt': DocumentFormat.TXT,
        'md': DocumentFormat.MD,
        'markdown': DocumentFormat.MD,
        'html': DocumentFormat.HTML,
        'htm': DocumentFormat.HTML,
        'xml': DocumentFormat.XML,
        'tex': DocumentFormat.TEX,
        'latex': DocumentFormat.TEX,
        'csv': DocumentFormat.CSV,
        'xlsx': DocumentFormat.XLSX,
        'xls': DocumentFormat.XLS,
        'pptx': DocumentFormat.PPTX,
        'ppt': DocumentFormat.PPT,
        'epub': DocumentFormat.EPUB,
        'json': DocumentFormat.JSON,
        'yaml': DocumentFormat.YAML,
        'yml': DocumentFormat.YAML,
        'heic': DocumentFormat.HEIC,
        'heif': DocumentFormat.HEIF,
        'jpg': DocumentFormat.JPEG,
        'jpeg': DocumentFormat.JPEG,
        'png': DocumentFormat.PNG,
        'gif': DocumentFormat.GIF,
        'webp': DocumentFormat.WEBP,
        'tiff': DocumentFormat.TIFF,
        'tif': DocumentFormat.TIFF,
        'svg': DocumentFormat.SVG,
    }
    
    def __init__(self, use_magic: bool = True):
        """Initialize format detector.
        
        Args:
            use_magic: Whether to use python-magic for MIME type detection
        """
        self.use_magic = use_magic
        self._magic_mime = None
        
        if use_magic:
            try:
                import magic
                self._magic_mime = magic.Magic(mime=True)
            except ImportError:
                self.use_magic = False
    
    def detect_format(self, file_path: str) -> Tuple[DocumentFormat, float]:
        """Detect document format using multiple methods.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Tuple of (detected_format, confidence_score)
            Confidence score ranges from 0.0 to 1.0
        """
        if not os.path.exists(file_path):
            return DocumentFormat.UNKNOWN, 0.0
            
        detection_results = []
        
        # Method 1: File extension
        ext_format, ext_confidence = self._detect_by_extension(file_path)
        detection_results.append((ext_format, ext_confidence, 'extension'))
        
        # Method 2: MIME type detection
        mime_format, mime_confidence = self._detect_by_mime_type(file_path)
        detection_results.append((mime_format, mime_confidence, 'mime'))
        
        # Method 3: Magic number/signature detection  
        magic_format, magic_confidence = self._detect_by_magic_numbers(file_path)
        detection_results.append((magic_format, magic_confidence, 'magic'))
        
        # Method 4: Content analysis for text-based formats
        content_format, content_confidence = self._detect_by_content_analysis(file_path)
        detection_results.append((content_format, content_confidence, 'content'))
        
        # Combine results using weighted scoring
        return self._combine_detection_results(detection_results)
    
    def _detect_by_extension(self, file_path: str) -> Tuple[DocumentFormat, float]:
        """Detect format by file extension."""
        try:
            _, ext = os.path.splitext(file_path.lower())
            ext = ext.lstrip('.')
            
            if ext in self.EXTENSION_MAP:
                return self.EXTENSION_MAP[ext], 0.7  # Moderate confidence
            return DocumentFormat.UNKNOWN, 0.0
        except Exception:
            return DocumentFormat.UNKNOWN, 0.0
    
    def _detect_by_mime_type(self, file_path: str) -> Tuple[DocumentFormat, float]:
        """Detect format by MIME type."""
        try:
            if self.use_magic and self._magic_mime:
                mime_type = self._magic_mime.from_file(file_path)
            else:
                mime_type, _ = mimetypes.guess_type(file_path)
                
            if mime_type and mime_type in self.MIME_TYPE_MAP:
                return self.MIME_TYPE_MAP[mime_type], 0.9  # High confidence
            return DocumentFormat.UNKNOWN, 0.0
        except Exception:
            return DocumentFormat.UNKNOWN, 0.0
    
    def _detect_by_magic_numbers(self, file_path: str) -> Tuple[DocumentFormat, float]:
        """Detect format by magic number/file signature."""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(32)  # Read first 32 bytes
                
            for signature, format_type in self.MAGIC_SIGNATURES.items():
                if header.startswith(signature):
                    if format_type:
                        return format_type, 0.95  # Very high confidence
                    elif signature == b'PK\\x03\\x04':
                        # ZIP-based format - need deeper inspection
                        zip_format = self._detect_zip_based_format(file_path)
                        if zip_format != DocumentFormat.UNKNOWN:
                            return zip_format, 0.9
                    elif signature == b'RIFF':
                        # RIFF-based format - check for WEBP
                        if len(header) >= 12 and header[8:12] == b'WEBP':
                            return DocumentFormat.WEBP, 0.95
                            
            return DocumentFormat.UNKNOWN, 0.0
        except Exception:
            return DocumentFormat.UNKNOWN, 0.0
    
    def _detect_zip_based_format(self, file_path: str) -> DocumentFormat:
        """Detect ZIP-based Office formats and EPUB."""
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                file_list = zip_file.namelist()
                
                # Check for Office Open XML formats
                if '[Content_Types].xml' in file_list:
                    try:
                        content_types = zip_file.read('[Content_Types].xml').decode('utf-8')
                        
                        if 'wordprocessingml' in content_types:
                            return DocumentFormat.DOCX
                        elif 'spreadsheetml' in content_types:
                            return DocumentFormat.XLSX  
                        elif 'presentationml' in content_types:
                            return DocumentFormat.PPTX
                    except Exception:
                        pass
                
                # Check for OpenDocument formats
                if 'META-INF/manifest.xml' in file_list:
                    try:
                        manifest = zip_file.read('META-INF/manifest.xml').decode('utf-8')
                        
                        if 'application/vnd.oasis.opendocument.text' in manifest:
                            return DocumentFormat.ODT
                    except Exception:
                        pass
                
                # Check for EPUB
                if 'META-INF/container.xml' in file_list:
                    return DocumentFormat.EPUB
                    
        except Exception:
            pass
            
        return DocumentFormat.UNKNOWN
    
    def _detect_by_content_analysis(self, file_path: str) -> Tuple[DocumentFormat, float]:
        """Detect format by analyzing file content."""
        try:
            # Only analyze files that might be text-based and aren't too large
            file_size = os.path.getsize(file_path)
            if file_size > 1024 * 1024:  # Skip files larger than 1MB
                return DocumentFormat.UNKNOWN, 0.0
                
            with open(file_path, 'rb') as f:
                raw_content = f.read(min(file_size, 8192))  # Read up to 8KB
                
            # Try to decode as text
            try:
                content = raw_content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    content = raw_content.decode('latin1')
                except UnicodeDecodeError:
                    return DocumentFormat.UNKNOWN, 0.0
            
            content_lower = content.lower().strip()
            
            # HTML detection
            if any(tag in content_lower for tag in ['<html', '<head>', '<body>', '<!doctype html']):
                return DocumentFormat.HTML, 0.8
                
            # XML detection
            if content_lower.startswith('<?xml') or content_lower.startswith('<'):
                return DocumentFormat.XML, 0.6
                
            # LaTeX detection
            if any(cmd in content for cmd in ['\\documentclass', '\\begin{document}', '\\usepackage']):
                return DocumentFormat.TEX, 0.8
                
            # Markdown detection
            markdown_indicators = ['# ', '## ', '### ', '* ', '- ', '+ ', '[', '](']
            if any(indicator in content for indicator in markdown_indicators):
                return DocumentFormat.MD, 0.6
                
            # CSV detection
            lines = content.split('\\n')[:5]  # Check first 5 lines
            if len(lines) >= 2 and all(',' in line for line in lines if line.strip()):
                return DocumentFormat.CSV, 0.7
                
            # JSON detection  
            content_stripped = content.strip()
            if (content_stripped.startswith('{') and content_stripped.endswith('}')) or \
               (content_stripped.startswith('[') and content_stripped.endswith(']')):
                try:
                    import json
                    json.loads(content)
                    return DocumentFormat.JSON, 0.9
                except:
                    pass
                    
            # YAML detection
            if content.startswith('---\\n') or ':\\n' in content or ': ' in content:
                return DocumentFormat.YAML, 0.5
                
            return DocumentFormat.TXT, 0.3  # Default to text with low confidence
            
        except Exception:
            return DocumentFormat.UNKNOWN, 0.0
    
    def _combine_detection_results(self, results: List[Tuple[DocumentFormat, float, str]]) -> Tuple[DocumentFormat, float]:
        """Combine multiple detection results using weighted scoring."""
        
        # Weights for different detection methods
        method_weights = {
            'extension': 0.2,
            'mime': 0.4, 
            'magic': 0.3,
            'content': 0.1
        }
        
        # Group results by format
        format_scores = {}
        
        for format_type, confidence, method in results:
            if format_type == DocumentFormat.UNKNOWN:
                continue
                
            weight = method_weights.get(method, 0.1)
            weighted_score = confidence * weight
            
            if format_type in format_scores:
                format_scores[format_type] += weighted_score
            else:
                format_scores[format_type] = weighted_score
        
        if not format_scores:
            return DocumentFormat.UNKNOWN, 0.0
            
        # Return format with highest score
        best_format = max(format_scores.items(), key=lambda x: x[1])
        return best_format[0], min(best_format[1], 1.0)
    
    def get_supported_formats(self) -> List[DocumentFormat]:
        """Get list of all supported formats."""
        return list(DocumentFormat)
    
    def is_format_supported(self, format_type: DocumentFormat) -> bool:
        """Check if a format is supported for conversion."""
        return format_type in self.EXTENSION_MAP.values()


# Global detector instance
_detector = FormatDetector()

def detect_file_format(file_path: str) -> Tuple[DocumentFormat, float]:
    """Convenience function to detect file format."""
    return _detector.detect_format(file_path)

def get_format_by_extension(extension: str) -> DocumentFormat:
    """Get format by file extension."""
    return FormatDetector.EXTENSION_MAP.get(extension.lower().lstrip('.'), DocumentFormat.UNKNOWN)