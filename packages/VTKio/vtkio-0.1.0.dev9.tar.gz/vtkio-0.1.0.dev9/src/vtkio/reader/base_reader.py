# !/usr/bin/env python
"""
Base reader class that extracts common patterns and implements simplified error handling.

"""

__author__ = 'J.P. Morrissey'
__copyright__ = 'Copyright 2022-2025'
__maintainer__ = 'J.P. Morrissey'
__email__ = 'morrissey.jp@gmail.com'
__status__ = 'Development'

# Standard Library
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, Union
from pathlib import Path
import logging
import base64
import struct
import re

from .exceptions import (
    VTKReaderError, UnsupportedFormatError, InvalidVTKFileError,
    MissingDataError, DataCorruptionError
)
from .data_processors import DataArrayProcessor, VTKDataProcessor
from .compression import (
    CompressionHandler, CompressionType, CompressionSettings,
    CompressedDataProcessor
)
from ..config import VTKConfig

logger = logging.getLogger(__name__)


class BaseVTKReader(ABC):
    """
    Complete base class with compression support and all XML handling methods.
    """

    def __init__(self, file_path: Union[str, Path],
                 compression_settings: Optional[CompressionSettings] = None):
        """Initialize base reader with compression support."""
        self.file_path = Path(file_path)
        self._validate_file()
        self.data_type = None
        self._data_cache = {}

        # Compression support
        self.compression_settings = compression_settings or CompressionSettings()
        self.compression_handler = CompressionHandler()
        self._detected_compression = CompressionType.NONE
        self._compression_processor = None

        # XML-specific attributes (will be None for HDF5 readers)
        self._xml_data = None
        self.appended_data_bstr = None
        self.appended_data_arrays = {}
        self.binary_data_encoding = None
        self.byte_order = 'little'
        self.byte_count_type = 'UInt32'
        self.byte_count_format = None
        self.file_version = 1.0
        self.data_format = None

    def _validate_file(self):
        """Basic file validation."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"File {self.file_path} does not exist")

        if self.file_path.stat().st_size == 0:
            raise InvalidVTKFileError(f"File {self.file_path} is empty")

        # Use config to validate supported formats
        extension = self.file_path.suffix.lower()
        supported_extensions = (VTKConfig.SUPPORTED_XML_EXTENSIONS +
                                VTKConfig.SUPPORTED_HDF5_EXTENSIONS)

        if extension not in supported_extensions:
            raise UnsupportedFormatError(
                f"Unsupported file format: {extension}. "
                f"Supported: {sorted(supported_extensions)}"
            )

    def _setup_compression_processor(self):
        """Initialize compression processor when compression is detected."""
        if self._detected_compression != CompressionType.NONE:
            self._compression_processor = CompressedDataProcessor(self.byte_order)
            logger.debug(f"Initialized compression processor for {self._detected_compression.value}")

    # Abstract methods that subclasses must implement
    @abstractmethod
    def _is_supported_format(self) -> bool:
        """Check if file format is supported by this reader."""
        pass

    @abstractmethod
    def _load_file_structure(self):
        """Load and parse the file structure (XML/HDF5 specific)."""
        pass

    @abstractmethod
    def _detect_compression(self) -> CompressionType:
        """Detect compression type used in the file."""
        pass

    @abstractmethod
    def _get_data_type(self) -> str:
        """Extract the VTK data type from the file."""
        pass

    @abstractmethod
    def _get_source_type(self) -> str:
        """Return the source type ('xml' or 'hdf5') for data processors."""
        pass

    @abstractmethod
    def _extract_raw_data_arrays(self, data_section: str,
                                 decompress: bool = True) -> Optional[Dict]:
        """Extract raw data arrays from a specific section with optional decompression."""
        pass

    @abstractmethod
    def _process_compressed_xml_arrays(self, xml_data: Dict) -> Dict:
        """Process compressed XML data arrays (implemented by XML reader)."""
        pass

    @abstractmethod
    def _process_compressed_hdf5_arrays(self, hdf5_data: Dict) -> Dict:
        """Process compressed HDF5 data arrays (implemented by HDF5 reader)."""
        pass

    # Extraction methods that subclasses must implement
    @abstractmethod
    def _extract_points(self) -> Dict:
        """Extract point coordinates."""
        pass

    @abstractmethod
    def _extract_connectivity(self) -> Dict:
        """Extract connectivity information."""
        pass

    @abstractmethod
    def _extract_polydata_topology(self) -> Dict:
        """Extract polydata topology."""
        pass

    @abstractmethod
    def _extract_image_grid(self):
        """Extract image data grid information."""
        pass

    @abstractmethod
    def _extract_extents(self):
        """Extract grid extents."""
        pass

    @abstractmethod
    def _extract_grid_coordinates(self):
        """Extract rectilinear grid coordinates."""
        pass

    # Core parsing template method
    def parse(self):
        """
        Enhanced template method with compression detection and handling.
        """
        try:
            self._load_file_structure()

            # Detect and setup compression if enabled
            if self.compression_settings.enable_compression:
                self._detected_compression = self._detect_compression()
                if self._detected_compression != CompressionType.NONE:
                    self._setup_compression_processor()
                    logger.info(f"Detected {self._detected_compression.value} compression")

            self.data_type = self._get_data_type()

            # Validate data type using config
            if not VTKConfig.validate_vtk_type(self.data_type):
                logger.warning(f"Data type {self.data_type} may not be fully supported")

            parser = self._get_parser_for_type()
            return parser()

        except VTKReaderError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error parsing {self.file_path}: {e}")
            raise VTKReaderError(f"Failed to parse VTK file: {e}") from e

    def _get_parser_for_type(self) -> Callable:
        """Get parser using config's supported types."""
        parser_mapping = VTKConfig.get_supported_data_types()

        if self.data_type not in parser_mapping:
            supported_types = list(parser_mapping.keys())
            raise UnsupportedFormatError(
                f"Unsupported VTK data type: {self.data_type}. "
                f"Supported: {supported_types}"
            )

        parsers = {
            'UnstructuredGrid': self._parse_unstructured_grid,
            'PolyData': self._parse_polydata,
            'ImageData': self._parse_image_data,
            'StructuredGrid': self._parse_structured_grid,
            'RectilinearGrid': self._parse_rectilinear_grid
        }

        return parsers[self.data_type]

    # XML-specific methods (will be no-ops for HDF5 readers)
    def _parse_invalid_xml_with_binary(self, raw_bytes: bytes) -> Dict:
        """
        Parse XML files that have binary data mixed in (malformed XML).

        This handles cases where XML parsing fails due to binary appended data.
        """
        try:
            # Find the end of the XML part
            xml_end_pattern = b'</VTKFile>'
            xml_end_pos = raw_bytes.find(xml_end_pattern)

            if xml_end_pos == -1:
                raise InvalidVTKFileError("Cannot find end of XML section")

            xml_end_pos += len(xml_end_pattern)
            xml_part = raw_bytes[:xml_end_pos]

            # Parse just the XML part
            import xmltodict
            xml_data = xmltodict.parse(xml_part)['VTKFile']

            # Handle appended data separately
            if xml_end_pos < len(raw_bytes):
                appended_part = raw_bytes[xml_end_pos:]
                self._handle_separated_appended_data(appended_part)

            return xml_data

        except Exception as e:
            raise InvalidVTKFileError(f"Failed to parse malformed XML: {e}")

    def _handle_separated_appended_data(self, appended_bytes: bytes):
        """Handle appended data that was separated from XML."""
        # Look for AppendedData marker
        appended_marker = b'<AppendedData'
        marker_pos = appended_bytes.find(appended_marker)

        if marker_pos != -1:
            # Extract encoding information
            encoding_pattern = rb'encoding="([^"]+)"'
            encoding_match = re.search(encoding_pattern, appended_bytes[marker_pos:marker_pos + 100])

            if encoding_match:
                self.binary_data_encoding = encoding_match.group(1).decode('utf-8')

            # Find the actual data (after the underscore marker)
            data_start = appended_bytes.find(b'_', marker_pos)
            if data_start != -1:
                self.appended_data_bstr = appended_bytes[data_start + 1:].decode('latin1')

    def _handle_appended_data(self):
        """Handle appended data from valid XML structure."""
        try:
            appended = self._xml_data.get('AppendedData', {})
            if appended:
                self.appended_data_bstr = appended.get('#text', '').strip('_')
                self.binary_data_encoding = appended.get('@encoding')

                if self.appended_data_bstr:
                    self._process_appended_data_with_compression()

        except Exception as e:
            logger.warning(f"Error processing appended data: {e}")

    def _process_appended_data_with_compression(self):
        """Process appended data with compression support."""
        if not self.appended_data_bstr:
            return

        try:
            # Get offset information from XML
            from ..utilities import get_recursively
            offset_keys = get_recursively(
                self._xml_data[self.data_type]['Piece'], '@offset'
            )

            if self.binary_data_encoding == 'base64':
                self._process_base64_appended_data(offset_keys)
            elif self.binary_data_encoding == 'raw':
                self._process_raw_appended_data(offset_keys)

            # Apply decompression if compression was detected
            if (self._detected_compression != CompressionType.NONE and
                    self.compression_settings.enable_compression):
                self._decompress_appended_arrays()

        except Exception as e:
            logger.warning(f"Error processing appended data: {e}")

    def _process_base64_appended_data(self, offset_keys: list):
        """Process base64 encoded appended data."""
        try:
            # Decode base64 data
            decoded_data = base64.b64decode(self.appended_data_bstr)

            # Split data by offsets
            self._split_appended_data_by_offsets(decoded_data, offset_keys)

        except Exception as e:
            logger.error(f"Error processing base64 appended data: {e}")
            raise DataCorruptionError(f"Invalid base64 appended data: {e}")

    def _process_raw_appended_data(self, offset_keys: list):
        """Process raw binary appended data."""
        try:
            # Convert string back to bytes (assuming latin1 encoding was used)
            raw_data = self.appended_data_bstr.encode('latin1')

            # Split data by offsets
            self._split_appended_data_by_offsets(raw_data, offset_keys)

        except Exception as e:
            logger.error(f"Error processing raw appended data: {e}")
            raise DataCorruptionError(f"Invalid raw appended data: {e}")

    def _split_appended_data_by_offsets(self, data: bytes, offset_keys: list):
        """Split appended data into arrays based on offsets."""
        self.appended_data_arrays = {}

        # Sort offsets to process in order
        sorted_offsets = sorted(set(int(offset) for offset in offset_keys))

        for i, offset in enumerate(sorted_offsets):
            try:
                # Determine the size of this data block
                if i < len(sorted_offsets) - 1:
                    next_offset = sorted_offsets[i + 1]
                    # Read size header
                    size_data = data[offset:offset + struct.calcsize(self.byte_count_format)]
                    if len(size_data) < struct.calcsize(self.byte_count_format):
                        logger.warning(f"Insufficient data for size header at offset {offset}")
                        continue

                    array_size = struct.unpack(self.byte_count_format, size_data)[0]
                    start_pos = offset + struct.calcsize(self.byte_count_format)
                    end_pos = min(start_pos + array_size, next_offset)
                else:
                    # Last array - read size header and use it
                    size_data = data[offset:offset + struct.calcsize(self.byte_count_format)]
                    if len(size_data) < struct.calcsize(self.byte_count_format):
                        logger.warning(f"Insufficient data for size header at offset {offset}")
                        continue

                    array_size = struct.unpack(self.byte_count_format, size_data)[0]
                    start_pos = offset + struct.calcsize(self.byte_count_format)
                    end_pos = start_pos + array_size

                # Extract the array data
                if end_pos <= len(data):
                    array_data = data[start_pos:end_pos]
                    self.appended_data_arrays[offset] = array_data
                else:
                    logger.warning(f"Array at offset {offset} extends beyond data bounds")

            except Exception as e:
                logger.warning(f"Error processing array at offset {offset}: {e}")

    def _decompress_appended_arrays(self):
        """Decompress all appended arrays using the compression processor."""
        if not self._compression_processor:
            logger.warning("No compression processor available")
            return

        decompressed_arrays = {}

        for offset, compressed_data in self.appended_data_arrays.items():
            try:
                # Estimate decompressed size for memory check
                estimated_size = self._estimate_decompressed_size(
                    compressed_data, self._detected_compression
                )
                self._check_memory_limits(estimated_size)

                # Decompress using compression processor
                decompressed = self._compression_processor.process_compressed_array(
                    compressed_data,
                    {'type': self._detected_compression.value}
                )

                decompressed_arrays[offset] = decompressed
                logger.debug(f"Decompressed array at offset {offset}: "
                             f"{len(compressed_data)} -> {len(decompressed)} bytes")

            except Exception as e:
                logger.warning(f"Failed to decompress array at offset {offset}: {e}")
                # Keep original data as fallback
                decompressed_arrays[offset] = compressed_data

        self.appended_data_arrays = decompressed_arrays

    # Helper methods for compression detection and handling
    def _detect_compression_from_string(self, compression_str: str) -> CompressionType:
        """Helper to detect compression using config validation."""
        if not compression_str:
            return CompressionType.NONE

        if VTKConfig.validate_compression_type(compression_str):
            return CompressionType.from_string(compression_str)
        else:
            logger.warning(f"Unknown compression type '{compression_str}', assuming no compression")
            return CompressionType.NONE

    def _check_memory_limits(self, estimated_size: int):
        """Check if decompression would exceed memory limits."""
        max_memory = self.compression_settings.max_memory_mb * 1024 * 1024

        if estimated_size > max_memory:
            raise MemoryError(
                f"Estimated decompressed size ({estimated_size} bytes) exceeds "
                f"maximum allowed memory ({max_memory} bytes)"
            )

    def _estimate_decompressed_size(self, compressed_data: bytes,
                                    compression_type: CompressionType) -> int:
        """Estimate decompressed size for memory planning."""
        ratios = {
            CompressionType.ZLIB: 3.0,
            CompressionType.LZMA: 4.0,
            CompressionType.LZ4: 2.5,
            CompressionType.NONE: 1.0
        }

        ratio = ratios.get(compression_type, 2.0)
        return int(len(compressed_data) * ratio)

    # Enhanced data extraction with compression support
    def _safe_extract_data_arrays(self, data_section: str) -> Optional[Dict]:
        """Enhanced data array extraction with compression support."""
        try:
            # Extract raw data with compression handling
            raw_data = self._extract_raw_data_arrays(
                data_section,
                decompress=self.compression_settings.enable_compression
            )

            if raw_data is None:
                logger.debug(f"No {data_section} found")
                return None

            # Process data arrays (handles both compressed and uncompressed)
            processed_data = self._process_data_arrays_with_compression(
                raw_data, data_section
            )

            if processed_data:
                self._data_cache[data_section] = processed_data

            return processed_data

        except Exception as e:
            logger.warning(f"Error extracting {data_section}: {e}")
            return None

    def _process_data_arrays_with_compression(self, raw_data: Dict,
                                              data_section: str) -> Optional[Dict]:
        """Process data arrays with compression awareness."""
        try:
            # If no compression detected, use standard processing
            if self._detected_compression == CompressionType.NONE:
                return DataArrayProcessor.process_data_arrays(
                    raw_data, self._get_source_type()
                )

            # Handle compressed data
            return self._process_compressed_data_arrays(raw_data, data_section)

        except Exception as e:
            logger.warning(f"Error processing {data_section} arrays: {e}")
            return None

    def _process_compressed_data_arrays(self, raw_data: Dict,
                                        data_section: str) -> Optional[Dict]:
        """Process compressed data arrays using compression processor."""
        if not self._compression_processor:
            logger.warning("No compression processor available")
            return None

        # Handle different raw data formats (XML vs HDF5)
        if self._get_source_type() == 'xml':
            return self._process_compressed_xml_arrays(raw_data)
        else:  # HDF5
            return self._process_compressed_hdf5_arrays(raw_data)

    # Generic parsing method with compression support
    def _parse_with_standard_pattern(self,
                                     topology_extractor: Callable,
                                     data_processor: Callable,
                                     required_data: Optional[list] = None) -> Any:
        """Enhanced generic parsing method with compression support."""
        try:
            # Step 1: Extract topology/geometry (may involve decompression)
            topology_data = topology_extractor()

            # Step 2: Extract data arrays with compression handling
            point_data = self._safe_extract_data_arrays('PointData')
            cell_data = self._safe_extract_data_arrays('CellData')
            field_data = self._safe_extract_data_arrays('FieldData')

            # Step 3: Validate required data
            if required_data:
                self._validate_required_data(topology_data, required_data)

            # Step 4: Create VTK structure
            return data_processor(
                topology_data=topology_data,
                point_data=point_data,
                cell_data=cell_data,
                field_data=field_data
            )

        except VTKReaderError:
            raise
        except Exception as e:
            logger.error(f"Error in standard parsing pattern: {e}")
            raise DataCorruptionError(f"Data corruption detected: {e}") from e

    def _validate_required_data(self, topology_data: Dict, required_fields: list):
        """Validate that required data fields are present."""
        missing_fields = []

        for field in required_fields:
            if field not in topology_data or topology_data[field] is None:
                missing_fields.append(field)

        if missing_fields:
            raise MissingDataError(
                f"Missing required fields: {', '.join(missing_fields)}"
            )

    # Concrete parsing methods using the standard pattern
    def _parse_unstructured_grid(self):
        """Parse unstructured grid using standard pattern with compression support."""

        def extract_topology():
            try:
                points_data = self._extract_points()
                connectivity_data = self._extract_connectivity()

                return {
                    'points': points_data['points'],
                    'connectivity': connectivity_data['connectivity'],
                    'offsets': connectivity_data['offsets'],
                    'types': connectivity_data['types']
                }
            except Exception as e:
                raise MissingDataError(f"Failed to extract unstructured grid topology: {e}")

        def create_structure(topology_data, point_data, cell_data, field_data):
            return VTKDataProcessor.create_unstructured_grid(
                points=topology_data['points'],
                connectivity=topology_data['connectivity'],
                offsets=topology_data['offsets'],
                types=topology_data['types'],
                point_data=point_data,
                cell_data=cell_data,
                field_data=field_data
            )

        return self._parse_with_standard_pattern(
            topology_extractor=extract_topology,
            data_processor=create_structure,
            required_data=['points', 'connectivity', 'offsets', 'types']
        )

    def _parse_polydata(self):
        """Parse polydata using standard pattern with compression support."""

        def extract_topology():
            try:
                points_data = self._extract_points()
                topology_data = self._extract_polydata_topology()

                return {
                    'points': points_data['points'],
                    'verts': topology_data.get('verts'),
                    'lines': topology_data.get('lines'),
                    'strips': topology_data.get('strips'),
                    'polys': topology_data.get('polys')
                }
            except Exception as e:
                raise MissingDataError(f"Failed to extract polydata topology: {e}")

        def create_structure(topology_data, point_data, cell_data, field_data):
            return VTKDataProcessor.create_polydata(
                points=topology_data['points'],
                verts=topology_data['verts'],
                lines=topology_data['lines'],
                strips=topology_data['strips'],
                polys=topology_data['polys'],
                point_data=point_data,
                cell_data=cell_data,
                field_data=field_data
            )

        return self._parse_with_standard_pattern(
            topology_extractor=extract_topology,
            data_processor=create_structure,
            required_data=['points']
        )

    def _parse_image_data(self):
        """Parse image data using standard pattern with compression support."""

        def extract_topology():
            try:
                return {'grid': self._extract_image_grid()}
            except Exception as e:
                raise MissingDataError(f"Failed to extract image grid: {e}")

        def create_structure(topology_data, point_data, cell_data, field_data):
            return VTKDataProcessor.create_image_data(
                grid_topology=topology_data['grid'],
                point_data=point_data,
                cell_data=cell_data,
                field_data=field_data
            )

        return self._parse_with_standard_pattern(
            topology_extractor=extract_topology,
            data_processor=create_structure,
            required_data=['grid']
        )

    def _parse_structured_grid(self):
        """Parse structured grid using standard pattern with compression support."""

        def extract_topology():
            try:
                points_data = self._extract_points()
                extents = self._extract_extents()

                return {
                    'points': points_data['points'],
                    'whole_extents': extents
                }
            except Exception as e:
                raise MissingDataError(f"Failed to extract structured grid topology: {e}")

        def create_structure(topology_data, point_data, cell_data, field_data):
            return VTKDataProcessor.create_structured_data(
                points=topology_data['points'],
                whole_extents=topology_data['whole_extents'],
                point_data=point_data,
                cell_data=cell_data,
                field_data=field_data
            )

        return self._parse_with_standard_pattern(
            topology_extractor=extract_topology,
            data_processor=create_structure,
            required_data=['points', 'whole_extents']
        )

    def _parse_rectilinear_grid(self):
        """Parse rectilinear grid using standard pattern with compression support."""

        def extract_topology():
            try:
                return {'coordinates': self._extract_grid_coordinates()}
            except Exception as e:
                raise MissingDataError(f"Failed to extract rectilinear coordinates: {e}")

        def create_structure(topology_data, point_data, cell_data, field_data):
            return VTKDataProcessor.create_rectilinear_data(
                coordinates=topology_data['coordinates'],
                point_data=point_data,
                cell_data=cell_data,
                field_data=field_data
            )

        return self._parse_with_standard_pattern(
            topology_extractor=extract_topology,
            data_processor=create_structure,
            required_data=['coordinates']
        )


# Enhanced error handling decorator
def handle_vtk_errors_with_compression(func):
    """Enhanced decorator that provides compression-aware error handling."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except VTKReaderError:
            # Re-raise our custom exceptions
            raise
        except MemoryError as e:
            raise VTKReaderError(f"Memory error during decompression: {e}")
        except ValueError as e:
            if "compression" in str(e).lower():
                raise DataCorruptionError(f"Compression error: {e}")
            raise VTKReaderError(f"Value error: {e}")
        except FileNotFoundError as e:
            raise InvalidVTKFileError(f"File not found: {e}")
        except PermissionError as e:
            raise VTKReaderError(f"Permission denied: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise VTKReaderError(f"Unexpected error: {e}") from e

    return wrapper