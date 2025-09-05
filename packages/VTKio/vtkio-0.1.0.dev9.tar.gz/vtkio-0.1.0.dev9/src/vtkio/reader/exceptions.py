# !/usr/bin/env python
"""
Custom exceptions for VTK readers with simplified error handling.
"""

__author__ = 'J.P. Morrissey'
__copyright__ = 'Copyright 2022-2025'
__maintainer__ = 'J.P. Morrissey'
__email__ = 'morrissey.jp@gmail.com'
__status__ = 'Development'

class VTKReaderError(Exception):
    """Base exception for all VTK reader errors."""
    pass


class UnsupportedFormatError(VTKReaderError):
    """Raised when an unsupported file format is encountered."""
    pass


class InvalidVTKFileError(VTKReaderError):
    """Raised when a file is not a valid VTK file."""
    pass


class DataCorruptionError(VTKReaderError):
    """Raised when data appears to be corrupted or malformed."""
    pass


class MissingDataError(VTKReaderError):
    """Raised when required data is missing from the file."""
    pass


class TopologyError(VTKReaderError):
    """Raised when there are issues with mesh topology."""
    pass