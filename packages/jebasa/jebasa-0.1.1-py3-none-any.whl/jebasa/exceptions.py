"""Custom exceptions for Jebasa."""


class JebasaError(Exception):
    """Base exception for all Jebasa errors."""
    pass


class AudioProcessingError(JebasaError):
    """Raised when audio processing fails."""
    pass


class TextProcessingError(JebasaError):
    """Raised when text processing fails."""
    pass


class AlignmentError(JebasaError):
    """Raised when MFA alignment fails."""
    pass


class DictionaryError(JebasaError):
    """Raised when dictionary creation fails."""
    pass


class SubtitleGenerationError(JebasaError):
    """Raised when subtitle generation fails."""
    pass


class ConfigurationError(JebasaError):
    """Raised when configuration is invalid."""
    pass


class ValidationError(JebasaError):
    """Raised when input validation fails."""
    pass


class FileFormatError(JebasaError):
    """Raised when file format is not supported."""
    pass