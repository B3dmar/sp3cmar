"""Sp3cMar exception hierarchy."""


class Sp3cMarError(Exception):
    """Base exception for all Sp3cMar errors."""


class SymlinkError(Sp3cMarError):
    """Raised when a symlink is detected where it shouldn't be."""


class PathTraversalError(Sp3cMarError):
    """Raised when path traversal is detected in a slug or filename."""
