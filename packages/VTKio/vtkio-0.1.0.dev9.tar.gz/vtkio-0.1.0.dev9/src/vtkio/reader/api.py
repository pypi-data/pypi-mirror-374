#!/usr/bin/env python
"""
Unified public API that brings everything together.

This shows how the config class, error handling, base patterns,
and concrete readers all work together in practice.
"""

from pathlib import Path
from typing import Union, Optional
import logging

from .base_reader import BaseVTKReader
from ..config import VTKConfig, ReaderSettings, create_default_settings
from .compression import CompressionSettings
from .exceptions import VTKReaderError, UnsupportedFormatError
from .readers import EnhancedHDF5Reader, EnhancedXMLReader


class VTKReaderFactory:
    """
    Factory for creating appropriate VTK readers based on file type.

    This demonstrates how the config class is used throughout the system.
    """

    def __init__(self, settings: Optional[ReaderSettings] = None,
                 compression_settings: Optional[CompressionSettings] = None):
        """
        Initialise factory with optional custom settings.

        Parameters
        ----------
        settings : ReaderSettings, optional
            Custom reader settings. If None, uses defaults from VTKConfig.
        """
        self.settings = settings or create_default_settings()
        self.logger = VTKConfig.setup_logging()

        # Cache reader classes to avoid repeated imports
        self._reader_classes = {
            'UnifiedXMLReader': EnhancedXMLReader,
            'UnifiedHDF5Reader': EnhancedHDF5Reader
        }

    def create_reader(self, file_path: Union[str, Path]) -> 'BaseVTKReader':
        """
        Create appropriate reader for the given file.

        Uses VTKConfig to determine the correct reader type.
        """
        file_path = Path(file_path)

        try:
            # Use config to determine reader class
            reader_class_name = VTKConfig.get_reader_class_for_extension(file_path)
            reader_class = self._reader_classes[reader_class_name]

            self.logger.info(f"Creating {reader_class_name} for {file_path}")

            # Create reader with settings
            if reader_class_name == 'UnifiedXMLReader':
                return reader_class(file_path, encoding=VTKConfig.DEFAULT_ENCODING)
            else:
                return reader_class(file_path)

        except KeyError as e:
            raise UnsupportedFormatError(f"No reader available for {file_path}: {e}")
        except Exception as e:
            self.logger.error(f"Failed to create reader for {file_path}: {e}")
            raise VTKReaderError(f"Reader creation failed: {e}") from e

    def read_file(self, file_path: Union[str, Path]):
        """
        Read VTK file using appropriate reader.

        This is the main entry point that replaces your original functions.
        """
        reader = self.create_reader(file_path)

        # Apply settings to reader (if the reader supports it)
        if hasattr(reader, 'apply_settings'):
            reader.apply_settings(self.settings)

        return reader.parse()


# Convenience functions for the public API
def load_vtk_data(file_path: Union[str, Path],
                  settings: Optional[ReaderSettings] = None):
    """
    Load VTK data from any supported format.

    This replaces both read_vtkhdf_data() and read_vtkxml_data() functions.

    Parameters
    ----------
    file_path : Union[str, Path]
        Path to VTK file (XML or HDF5)
    settings : ReaderSettings, optional
        Custom reader settings

    Returns
    -------
    VTK data structure (ImageData, PolyData, etc.)

    Examples
    --------
    # Basic usage (uses config defaults)
    >>> data = load_vtk_data('mesh.vtu')

    # With custom settings
    >>> settings = ReaderSettings(validate_topology=False)
    >>> data = load_vtk_data('large_mesh.vtu', settings=settings)

    # Performance optimised
    >>> from ..config import create_performance_settings
    >>> data = load_vtk_data('huge_file.h5', create_performance_settings())
    """
    factory = VTKReaderFactory(settings)
    return factory.read_file(file_path)


def convert_vtk_format(input_path: Union[str, Path],
                       output_path: Union[str, Path],
                       output_format: str = 'auto',
                       settings: Optional[ReaderSettings] = None):
    """
    Convert between VTK formats.

    Parameters
    ----------
    input_path : Union[str, Path]
        Input VTK file path
    output_path : Union[str, Path]
        Output file path
    output_format : str
        Output format ('xml', 'hdf5', or 'auto' to detect from extension)
    settings : ReaderSettings, optional
        Custom reader settings

    Examples
    --------
    >>> convert_vtk_format('mesh.vtu', 'mesh.h5')  # XML to HDF5
    >>> convert_vtk_format('data.h5', 'data.vti')  # HDF5 to XML
    """
    # Load data using unified API
    data = load_vtk_data(input_path, settings)

    # Determine output format
    output_path = Path(output_path)
    if output_format == 'auto':
        if output_path.suffix.lower() in VTKConfig.SUPPORTED_HDF5_EXTENSIONS:
            output_format = 'hdf5'
        elif output_path.suffix.lower() in VTKConfig.SUPPORTED_XML_EXTENSIONS:
            output_format = 'xml'
        else:
            raise UnsupportedFormatError(f"Cannot determine format for {output_path}")

    # Write data (assumes your VTK structures have write methods)
    if hasattr(data, 'write'):
        data.write(output_path, format=output_format)
    else:
        raise NotImplementedError("Write functionality not yet implemented")


def validate_vtk_file(file_path: Union[str, Path],
                      strict: bool = False) -> dict:
    """
    Validate VTK file without fully loading it.

    Parameters
    ----------
    file_path : Union[str, Path]
        Path to VTK file
    strict : bool
        If True, use strict validation settings

    Returns
    -------
    dict
        Validation results with metadata

    Examples
    --------
    >>> info = validate_vtk_file('mesh.vtu')
    >>> print(f"File type: {info['vtk_type']}")
    >>> print(f"Valid: {info['is_valid']}")
    """
    file_path = Path(file_path)

    validation_settings = ReaderSettings(
        validate_topology=True,
        validate_data_consistency=True,
        strict_validation=strict,
        continue_on_data_errors=not strict
    )

    try:
        factory = VTKReaderFactory(validation_settings)
        reader = factory.create_reader(file_path)

        # Just parse metadata, don't load full data
        reader._load_file_structure()
        vtk_type = reader._get_data_type()

        return {
            'file_path': str(file_path),
            'vtk_type': vtk_type,
            'file_size_mb': file_path.stat().st_size / (1024 * 1024),
            'is_valid': True,
            'reader_type': type(reader).__name__,
            'supported_type': VTKConfig.validate_vtk_type(vtk_type)
        }

    except VTKReaderError as e:
        return {
            'file_path': str(file_path),
            'vtk_type': None,
            'file_size_mb': file_path.stat().st_size / (1024 * 1024) if file_path.exists() else 0,
            'is_valid': False,
            'error': str(e),
            'error_type': type(e).__name__
        }


def get_file_info(file_path: Union[str, Path]) -> dict:
    """
    Get basic information about a VTK file without loading data.

    This is useful for file browsers or data catalogues.

    Parameters
    ----------
    file_path : Union[str, Path]
        Path to VTK file

    Returns
    -------
    dict
        File information

    Examples
    --------
    >>> info = get_file_info('mesh.vtu')
    >>> print(f"Contains {info['estimated_points']} points")
    """
    try:
        validation_result = validate_vtk_file(file_path)

        if validation_result['is_valid']:
            # Get additional metadata without loading arrays
            factory = VTKReaderFactory()
            reader = factory.create_reader(file_path)
            reader._load_file_structure()

            # Extract basic counts/sizes (implementation would depend on reader type)
            # This is a simplified example
            info = validation_result.copy()
            info.update({
                'estimated_points': 'unknown',  # Would extract from metadata
                'estimated_cells': 'unknown',
                'data_arrays': [],  # List of available data arrays
                'has_point_data': False,
                'has_cell_data': False,
                'has_field_data': False
            })

            return info
        else:
            return validation_result

    except Exception as e:
        return {
            'file_path': str(file_path),
            'is_valid': False,
            'error': f"Failed to get file info: {e}"
        }


# Usage examples and backward compatibility
def read_vtkhdf_data(filepath: Union[str, Path]):
    """
    Backward compatible function for HDF5 files.

    This maintains the same interface as your original function
    but uses the new unified system internally.
    """
    import warnings
    warnings.warn(
        "read_vtkhdf_data is deprecated. Use load_vtk_data() instead.",
        DeprecationWarning,
        stacklevel=2
    )

    # Ensure it's an HDF5 file
    file_path = Path(filepath)
    if file_path.suffix.lower() not in VTKConfig.SUPPORTED_HDF5_EXTENSIONS:
        raise UnsupportedFormatError(f"Not an HDF5 file: {filepath}")

    return load_vtk_data(filepath)


def read_vtkxml_data(filename: Union[str, Path]):
    """
    Backward compatible function for XML files.

    This maintains the same interface as your original function.
    """
    import warnings
    warnings.warn(
        "read_vtkxml_data is deprecated. Use load_vtk_data() instead.",
        DeprecationWarning,
        stacklevel=2
    )

    # Ensure it's an XML file
    file_path = Path(filename)
    if file_path.suffix.lower() not in VTKConfig.SUPPORTED_XML_EXTENSIONS:
        raise UnsupportedFormatError(f"Not an XML file: {filename}")

    return load_vtk_data(filename)


# Configuration shortcuts for common use cases
class QuickStart:
    """
    Quick start configurations for common scenarios.

    This demonstrates how the config system makes different use cases easy.
    """

    @staticmethod
    def for_large_files():
        """Settings optimised for large files."""
        from ..config import create_performance_settings
        return create_performance_settings()

    @staticmethod
    def for_data_validation():
        """Settings optimised for data validation and integrity."""
        from ..config import create_strict_settings
        return create_strict_settings()

    @staticmethod
    def for_web_service():
        """Settings optimised for web service usage."""
        return ReaderSettings(
            validate_topology=False,  # Skip expensive validation
            continue_on_data_errors=True,  # Don't fail on missing optional data
            max_memory_usage_mb=512  # Limit memory usage
        )

    @staticmethod
    def for_batch_processing():
        """Settings optimised for batch processing many files."""
        return ReaderSettings(
            validate_topology=False,
            validate_data_consistency=False,
            continue_on_data_errors=True,
            chunk_size=32768  # Larger chunks for throughput
        )


# Example of how this would be used:
"""
# Basic usage - replaces your original functions
data = load_vtk_data('mesh.vtu')  # Works for both XML and HDF5

# Performance optimized for large files
data = load_vtk_data('huge_mesh.h5', QuickStart.for_large_files())

# Strict validation for critical data
data = load_vtk_data('critical_data.vtu', QuickStart.for_data_validation())

# Convert between formats
convert_vtk_format('mesh.vtu', 'mesh.h5')

# Validate file before processing
info = validate_vtk_file('unknown_file.vtk')
if info['is_valid']:
    data = load_vtk_data('unknown_file.vtk')
    print(f"Loaded {info['vtk_type']} with {len(data.points)} points")

# Custom settings for specific use case
custom_settings = ReaderSettings(
    validate_topology=True,
    max_memory_usage_mb=2048,
    continue_on_data_errors=False
)
data = load_vtk_data('my_data.h5', custom_settings)

# Backward compatibility (with deprecation warnings)
data = read_vtkhdf_data('legacy_code.h5')  # Still works
data = read_vtkxml_data('legacy_code.vtu')  # Still works

# File information without loading full data
info = get_file_info('large_dataset.h5')
print(f"File contains {info['vtk_type']} data")
print(f"File size: {info['file_size_mb']:.1f} MB")

# Batch processing with error handling
files_to_process = ['mesh1.vtu', 'mesh2.h5', 'mesh3.vti']
batch_settings = QuickStart.for_batch_processing()

for file_path in files_to_process:
    try:
        data = load_vtk_data(file_path, batch_settings)
        print(f"Successfully processed {file_path}")
        # Process data...
    except VTKReaderError as e:
        print(f"Failed to process {file_path}: {e}")
        continue

# Using the factory directly for more control
factory = VTKReaderFactory(QuickStart.for_web_service())
reader = factory.create_reader('api_data.h5')
data = reader.parse()

# Configuration-driven approach
if VTKConfig.validate_vtk_type('UnstructuredGrid'):
    print("UnstructuredGrid is supported")

# Get reader type without creating reader
reader_type = VTKConfig.get_reader_class_for_extension(Path('test.vtu'))
print(f"Would use: {reader_type}")
"""