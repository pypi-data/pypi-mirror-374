"""
Universal conversion pipeline framework for Docuvert.

This module provides a unified interface for document conversion that can
work through direct conversion or via the AST system.
"""

import os
import importlib
from typing import Optional, Dict, Any, List, Callable, Protocol
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum

from .ast import ASTNode, DocumentMetadata, NodeType
from .format_detector import DocumentFormat, detect_file_format


class ConversionStrategy(Enum):
    """Available conversion strategies."""
    DIRECT = "direct"           # Direct library-based conversion
    AST_BASED = "ast_based"     # Convert via AST representation
    HYBRID = "hybrid"           # Try direct first, fallback to AST
    AUTO = "auto"               # Automatically choose best strategy


class ConversionQuality(Enum):
    """Quality levels for conversion."""
    FAST = "fast"               # Fastest conversion, may lose some formatting
    BALANCED = "balanced"       # Balance between speed and quality
    HIGH_FIDELITY = "high"      # Best quality, preserve all formatting


@dataclass
class ConversionOptions:
    """Options for controlling conversion behavior."""
    strategy: ConversionStrategy = ConversionStrategy.AUTO
    quality: ConversionQuality = ConversionQuality.BALANCED
    preserve_metadata: bool = True
    preserve_images: bool = True
    preserve_formatting: bool = True
    custom_options: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class ConversionResult:
    """Result of a conversion operation."""
    success: bool
    output_path: str
    source_format: DocumentFormat
    target_format: DocumentFormat
    strategy_used: ConversionStrategy
    metadata: Optional[DocumentMetadata] = None
    warnings: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    processing_time: Optional[float] = None


class BaseConverter(Protocol):
    """Protocol for converter classes."""
    
    def convert(self, input_path: str, output_path: str) -> None:
        """Direct conversion method."""
        ...
        
    def parse_to_ast(self, input_path: str) -> ASTNode:
        """Parse input to AST representation."""
        ...
        
    def ast_to_output(self, ast_root: ASTNode, output_path: str) -> None:
        """Convert AST to output format."""
        ...


class ConversionPipeline:
    """Universal conversion pipeline with multiple strategies."""
    
    def __init__(self):
        self._converter_cache: Dict[str, Any] = {}
        self._parsers: Dict[DocumentFormat, List[Callable]] = {}
        self._generators: Dict[DocumentFormat, List[Callable]] = {}
        
    def register_parser(self, format_type: DocumentFormat, parser_func: Callable):
        """Register a parser function for a specific format."""
        if format_type not in self._parsers:
            self._parsers[format_type] = []
        self._parsers[format_type].append(parser_func)
        
    def register_generator(self, format_type: DocumentFormat, generator_func: Callable):
        """Register a generator function for a specific format."""
        if format_type not in self._generators:
            self._generators[format_type] = []
        self._generators[format_type].append(generator_func)
    
    def convert(
        self,
        input_path: str,
        output_path: str, 
        source_format: Optional[DocumentFormat] = None,
        target_format: Optional[DocumentFormat] = None,
        options: Optional[ConversionOptions] = None
    ) -> ConversionResult:
        """
        Main conversion method with automatic format detection and strategy selection.
        
        Args:
            input_path: Path to input file
            output_path: Path for output file
            source_format: Source format (auto-detected if None)
            target_format: Target format (derived from output extension if None)
            options: Conversion options
            
        Returns:
            ConversionResult with details about the conversion
        """
        import time
        start_time = time.time()
        
        options = options or ConversionOptions()
        
        try:
            # Auto-detect formats if not provided
            if not source_format:
                detected_format, confidence = detect_file_format(input_path)
                source_format = detected_format
                if confidence < 0.5:
                    return ConversionResult(
                        success=False,
                        output_path=output_path,
                        source_format=source_format,
                        target_format=target_format or DocumentFormat.UNKNOWN,
                        strategy_used=ConversionStrategy.AUTO,
                        error_message=f"Could not reliably detect input format (confidence: {confidence:.2f})"
                    )
            
            if not target_format:
                target_format = self._detect_target_format(output_path)
                if target_format == DocumentFormat.UNKNOWN:
                    return ConversionResult(
                        success=False,
                        output_path=output_path,
                        source_format=source_format,
                        target_format=target_format,
                        strategy_used=ConversionStrategy.AUTO,
                        error_message="Could not determine target format from output path"
                    )
            
            # Choose conversion strategy
            strategy = self._choose_strategy(source_format, target_format, options)
            
            # Execute conversion
            result = self._execute_conversion(
                input_path, output_path, source_format, target_format, strategy, options
            )
            
            result.processing_time = time.time() - start_time
            return result
            
        except Exception as e:
            return ConversionResult(
                success=False,
                output_path=output_path,
                source_format=source_format or DocumentFormat.UNKNOWN,
                target_format=target_format or DocumentFormat.UNKNOWN,
                strategy_used=options.strategy,
                error_message=str(e),
                processing_time=time.time() - start_time
            )
    
    def _detect_target_format(self, output_path: str) -> DocumentFormat:
        """Detect target format from output file extension."""
        from .format_detector import get_format_by_extension
        _, ext = os.path.splitext(output_path)
        return get_format_by_extension(ext)
    
    def _choose_strategy(
        self, 
        source_format: DocumentFormat, 
        target_format: DocumentFormat,
        options: ConversionOptions
    ) -> ConversionStrategy:
        """Choose optimal conversion strategy based on formats and options."""
        
        if options.strategy != ConversionStrategy.AUTO:
            return options.strategy
            
        # Strategy selection logic
        converter_name = f"{source_format.value}2{target_format.value}"
        
        # Check if direct converter exists and is likely to be high-quality
        if self._has_direct_converter(converter_name):
            # For common conversions, direct is usually best
            common_conversions = {
                ('pdf', 'docx'), ('docx', 'pdf'), ('md', 'html'), ('html', 'md'),
                ('csv', 'xlsx'), ('xlsx', 'csv'), ('txt', 'md'), ('md', 'txt')
            }
            
            if (source_format.value, target_format.value) in common_conversions:
                return ConversionStrategy.DIRECT
                
        # For complex formatting preservation, prefer AST if available
        if options.quality == ConversionQuality.HIGH_FIDELITY:
            if self._has_ast_support(source_format) and self._has_ast_support(target_format):
                return ConversionStrategy.AST_BASED
                
        # Default to hybrid approach
        return ConversionStrategy.HYBRID
    
    def _has_direct_converter(self, converter_name: str) -> bool:
        """Check if a direct converter exists for the given conversion."""
        try:
            module_path = f"docuvert.converters.{converter_name}"
            importlib.import_module(module_path)
            return True
        except ImportError:
            return False
    
    def _has_ast_support(self, format_type: DocumentFormat) -> bool:
        """Check if AST support is available for a format."""
        return format_type in self._parsers and format_type in self._generators
    
    def _execute_conversion(
        self,
        input_path: str,
        output_path: str,
        source_format: DocumentFormat,
        target_format: DocumentFormat,
        strategy: ConversionStrategy,
        options: ConversionOptions
    ) -> ConversionResult:
        """Execute the conversion using the specified strategy."""
        
        warnings = []
        
        try:
            if strategy == ConversionStrategy.DIRECT:
                return self._convert_direct(input_path, output_path, source_format, target_format, options)
                
            elif strategy == ConversionStrategy.AST_BASED:
                return self._convert_via_ast(input_path, output_path, source_format, target_format, options)
                
            elif strategy == ConversionStrategy.HYBRID:
                # Try direct first
                try:
                    return self._convert_direct(input_path, output_path, source_format, target_format, options)
                except Exception as e:
                    warnings.append(f"Direct conversion failed: {str(e)}")
                    # Fallback to AST
                    result = self._convert_via_ast(input_path, output_path, source_format, target_format, options)
                    result.warnings.extend(warnings)
                    return result
                    
            else:
                raise ValueError(f"Unknown conversion strategy: {strategy}")
                
        except Exception as e:
            return ConversionResult(
                success=False,
                output_path=output_path,
                source_format=source_format,
                target_format=target_format,
                strategy_used=strategy,
                warnings=warnings,
                error_message=str(e)
            )
    
    def _convert_direct(
        self,
        input_path: str,
        output_path: str,
        source_format: DocumentFormat,
        target_format: DocumentFormat,
        options: ConversionOptions
    ) -> ConversionResult:
        """Perform direct conversion using existing converter classes."""
        
        converter_name = f"{source_format.value}2{target_format.value}"
        
        # Load converter
        converter = self._get_converter(converter_name)
        
        # Execute conversion
        converter.convert(input_path, output_path)
        
        # Verify output was created
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            raise RuntimeError("Conversion completed but output file is empty or missing")
        
        return ConversionResult(
            success=True,
            output_path=output_path,
            source_format=source_format,
            target_format=target_format,
            strategy_used=ConversionStrategy.DIRECT
        )
    
    def _convert_via_ast(
        self,
        input_path: str,
        output_path: str,
        source_format: DocumentFormat,
        target_format: DocumentFormat,
        options: ConversionOptions
    ) -> ConversionResult:
        """Perform conversion via AST representation."""
        
        # Parse input to AST
        if source_format not in self._parsers:
            raise ValueError(f"No AST parser available for format: {source_format}")
            
        parser = self._parsers[source_format][0]  # Use first available parser
        ast_root = parser(input_path)
        
        # Generate output from AST
        if target_format not in self._generators:
            raise ValueError(f"No AST generator available for format: {target_format}")
            
        generator = self._generators[target_format][0]  # Use first available generator
        generator(ast_root, output_path)
        
        # Verify output was created
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            raise RuntimeError("AST conversion completed but output file is empty or missing")
        
        return ConversionResult(
            success=True,
            output_path=output_path,
            source_format=source_format,
            target_format=target_format,
            strategy_used=ConversionStrategy.AST_BASED,
            metadata=ast_root.metadata
        )
    
    def _get_converter(self, converter_name: str) -> Any:
        """Get converter instance, using cache if available."""
        
        if converter_name in self._converter_cache:
            return self._converter_cache[converter_name]
        
        # Load converter module
        try:
            module_path = f"docuvert.converters.{converter_name}"
            converter_module = importlib.import_module(module_path)
            
            # Get converter class
            parts = converter_name.split('2')
            class_name = f"{parts[0].capitalize()}2{parts[1].capitalize()}Converter"
            converter_class = getattr(converter_module, class_name)
            
            # Create instance
            converter_instance = converter_class()
            
            # Cache for future use
            self._converter_cache[converter_name] = converter_instance
            
            return converter_instance
            
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Could not load converter {converter_name}: {e}")
    
    def list_available_conversions(self) -> Dict[DocumentFormat, List[DocumentFormat]]:
        """List all available conversions."""
        conversions = {}
        
        # Scan converter modules
        converters_path = os.path.join(os.path.dirname(__file__), '..', 'converters')
        if os.path.exists(converters_path):
            for filename in os.listdir(converters_path):
                if filename.endswith('.py') and '2' in filename and filename != '__init__.py':
                    converter_name = filename[:-3]  # Remove .py
                    if '2' in converter_name:
                        parts = converter_name.split('2')
                        source_format = DocumentFormat(parts[0])
                        target_format = DocumentFormat(parts[1])
                        
                        if source_format not in conversions:
                            conversions[source_format] = []
                        conversions[source_format].append(target_format)
        
        return conversions
    
    def get_conversion_path(
        self, 
        source_format: DocumentFormat, 
        target_format: DocumentFormat
    ) -> Optional[List[DocumentFormat]]:
        """Find a conversion path between two formats (for multi-step conversions)."""
        # For now, only support direct conversions
        # TODO: Implement multi-step conversion path finding
        
        direct_converter = f"{source_format.value}2{target_format.value}"
        if self._has_direct_converter(direct_converter):
            return [source_format, target_format]
            
        return None


# Global pipeline instance
_pipeline = ConversionPipeline()

def convert_document(
    input_path: str,
    output_path: str,
    source_format: Optional[DocumentFormat] = None,
    target_format: Optional[DocumentFormat] = None,
    options: Optional[ConversionOptions] = None
) -> ConversionResult:
    """Convenience function for document conversion."""
    return _pipeline.convert(input_path, output_path, source_format, target_format, options)

def get_pipeline() -> ConversionPipeline:
    """Get the global conversion pipeline instance."""
    return _pipeline