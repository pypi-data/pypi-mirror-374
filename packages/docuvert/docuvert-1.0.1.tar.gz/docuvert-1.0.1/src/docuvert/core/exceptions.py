"""
Comprehensive exception handling framework for Docuvert.

This module provides structured error handling with detailed error information,
recovery suggestions, and logging capabilities.
"""

import logging
import traceback
from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass, field

from .format_detector import DocumentFormat


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"           # Minor issues, conversion may still work
    MEDIUM = "medium"     # Significant issues, quality may be affected
    HIGH = "high"         # Major issues, conversion likely to fail
    CRITICAL = "critical" # System errors, immediate attention required


class ErrorCategory(Enum):
    """Categories of errors that can occur."""
    FILE_IO = "file_io"                    # File reading/writing issues
    FORMAT_DETECTION = "format_detection" # Format detection failures
    PARSING = "parsing"                    # Document parsing errors
    CONVERSION = "conversion"              # Conversion process errors
    DEPENDENCY = "dependency"              # Missing dependencies
    VALIDATION = "validation"              # Input validation errors
    SYSTEM = "system"                      # System/environment issues
    CONFIGURATION = "configuration"       # Configuration/settings errors
    NETWORK = "network"                    # Network-related errors (future)
    MEMORY = "memory"                      # Memory/resource issues


@dataclass
class ErrorDetails:
    """Detailed error information."""
    code: str
    message: str
    category: ErrorCategory
    severity: ErrorSeverity
    suggestions: List[str] = field(default_factory=list)
    technical_details: Optional[str] = None
    related_file: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)


class DocuvertException(Exception):
    """Base exception for all Docuvert errors."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "UNKNOWN_ERROR",
        category: ErrorCategory = ErrorCategory.SYSTEM,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        suggestions: Optional[List[str]] = None,
        technical_details: Optional[str] = None,
        related_file: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.details = ErrorDetails(
            code=error_code,
            message=message,
            category=category,
            severity=severity,
            suggestions=suggestions or [],
            technical_details=technical_details,
            related_file=related_file,
            context=context or {}
        )
    
    def __str__(self) -> str:
        return f"[{self.details.code}] {self.details.message}"


class FileIOError(DocuvertException):
    """File input/output related errors."""
    
    def __init__(self, message: str, file_path: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code=kwargs.get("error_code", "FILE_IO_ERROR"),
            category=ErrorCategory.FILE_IO,
            severity=kwargs.get("severity", ErrorSeverity.HIGH),
            related_file=file_path,
            **{k: v for k, v in kwargs.items() if k not in ["error_code", "severity"]}
        )


class FormatDetectionError(DocuvertException):
    """Format detection related errors."""
    
    def __init__(self, message: str, file_path: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code=kwargs.get("error_code", "FORMAT_DETECTION_ERROR"),
            category=ErrorCategory.FORMAT_DETECTION,
            severity=kwargs.get("severity", ErrorSeverity.MEDIUM),
            related_file=file_path,
            **{k: v for k, v in kwargs.items() if k not in ["error_code", "severity"]}
        )


class ParsingError(DocuvertException):
    """Document parsing related errors."""
    
    def __init__(self, message: str, file_path: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code=kwargs.get("error_code", "PARSING_ERROR"),
            category=ErrorCategory.PARSING,
            severity=kwargs.get("severity", ErrorSeverity.HIGH),
            related_file=file_path,
            **{k: v for k, v in kwargs.items() if k not in ["error_code", "severity"]}
        )


class ConversionError(DocuvertException):
    """Document conversion related errors."""
    
    def __init__(
        self, 
        message: str, 
        source_format: Optional[DocumentFormat] = None,
        target_format: Optional[DocumentFormat] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if source_format:
            context["source_format"] = source_format.value
        if target_format:
            context["target_format"] = target_format.value
            
        super().__init__(
            message=message,
            error_code=kwargs.get("error_code", "CONVERSION_ERROR"),
            category=ErrorCategory.CONVERSION,
            severity=kwargs.get("severity", ErrorSeverity.HIGH),
            context=context,
            **{k: v for k, v in kwargs.items() if k not in ["error_code", "severity", "context"]}
        )


class DependencyError(DocuvertException):
    """Missing dependency related errors."""
    
    def __init__(self, message: str, missing_dependency: Optional[str] = None, **kwargs):
        suggestions = kwargs.get("suggestions", [])
        if missing_dependency and not suggestions:
            suggestions = [
                f"Install the missing dependency: pip install {missing_dependency}",
                "Check the requirements.txt file for all required dependencies",
                "Run ./setup.sh to install all dependencies automatically"
            ]
        
        context = kwargs.get("context", {})
        if missing_dependency:
            context["missing_dependency"] = missing_dependency
            
        super().__init__(
            message=message,
            error_code=kwargs.get("error_code", "DEPENDENCY_ERROR"),
            category=ErrorCategory.DEPENDENCY,
            severity=kwargs.get("severity", ErrorSeverity.HIGH),
            suggestions=suggestions,
            context=context,
            **{k: v for k, v in kwargs.items() if k not in ["error_code", "severity", "suggestions", "context"]}
        )


class ValidationError(DocuvertException):
    """Input validation related errors."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            error_code=kwargs.get("error_code", "VALIDATION_ERROR"),
            category=ErrorCategory.VALIDATION,
            severity=kwargs.get("severity", ErrorSeverity.MEDIUM),
            **{k: v for k, v in kwargs.items() if k not in ["error_code", "severity"]}
        )


class ConfigurationError(DocuvertException):
    """Configuration related errors."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            error_code=kwargs.get("error_code", "CONFIGURATION_ERROR"),
            category=ErrorCategory.CONFIGURATION,
            severity=kwargs.get("severity", ErrorSeverity.MEDIUM),
            **{k: v for k, v in kwargs.items() if k not in ["error_code", "severity"]}
        )


class MemoryError(DocuvertException):
    """Memory/resource related errors."""
    
    def __init__(self, message: str, **kwargs):
        suggestions = kwargs.get("suggestions", [])
        if not suggestions:
            suggestions = [
                "Try processing smaller files or reduce quality settings",
                "Close other applications to free up memory",
                "Consider splitting large documents into smaller parts"
            ]
            
        super().__init__(
            message=message,
            error_code=kwargs.get("error_code", "MEMORY_ERROR"),
            category=ErrorCategory.MEMORY,
            severity=kwargs.get("severity", ErrorSeverity.HIGH),
            suggestions=suggestions,
            **{k: v for k, v in kwargs.items() if k not in ["error_code", "severity", "suggestions"]}
        )


class ErrorHandler:
    """Central error handling and logging system."""
    
    def __init__(self, logger_name: str = "docuvert"):
        self.logger = logging.getLogger(logger_name)
        self.error_counts: Dict[str, int] = {}
        
    def handle_exception(
        self, 
        exception: Exception, 
        context: Optional[Dict[str, Any]] = None,
        log_level: int = logging.ERROR
    ) -> DocuvertException:
        """Handle any exception and convert to DocuvertException if needed."""
        
        if isinstance(exception, DocuvertException):
            docuvert_exception = exception
        else:
            # Convert standard exceptions to DocuvertException
            docuvert_exception = self._convert_standard_exception(exception, context)
        
        # Log the error
        self._log_error(docuvert_exception, log_level)
        
        # Update error counts
        self.error_counts[docuvert_exception.details.code] = \
            self.error_counts.get(docuvert_exception.details.code, 0) + 1
            
        return docuvert_exception
    
    def _convert_standard_exception(
        self, 
        exception: Exception, 
        context: Optional[Dict[str, Any]] = None
    ) -> DocuvertException:
        """Convert standard Python exceptions to DocuvertException."""
        
        context = context or {}
        
        if isinstance(exception, FileNotFoundError):
            return FileIOError(
                message=f"File not found: {str(exception)}",
                error_code="FILE_NOT_FOUND",
                suggestions=[
                    "Check that the file path is correct",
                    "Verify the file exists and is accessible",
                    "Check file permissions"
                ],
                context=context
            )
            
        elif isinstance(exception, PermissionError):
            return FileIOError(
                message=f"Permission denied: {str(exception)}",
                error_code="PERMISSION_DENIED",
                suggestions=[
                    "Check file permissions",
                    "Run with appropriate user privileges",
                    "Ensure the file is not being used by another process"
                ],
                context=context
            )
            
        elif isinstance(exception, ImportError):
            module_name = str(exception).split("'")
            module_name = module_name[1] if len(module_name) > 1 else "unknown"
            
            return DependencyError(
                message=f"Missing dependency: {str(exception)}",
                error_code="MISSING_DEPENDENCY",
                missing_dependency=module_name,
                context=context
            )
            
        elif isinstance(exception, MemoryError):
            return MemoryError(
                message="Insufficient memory to complete operation",
                error_code="OUT_OF_MEMORY",
                context=context
            )
            
        elif isinstance(exception, ValueError):
            return ValidationError(
                message=f"Invalid value: {str(exception)}",
                error_code="INVALID_VALUE",
                suggestions=[
                    "Check input parameters and values",
                    "Verify file format and content"
                ],
                context=context
            )
            
        else:
            # Generic exception conversion
            return DocuvertException(
                message=str(exception),
                error_code="UNEXPECTED_ERROR",
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.HIGH,
                technical_details=traceback.format_exc(),
                context=context
            )
    
    def _log_error(self, exception: DocuvertException, log_level: int):
        """Log error details."""
        
        details = exception.details
        
        # Create log message
        log_message = f"[{details.code}] {details.message}"
        
        # Add context information
        if details.related_file:
            log_message += f" (File: {details.related_file})"
            
        # Log at appropriate level
        self.logger.log(log_level, log_message)
        
        # Log technical details at debug level
        if details.technical_details:
            self.logger.debug(f"Technical details for {details.code}: {details.technical_details}")
            
        # Log suggestions at info level
        if details.suggestions:
            self.logger.info(f"Suggestions for {details.code}: {'; '.join(details.suggestions)}")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of errors encountered."""
        return {
            "total_errors": sum(self.error_counts.values()),
            "error_counts": self.error_counts.copy(),
            "most_common_errors": sorted(
                self.error_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
        }
    
    def reset_error_counts(self):
        """Reset error counting."""
        self.error_counts.clear()


# Global error handler instance
_error_handler = ErrorHandler()

def handle_error(
    exception: Exception,
    context: Optional[Dict[str, Any]] = None,
    log_level: int = logging.ERROR
) -> DocuvertException:
    """Convenience function for error handling."""
    return _error_handler.handle_exception(exception, context, log_level)

def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    return _error_handler


# Context manager for error handling
class ErrorContext:
    """Context manager for structured error handling."""
    
    def __init__(
        self, 
        operation: str,
        file_path: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ):
        self.operation = operation
        self.context = {
            "operation": operation,
            **(additional_context or {})
        }
        if file_path:
            self.context["file_path"] = file_path
    
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_value, traceback_obj):
        if exc_value:
            # Handle the exception
            handled_exception = handle_error(exc_value, self.context)
            
            # Re-raise the handled exception
            raise handled_exception
        return False


def safe_execute(func, *args, **kwargs):
    """Execute a function with error handling."""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        handled_exception = handle_error(e)
        raise handled_exception