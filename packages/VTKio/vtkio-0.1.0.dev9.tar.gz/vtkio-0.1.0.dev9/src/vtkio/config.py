# !/usr/bin/env python
"""
Configuration settings for the VTKio package.

This centralises all magic strings, type mappings, and configuration
to make the system more maintainable.
"""

__author__ = 'J.P. Morrissey'
__copyright__ = 'Copyright 2022-2025'
__maintainer__ = 'J.P. Morrissey'
__email__ = 'morrissey.jp@gmail.com'
__status__ = 'Development'

import numpy as np
from typing import Dict, Set, Any
from pathlib import Path
import logging


class VTKConfig:
    """Central configuration for VTK readers."""

    # File format support
    SUPPORTED_XML_EXTENSIONS: Set[str] = {'.vti', '.vtr', '.vts', '.vtu', '.vtp'}
    SUPPORTED_HDF5_EXTENSIONS: Set[str] = {'.h5', '.hdf5', 'vtkhdf', '.hdf'}

    # VTK data types
    SUPPORTED_VTK_TYPES: Set[str] = {
        'ImageData', 'PolyData', 'UnstructuredGrid',
        'StructuredGrid', 'RectilinearGrid'
    }

    # File format defaults
    DEFAULT_ENCODING: str = 'utf-8'
    DEFAULT_BYTE_ORDER: str = 'little_endian'

    # Data type mappings for XML parsing
    XML_TYPE_MAPPING: Dict[str, Any] = {
        'int': np.int64,
        'float': np.float32,
        'double': np.float64,
        'float16': np.float16,
        'float32': np.float32,
        'float64': np.float64,
        'int8': np.int8,
        'int16': np.int16,
        'int32': np.int32,
        'int64': np.int64,
        'uint8': np.uint8,
        'uint16': np.uint16,
        'uint32': np.uint32,
        'uint64': np.uint64,
        'string': 's'
    }

    # Required data sections for each VTK type
    REQUIRED_DATA_SECTIONS: Dict[str, Set[str]] = {
        'UnstructuredGrid': {'Points', 'Cells'},
        'PolyData': {'Points'},
        'ImageData': set(),  # Grid info comes from attributes
        'StructuredGrid': {'Points'},
        'RectilinearGrid': {'Coordinates'}
    }

    # Optional data sections (always try to read these)
    OPTIONAL_DATA_SECTIONS: Set[str] = {'PointData', 'CellData', 'FieldData'}

    # XML specific constants
    XML_ARRAY_KEYS: Set[str] = {'DataArray', 'Array'}
    XML_DATA_FORMATS: Set[str] = {'ascii', 'binary', 'appended'}

    # HDF5 specific constants
    HDF5_VTKHDF_GROUP: str = 'VTKHDF'
    HDF5_REQUIRED_ATTRIBUTES: Set[str] = {'Type'}

    # Polydata topology sections
    POLYDATA_TOPOLOGY_SECTIONS: Dict[str, str] = {
        'Vertices': 'verts',
        'Lines': 'lines',
        'Strips': 'strips',
        'Polygons': 'polys',
        'Polys': 'polys'  # Handle both naming conventions
    }

    # Grid attributes for ImageData
    IMAGE_DATA_ATTRIBUTES: Set[str] = {
        'WholeExtent', 'Origin', 'Spacing', 'Direction'
    }

    # Coordinate names for RectilinearGrid
    RECTILINEAR_COORDINATES: Set[str] = {'XCoordinates', 'YCoordinates', 'ZCoordinates'}

    # Point array common names (in order of preference)
    POINT_ARRAY_NAMES: list = ['Points', 'Coordinates', 'points', 'coordinates']

    # Connectivity array names
    CONNECTIVITY_ARRAY_NAMES: Dict[str, str] = {
        'connectivity': 'connectivity',
        'offsets': 'offsets',
        'types': 'types'
    }

    # Compression type mapping - centralizes compression constants
    SUPPORTED_COMPRESSION_TYPES = {
        'none': 'none',
        'zlib': 'zlib',
        'gzip': 'zlib',  # HDF5 gzip maps to zlib
        'lzma': 'lzma',
        'xz': 'lzma',  # XZ maps to lzma
        'lz4': 'lz4'
    }

    # Default compression settings
    DEFAULT_COMPRESSION_TYPE = 'zlib'
    MAX_DECOMPRESSION_MEMORY_MB = 1024  # 1GB default limit

    # VTK-specific compression block size (typical default)
    DEFAULT_COMPRESSION_BLOCK_SIZE = 32768

    # Logging configuration
    DEFAULT_LOG_LEVEL: int = logging.INFO
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Performance settings
    CHUNK_SIZE: int = 8192  # For reading large files in chunks
    MAX_MEMORY_USAGE_MB: int = 1024  # Maximum memory usage before warnings

    # Validation settings
    VALIDATE_TOPOLOGY: bool = True
    VALIDATE_DATA_CONSISTENCY: bool = True

    # Error handling settings
    STRICT_VALIDATION: bool = False  # If True, fail on any validation errors
    CONTINUE_ON_DATA_ERRORS: bool = True  # Continue reading even if some data arrays fail

    @classmethod
    def get_reader_class_for_extension(cls, file_path: Path) -> str:
        """
        Get the appropriate reader class name for a file extension.

        Parameters
        ----------
        file_path : Path
            Path to the file

        Returns
        -------
        str
            Name of the reader class to use

        Raises
        ------
        ValueError
            If file extension is not supported
        """
        suffix = file_path.suffix.lower()

        if suffix in cls.SUPPORTED_XML_EXTENSIONS:
            return 'UnifiedXMLReader'
        elif suffix in cls.SUPPORTED_HDF5_EXTENSIONS:
            return 'UnifiedHDF5Reader'
        else:
            raise ValueError(f"Unsupported file extension: {suffix}")

    @classmethod
    def get_vtk_type_from_extension(cls, file_path: Path) -> str:
        """
        Guess VTK type from file extension.

        This is a fallback when type cannot be read from file.
        """
        extension_to_type = {
            '.vti': 'ImageData',
            '.vtr': 'RectilinearGrid',
            '.vts': 'StructuredGrid',
            '.vtu': 'UnstructuredGrid',
            '.vtp': 'PolyData'
        }

        return extension_to_type.get(file_path.suffix.lower(), 'Unknown')

    @classmethod
    def validate_vtk_type(cls, vtk_type: str) -> bool:
        """Check if VTK type is supported."""
        return vtk_type in cls.SUPPORTED_VTK_TYPES

    @classmethod
    def get_numpy_dtype(cls, xml_type_string: str) -> Any:
        """Convert XML type string to numpy dtype."""
        return cls.XML_TYPE_MAPPING.get(xml_type_string.lower(), None)

    @classmethod
    def validate_compression_type(cls, compression_type: str) -> bool:
        """Validate if compression type is supported."""
        return compression_type.lower() in cls.SUPPORTED_COMPRESSION_TYPES

    @classmethod
    def normalize_compression_type(cls, compression_type: str) -> str:
        """Normalize compression type name to standard form."""
        normalized = compression_type.lower()
        return cls.SUPPORTED_COMPRESSION_TYPES.get(normalized, 'none')

    @classmethod
    def get_supported_extensions_for_compression(cls) -> set:
        """Get all file extensions that may contain compressed data."""
        return cls.SUPPORTED_HDF5_EXTENSIONS | cls.SUPPORTED_XML_EXTENSIONS

    @classmethod
    def setup_logging(cls, level: int = None, format_str: str = None) -> logging.Logger:
        """Set up logging with standard configuration."""
        level = level or cls.DEFAULT_LOG_LEVEL
        format_str = format_str or cls.LOG_FORMAT

        logging.basicConfig(level=level, format=format_str)
        logger = logging.getLogger('vtk_reader')
        return logger

    @classmethod
    def get_supported_data_types(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get supported VTK data types with their parser information.

        Returns
        -------
        Dict[str, Dict[str, Any]]
            Dictionary mapping VTK type names to parser information
        """
        return {
            'UnstructuredGrid': {
                'required_sections': cls.REQUIRED_DATA_SECTIONS['UnstructuredGrid'],
                'parser_method': '_parse_unstructured_grid',
                'description': 'Unstructured grid with arbitrary connectivity'
            },
            'PolyData': {
                'required_sections': cls.REQUIRED_DATA_SECTIONS['PolyData'],
                'parser_method': '_parse_polydata',
                'description': 'Polygonal data (vertices, lines, polygons, triangle strips)'
            },
            'ImageData': {
                'required_sections': cls.REQUIRED_DATA_SECTIONS['ImageData'],
                'parser_method': '_parse_image_data',
                'description': 'Regular grid with uniform spacing'
            },
            'StructuredGrid': {
                'required_sections': cls.REQUIRED_DATA_SECTIONS['StructuredGrid'],
                'parser_method': '_parse_structured_grid',
                'description': 'Structured grid with arbitrary point positions'
            },
            'RectilinearGrid': {
                'required_sections': cls.REQUIRED_DATA_SECTIONS['RectilinearGrid'],
                'parser_method': '_parse_rectilinear_grid',
                'description': 'Grid with separate coordinate arrays'
            }
        }

    @classmethod
    def get_required_sections_for_type(cls, vtk_type: str) -> Set[str]:
        """
        Get required data sections for a specific VTK type.

        Parameters
        ----------
        vtk_type : str
            VTK data type name

        Returns
        -------
        Set[str]
            Set of required section names
        """
        return cls.REQUIRED_DATA_SECTIONS.get(vtk_type, set())

    @classmethod
    def get_parser_method_for_type(cls, vtk_type: str) -> str:
        """
        Get the parser method name for a VTK type.

        Parameters
        ----------
        vtk_type : str
            VTK data type name

        Returns
        -------
        str
            Name of the parser method

        Raises
        ------
        ValueError
            If VTK type is not supported
        """
        supported_types = cls.get_supported_data_types()
        if vtk_type not in supported_types:
            raise ValueError(f"Unsupported VTK type: {vtk_type}")

        return supported_types[vtk_type]['parser_method']

    @classmethod
    def is_xml_extension(cls, extension: str) -> bool:
        """Check if extension is a supported XML format."""
        return extension.lower() in cls.SUPPORTED_XML_EXTENSIONS

    @classmethod
    def is_hdf5_extension(cls, extension: str) -> bool:
        """Check if extension is a supported HDF5 format."""
        return extension.lower() in cls.SUPPORTED_HDF5_EXTENSIONS

    @classmethod
    def get_all_supported_extensions(cls) -> Set[str]:
        """Get all supported file extensions."""
        return cls.SUPPORTED_XML_EXTENSIONS | cls.SUPPORTED_HDF5_EXTENSIONS


class ReaderSettings:
    """Runtime settings for VTK readers that can be customized per read operation."""

    def __init__(self,
                 validate_topology: bool = None,
                 validate_data_consistency: bool = None,
                 strict_validation: bool = None,
                 continue_on_data_errors: bool = None,
                 max_memory_usage_mb: int = None,
                 chunk_size: int = None):
        """
        Initialize reader settings.

        Parameters that are None will use the defaults from VTKConfig.
        """
        self.validate_topology = validate_topology if validate_topology is not None else VTKConfig.VALIDATE_TOPOLOGY
        self.validate_data_consistency = validate_data_consistency if validate_data_consistency is not None else VTKConfig.VALIDATE_DATA_CONSISTENCY
        self.strict_validation = strict_validation if strict_validation is not None else VTKConfig.STRICT_VALIDATION
        self.continue_on_data_errors = continue_on_data_errors if continue_on_data_errors is not None else VTKConfig.CONTINUE_ON_DATA_ERRORS
        self.max_memory_usage_mb = max_memory_usage_mb if max_memory_usage_mb is not None else VTKConfig.MAX_MEMORY_USAGE_MB
        self.chunk_size = chunk_size if chunk_size is not None else VTKConfig.CHUNK_SIZE

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary for logging/debugging."""
        return {
            'validate_topology': self.validate_topology,
            'validate_data_consistency': self.validate_data_consistency,
            'strict_validation': self.strict_validation,
            'continue_on_data_errors': self.continue_on_data_errors,
            'max_memory_usage_mb': self.max_memory_usage_mb,
            'chunk_size': self.chunk_size
        }


# Convenience functions for common configurations
def create_performance_settings() -> ReaderSettings:
    """Create settings optimised for performance (less validation)."""
    return ReaderSettings(
        validate_topology=False,
        validate_data_consistency=False,
        strict_validation=False,
        continue_on_data_errors=True,
        chunk_size=16384  # Larger chunks
    )


def create_strict_settings() -> ReaderSettings:
    """Create settings optimised for data integrity (more validation)."""
    return ReaderSettings(
        validate_topology=True,
        validate_data_consistency=True,
        strict_validation=True,
        continue_on_data_errors=False
    )


def create_default_settings() -> ReaderSettings:
    """Create default balanced settings."""
    return ReaderSettings()  # Uses all defaults from VTKConfig
