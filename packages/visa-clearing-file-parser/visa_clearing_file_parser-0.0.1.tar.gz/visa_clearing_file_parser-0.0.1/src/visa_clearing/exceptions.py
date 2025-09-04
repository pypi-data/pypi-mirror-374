"""Custom exceptions for visa-clearing-file-parser library"""

class VisaClearingError(Exception):
    """Base exception for visa-clearing-file-parser library"""
    pass

class ParseError(VisaClearingError):
    """Raised when parsing fails"""
    pass

class EncodingError(VisaClearingError):
    """Raised when encoding detection fails"""
    pass