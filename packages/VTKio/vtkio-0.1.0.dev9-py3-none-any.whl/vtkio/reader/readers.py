#!/usr/bin/env python
"""
Concrete implementations of HDF5 and XML readers using the base class pattern.

This shows how the simplified error handling and extracted common patterns
work in practice.
"""
__author__ = 'J.P. Morrissey'
__copyright__ = 'Copyright 2022-2025'
__maintainer__ = 'J.P. Morrissey'
__email__ = 'morrissey.jp@gmail.com'
__status__ = 'Development'

import struct

# Standard Library
import h5py
from typing import Dict, Any, Optional, Union
from pathlib import Path
import logging
import numpy as np
import pybase64
import xmltodict

from .base_reader import BaseVTKReader, handle_vtk_errors_with_compression
from .exceptions import InvalidVTKFileError, MissingDataError, DataCorruptionError, UnsupportedFormatError
from .compression import CompressionType
from .data_processors import (
    DataArrayProcessor, PolyDataTopologyProcessor, GridTopologyProcessor,
    determine_points_key, safe_get_hdf5_attr
)
from ..config import VTKConfig
from ..helpers import _parse_bytecount_type
from ..utilities import dict_extract_generator, get_recursively
from ..vtk_structures import PolyDataTopology, Grid, GridCoordinates

logger = logging.getLogger(__name__)


class UnifiedHDF5Reader(BaseVTKReader):
    """HDF5 reader with built-in compression support."""

    def __init__(self, file_path: Union[str, Path], compression_settings=None):
        extension = Path(file_path).suffix.lower()
        if extension not in VTKConfig.SUPPORTED_HDF5_EXTENSIONS:
            raise UnsupportedFormatError(f"Not an HDF5 file: {extension}")

        super().__init__(file_path, compression_settings)
        self._hdf5_file = None
        self._vtkhdf_group = None
        self._compression_info = {}

    def _is_supported_format(self) -> bool:
        return Path(self.file_path).suffix.lower() in VTKConfig.SUPPORTED_HDF5_EXTENSIONS

    def _detect_compression(self) -> CompressionType:
        """Detect compression in HDF5 datasets."""
        if not self._compression_info:
            return CompressionType.NONE

        # Get compression types from HDF5 datasets
        compression_types = {info['type'] for info in self._compression_info.values()}

        for hdf5_compression in compression_types:
            normalized = VTKConfig.normalize_compression_type(hdf5_compression)
            if normalized != 'none':
                return CompressionType(normalized)

        return CompressionType.NONE

    @handle_vtk_errors_with_compression
    def _load_file_structure(self):
        """Load HDF5 structure and detect compression."""
        try:
            self._hdf5_file = h5py.File(self.file_path, 'r')

            if 'VTKHDF' not in self._hdf5_file:
                raise InvalidVTKFileError("File does not contain VTKHDF group")

            self._vtkhdf_group = self._hdf5_file['VTKHDF']
            self._scan_compression()

        except OSError as e:
            raise InvalidVTKFileError(f"Cannot open HDF5 file: {e}")

    def _scan_compression(self):
        """Scan for compression in HDF5 datasets."""

        def scan_group(group, path=""):
            for name, item in group.items():
                full_path = f"{path}/{name}" if path else name

                if isinstance(item, h5py.Dataset) and item.compression:
                    self._compression_info[full_path] = {
                        'type': item.compression,
                        'opts': getattr(item, 'compression_opts', None),
                        'shape': item.shape,
                        'dtype': item.dtype
                    }
                    logger.debug(f"Dataset {full_path} uses {item.compression} compression")
                elif isinstance(item, h5py.Group):
                    scan_group(item, full_path)

        scan_group(self._vtkhdf_group)

    def _get_data_type(self) -> str:
        data_type = safe_get_hdf5_attr(self._vtkhdf_group, 'Type')
        if not data_type:
            raise MissingDataError("Missing 'Type' attribute")
        if isinstance(data_type, bytes):
            data_type = data_type.decode('utf-8')
        return data_type

    def _get_source_type(self) -> str:
        return 'hdf5'

    @handle_vtk_errors_with_compression
    def _extract_raw_data_arrays(self, data_section: str, decompress: bool = True) -> Optional[Dict]:
        """Extract HDF5 data arrays (decompression handled transparently by h5py)."""
        try:
            if data_section in self._vtkhdf_group:
                return self._vtkhdf_group[data_section]
            return None
        except Exception as e:
            logger.warning(f"Error accessing {data_section}: {e}")
            return None

    def _process_compressed_xml_arrays(self, xml_data: Dict) -> Dict:
        """Not applicable for HDF5 reader."""
        return {}

    def _process_compressed_hdf5_arrays(self, hdf5_data: Dict) -> Optional[Dict]:
        """Process HDF5 data with compression awareness."""
        compression_context = {
            'compression_processor': self._compression_processor,
            'compression_info': self._compression_info
        }

        return DataArrayProcessor.process_data_arrays(
            hdf5_data, 'hdf5', compression_context
        )

    @handle_vtk_errors_with_compression
    def _extract_points(self) -> Dict:
        """Extract points from HDF5."""
        try:
            points = self._vtkhdf_group['Points'][:]
            return {'points': points}
        except KeyError:
            raise MissingDataError("Points dataset not found")
        except Exception as e:
            raise DataCorruptionError(f"Corrupted points data: {e}")

    @handle_vtk_errors_with_compression
    def _extract_connectivity(self) -> Dict:
        """Extract connectivity data from HDF5."""
        try:
            return {
                'connectivity': self._vtkhdf_group['Connectivity'][:],
                'offsets': self._vtkhdf_group['Offsets'][1:],  # Skip first zero
                'types': self._vtkhdf_group['Types'][:]
            }
        except KeyError as e:
            raise MissingDataError(f"Missing connectivity data: {e}")
        except Exception as e:
            raise DataCorruptionError(f"Corrupted connectivity data: {e}")

    @handle_vtk_errors_with_compression
    def _extract_polydata_topology(self) -> Dict:
        """Extract polydata topology from HDF5."""
        topology = {}

        # Check each polydata topology section
        for section_name, vtk_name in VTKConfig.POLYDATA_TOPOLOGY_SECTIONS.items():
            if section_name in self._vtkhdf_group:
                topology_obj = PolyDataTopologyProcessor.process_hdf5_topology(
                    self._vtkhdf_group, section_name
                )
                if topology_obj:
                    topology[vtk_name] = topology_obj

        return topology

    @handle_vtk_errors_with_compression
    def _extract_image_grid(self) -> Grid:
        """Extract image data grid from HDF5 attributes."""
        try:
            whole_extents = safe_get_hdf5_attr(self._vtkhdf_group, 'WholeExtent')
            origin = safe_get_hdf5_attr(self._vtkhdf_group, 'Origin')
            spacing = safe_get_hdf5_attr(self._vtkhdf_group, 'Spacing')
            direction = safe_get_hdf5_attr(self._vtkhdf_group, 'Direction')

            if whole_extents is None or origin is None or spacing is None:
                raise MissingDataError("Missing required grid attributes")

            return GridTopologyProcessor.create_grid_from_attributes(
                whole_extents, origin, spacing, direction
            )

        except Exception as e:
            raise DataCorruptionError(f"Invalid image grid data: {e}")

    @handle_vtk_errors_with_compression
    def _extract_extents(self) -> np.ndarray:
        """Extract extents for structured grid from HDF5."""
        try:
            extents = safe_get_hdf5_attr(self._vtkhdf_group, 'WholeExtent')
            if extents is None:
                raise MissingDataError("WholeExtent attribute not found")

            if isinstance(extents, str):
                extents = np.fromstring(extents, dtype=int, sep=' ')

            return extents

        except Exception as e:
            raise DataCorruptionError(f"Invalid extents data: {e}")

    @handle_vtk_errors_with_compression
    def _extract_grid_coordinates(self) -> GridCoordinates:
        """Extract rectilinear grid coordinates from HDF5."""
        try:
            x_coords = self._vtkhdf_group['XCoordinates'][:]
            y_coords = self._vtkhdf_group['YCoordinates'][:]
            z_coords = self._vtkhdf_group['ZCoordinates'][:]

            whole_extents = safe_get_hdf5_attr(self._vtkhdf_group, 'WholeExtent')
            if whole_extents is None:
                # Calculate extents from coordinate arrays
                whole_extents = np.array([
                    0, len(x_coords) - 1,
                    0, len(y_coords) - 1,
                    0, len(z_coords) - 1
                ])

            return GridTopologyProcessor.create_grid_coordinates(
                x_coords, y_coords, z_coords, whole_extents
            )

        except KeyError as e:
            raise MissingDataError(f"Missing coordinate data: {e}")
        except Exception as e:
            raise DataCorruptionError(f"Invalid coordinate data: {e}")

    def __del__(self):
        """Cleanup HDF5 file handle."""
        if hasattr(self, '_hdf5_file') and self._hdf5_file:
            try:
                self._hdf5_file.close()
            except:
                pass


class UnifiedXMLReader(BaseVTKReader):
    """XML reader with built-in compression support."""

    def __init__(self, file_path: Union[str, Path], encoding: str = None, compression_settings=None):
        extension = Path(file_path).suffix.lower()
        if extension not in VTKConfig.SUPPORTED_XML_EXTENSIONS:
            raise UnsupportedFormatError(f"Not an XML VTK file: {extension}")

        super().__init__(file_path, compression_settings)
        self.encoding = encoding or VTKConfig.DEFAULT_ENCODING
        self._piece_data = None

    def _is_supported_format(self) -> bool:
        return Path(self.file_path).suffix.lower() in VTKConfig.SUPPORTED_XML_EXTENSIONS

    def _detect_compression(self) -> CompressionType:
        """Detect compression from XML attributes."""
        try:
            piece_data = self._xml_data[self.data_type]['Piece']

            for section_name in ['Points', 'Cells', 'PointData', 'CellData', 'Coordinates']:
                if section_name in piece_data:
                    arrays = self._get_arrays_from_section(piece_data[section_name])

                    for array in arrays:
                        compressor = array.get('@compressor', '').lower()
                        if compressor and compressor != 'none':
                            return self._detect_compression_from_string(compressor)

        except Exception as e:
            logger.debug(f"Error detecting compression: {e}")

        return CompressionType.NONE

    def _get_arrays_from_section(self, section_data: Dict) -> list:
        """Get arrays from section, handling both DataArray and Array keys."""
        array_key = 'DataArray' if 'DataArray' in section_data else 'Array'
        if array_key not in section_data:
            return []

        arrays = section_data[array_key]
        return arrays if isinstance(arrays, list) else [arrays]

    @handle_vtk_errors_with_compression
    def _load_file_structure(self):
        """Load XML structure with compression detection."""
        try:
            raw_bytes = self.file_path.read_bytes()

            try:
                self._xml_data = xmltodict.parse(raw_bytes)['VTKFile']
                self._handle_appended_data()
            except:
                self._xml_data = self._parse_invalid_xml_with_binary(raw_bytes)

            self._extract_xml_metadata()

        except Exception as e:
            raise InvalidVTKFileError(f"Cannot parse XML file: {e}")

    def _extract_xml_metadata(self):
        """Extract XML metadata and attributes."""
        try:
            self.data_type = self._xml_data['@type']
            self.file_version = float(self._xml_data['@version'])
            self.byte_order = self._xml_data['@byte_order'].lower()

            if self.file_version < 1:
                self.byte_count_type = 'UInt32'
            else:
                self.byte_count_type = self._xml_data['@header_type']

            self.byte_count_format = _parse_bytecount_type(
                self.byte_count_type, self.byte_order
            )

            try:
                self.data_format = next(dict_extract_generator(
                    '@format', self._xml_data[self.data_type]['Piece']
                ))
            except StopIteration:
                self.data_format = None

            self._piece_data = self._xml_data[self.data_type]['Piece']

        except KeyError as e:
            raise MissingDataError(f"Missing required XML attribute: {e}")
        except Exception as e:
            raise DataCorruptionError(f"Invalid XML metadata: {e}")

    def _get_data_type(self) -> str:
        return self._xml_data['@type']

    def _get_source_type(self) -> str:
        return 'xml'

    @handle_vtk_errors_with_compression
    def _extract_raw_data_arrays(self, data_section: str, decompress: bool = True) -> Optional[Dict]:
        """Extract XML data arrays."""
        try:
            if data_section in self._piece_data:
                section_data = self._piece_data[data_section]
                if section_data:
                    array_key = 'DataArray' if 'DataArray' in section_data else 'Array'
                    if array_key in section_data:
                        return section_data[array_key]
            return None
        except Exception as e:
            logger.warning(f"Error accessing {data_section}: {e}")
            return None

    def _process_compressed_xml_arrays(self, xml_data: Dict) -> Dict:
        """Process compressed XML arrays."""
        compression_context = {
            'xml_reader': self,
            'compression_processor': self._compression_processor
        }

        return DataArrayProcessor.process_data_arrays(
            xml_data, 'xml', compression_context
        ) or {}

    def _process_compressed_hdf5_arrays(self, hdf5_data: Dict) -> Dict:
        """Not applicable for XML reader."""
        return {}

    @handle_vtk_errors_with_compression
    def _extract_points(self) -> Dict:
        """Extract points from XML."""
        try:
            raw_points = self._safe_extract_data_arrays('Points')
            if not raw_points:
                raise MissingDataError("No points data found")

            points = determine_points_key(raw_points)
            return {'points': points}
        except Exception as e:
            raise DataCorruptionError(f"Corrupted points data: {e}")

    @handle_vtk_errors_with_compression
    def _extract_connectivity(self) -> Dict:
        """Extract connectivity data from XML."""
        try:
            raw_cells = self._safe_extract_data_arrays('Cells')
            if not raw_cells:
                raise MissingDataError("No cells data found")

            connectivity = raw_cells.get('connectivity')
            offsets = raw_cells.get('offsets')
            types = raw_cells.get('types')

            if connectivity is None or offsets is None or types is None:
                raise MissingDataError("Missing connectivity components")

            return {
                'connectivity': connectivity,
                'offsets': offsets,
                'types': types
            }

        except Exception as e:
            raise DataCorruptionError(f"Corrupted connectivity data: {e}")

    @handle_vtk_errors_with_compression
    def _extract_polydata_topology(self) -> Dict:
        """Extract polydata topology from XML."""
        topology = {}

        for section_name, vtk_name in VTKConfig.POLYDATA_TOPOLOGY_SECTIONS.items():
            if section_name in self._piece_data:
                topology_obj = PolyDataTopologyProcessor.process_xml_topology(
                    self._piece_data, self, section_name
                )
                if topology_obj:
                    topology[vtk_name] = topology_obj

        return topology

    @handle_vtk_errors_with_compression
    def _extract_image_grid(self) -> Grid:
        """Extract image data grid from XML attributes."""
        try:
            piece_attrs = self._piece_data

            whole_extents = piece_attrs.get('@WholeExtent')
            origin = piece_attrs.get('@Origin')
            spacing = piece_attrs.get('@Spacing')
            direction = piece_attrs.get('@Direction')

            if not whole_extents or not origin or not spacing:
                raise MissingDataError("Missing required grid attributes")

            return GridTopologyProcessor.create_grid_from_attributes(
                whole_extents, origin, spacing, direction
            )

        except Exception as e:
            raise DataCorruptionError(f"Invalid image grid data: {e}")

    @handle_vtk_errors_with_compression
    def _extract_extents(self) -> np.ndarray:
        """Extract extents for structured grid from XML."""
        try:
            extents_str = self._piece_data.get('@WholeExtent')
            if not extents_str:
                raise MissingDataError("WholeExtent attribute not found")

            extents = np.fromstring(extents_str, dtype=int, sep=' ')
            return extents

        except Exception as e:
            raise DataCorruptionError(f"Invalid extents data: {e}")

    @handle_vtk_errors_with_compression
    def _extract_grid_coordinates(self) -> GridCoordinates:
        """Extract rectilinear grid coordinates from XML."""
        try:
            # Extract coordinate arrays from XML
            coordinates_data = self._safe_extract_data_arrays('Coordinates')
            if not coordinates_data:
                raise MissingDataError("No coordinates data found")

            x_coords = coordinates_data.get('XCoordinates')
            y_coords = coordinates_data.get('YCoordinates')
            z_coords = coordinates_data.get('ZCoordinates')

            if x_coords is None or y_coords is None or z_coords is None:
                raise MissingDataError("Missing coordinate arrays")

            # Get extents from attributes
            whole_extents = self._piece_data.get('@WholeExtent')
            if not whole_extents:
                # Calculate from coordinate lengths
                whole_extents = np.array([
                    0, len(x_coords) - 1,
                    0, len(y_coords) - 1,
                    0, len(z_coords) - 1
                ])

            return GridTopologyProcessor.create_grid_coordinates(
                x_coords, y_coords, z_coords, whole_extents
            )

        except Exception as e:
            raise DataCorruptionError(f"Invalid coordinate data: {e}")

    def _bytes_to_array(self, data_bytes: bytes, array_info: Dict) -> np.ndarray:
        """
        Convert decompressed bytes to numpy array (equivalent to final step of decode_array).

        This is used after decompression to convert raw bytes to numpy array.
        """
        try:
            # Get array metadata from XML
            vtk_type = array_info.get('@type', 'Float32')
            num_components = int(array_info.get('@NumberOfComponents', 1))

            # Convert VTK type to numpy dtype using config
            numpy_dtype = VTKConfig.get_numpy_dtype(vtk_type)
            if numpy_dtype is None:
                # Fallback mapping
                dtype_map = {
                    'Float32': np.float32, 'Float64': np.float64,
                    'Int32': np.int32, 'Int64': np.int64,
                    'UInt32': np.uint32, 'UInt64': np.uint64,
                    'Int8': np.int8, 'UInt8': np.uint8
                }
                numpy_dtype = dtype_map.get(vtk_type, np.float32)

            # Handle byte order
            if numpy_dtype != 's':  # Not string data
                numpy_dtype = self._decode_np_byteorder(numpy_dtype)

            # Parse binary data
            if vtk_type.lower() == 'string':
                # Handle string data
                data_str = data_bytes.decode('utf-8').rstrip('\x00')
                return data_str.split('\x00')
            else:
                array = np.frombuffer(data_bytes, dtype=numpy_dtype)

            # Reshape if multi-component
            if num_components > 1:
                array = array.reshape(-1, num_components)

            return array

        except Exception as e:
            logger.error(f"Error converting bytes to array: {e}")
            raise DataCorruptionError(f"Failed to parse array data: {e}")

    def _extract_array_data_standard(self, array_data: Dict) -> bytes:
        """
        Extract standard (uncompressed) array data as bytes.

        This is equivalent to the format-handling part of your original decode_array(),
        but returns raw bytes instead of numpy arrays.
        """
        try:
            data_text = array_data.get('#text', '')
            offset = array_data.get('@offset')
            vtk_type = array_data.get('@type', 'Float32')

            if self.data_format == 'ascii':
                # Convert ASCII to bytes
                if vtk_type.lower() == 'string':
                    # Handle string data
                    chars = list(map(chr, map(int, data_text.split())))
                    string_data = ''.join(chars).rstrip('\x00')
                    return string_data.encode('utf-8')
                else:
                    # Convert ASCII numbers to binary
                    array = np.fromstring(data_text, dtype=VTKConfig.get_numpy_dtype(vtk_type), sep=' ')
                    return array.tobytes()

            elif self.data_format == 'binary':
                # Decode base64 and extract actual data (skip size header)
                binary_data = pybase64.b64decode(data_text)
                return self._extract_from_binary_data(binary_data, vtk_type)

            elif self.data_format == 'appended':
                if self.appended_data_bstr is None:
                    raise ValueError("Appended data is required for 'appended' format")

                if offset not in self.appended_data_arrays:
                    raise ValueError(f"Offset {offset} not found in appended data")

                binary_data = self.appended_data_arrays[offset]
                return self._extract_from_binary_data(binary_data, vtk_type)

            else:
                raise ValueError(f"Unknown format type: {self.data_format}")

        except Exception as e:
            raise DataCorruptionError(f"Failed to extract array data: {e}")

    def _extract_from_binary_data(self, binary_data: bytes, vtk_type: str) -> bytes:
        """
        Extract actual array data from binary data (removing size header).

        Binary VTK data format:
        [size_header][actual_data]

        Note: vtk_type is kept for potential future use with string data or
        special type handling, but currently not used in the extraction logic.
        """
        try:
            # Read size header
            data_size = struct.unpack_from(self.byte_count_format[0], binary_data)[0]
            header_size = self.byte_count_format[1]

            # Extract actual data
            actual_data = binary_data[header_size:header_size + data_size]

            if len(actual_data) != data_size:
                raise ValueError(f"Data size mismatch: expected {data_size}, got {len(actual_data)}")

            # Optional: Add type-specific validation in the future
            # if vtk_type.lower() == 'string':
            #     # Could add string-specific validation here
            #     pass

            return actual_data

        except Exception as e:
            raise DataCorruptionError(f"Failed to extract from binary data: {e}")

    def extract_data_array(self, array_data: Dict) -> tuple:
        """
        Extract single data array from XML (equivalent to your original extract_data_array).

        This is the main method that combines format handling and array conversion.
        """
        try:
            # Extract metadata
            data_name = array_data.get('@Name', 'unknown_name')
            vtk_type = array_data.get('@type', 'Float32')
            num_components = int(array_data.get('@NumberOfComponents', 1))

            # Check for compression
            compressor = array_data.get('@compressor', 'none')
            if compressor.lower() != 'none' and self._detected_compression != CompressionType.NONE:
                # Handle compressed data using compression processor
                raw_data = self._extract_array_data_standard(array_data)
                decompressed_data = self._compression_processor.process_compressed_array(
                    raw_data, {'type': self._detected_compression.value}
                )
                array = self._bytes_to_array(decompressed_data, array_data)
            else:
                # Handle uncompressed data using original logic
                array = self._decode_array_legacy(array_data)

            return data_name, array

        except Exception as e:
            logger.error(f"Failed to extract data array {array_data.get('@Name', 'unknown')}: {e}")
            raise DataCorruptionError(f"Array extraction failed: {e}")

    def _decode_array_legacy(self, array_data: Dict) -> np.ndarray:
        """
        Legacy decode_array implementation for uncompressed data.

        This preserves your original decode_array logic for backward compatibility.
        """
        try:
            data_text = array_data.get('#text', '')
            offset = array_data.get('@offset')
            vtk_type = array_data.get('@type', 'Float32')
            num_components = int(array_data.get('@NumberOfComponents', 1))

            # Get numpy dtype
            numpy_dtype = VTKConfig.get_numpy_dtype(vtk_type) or self.parse_data_type(vtk_type)

            if self.data_format == 'ascii':
                if vtk_type.lower() == 'string':
                    chars = list(map(chr, map(int, data_text.split())))
                    return ''.join(chars).rstrip('\x00').split('\x00')
                else:
                    array = np.fromstring(data_text, dtype=numpy_dtype, sep=' ')

            elif self.data_format == 'binary':
                binary_data = pybase64.b64decode(data_text)
                array = self._decode_byte_data(binary_data, numpy_dtype)

            elif self.data_format == 'appended':
                if self.appended_data_bstr is None:
                    raise ValueError("Appended data is required for 'appended' format")
                array = self._decode_byte_data(self.appended_data_arrays[offset], numpy_dtype)

            else:
                raise ValueError(f"Unknown format type: {self.data_format}")

            # Reshape if multi-component
            if num_components > 1 and vtk_type.lower() != 'string':
                array = array.reshape(-1, num_components)

            return array

        except Exception as e:
            raise DataCorruptionError(f"Legacy decode failed: {e}")

    def _decode_byte_data(self, data: bytes, data_type) -> np.ndarray:
        """
        Helper to decode binary data (from your original implementation).
        """
        data_size = struct.unpack_from(self.byte_count_format[0], data)[0]

        if data_type != 's':
            dtype = self._decode_np_byteorder(data_type)
            return np.frombuffer(data[self.byte_count_format[1]:self.byte_count_format[1] + data_size], dtype=dtype)
        else:
            dtype = self._decode_str_byteorder(data_type, data_size)
            data_strs = struct.unpack(dtype, data[self.byte_count_format[1]:])[0]
            return data_strs.decode('utf8').rstrip('\x00').split('\x00')

    def _decode_np_byteorder(self, dtype):
        """Helper to adjust dtype based on byte order (from your original)."""
        from ..helpers import LITTLE_ENDIAN, BIG_ENDIAN
        new_byteorder = LITTLE_ENDIAN if self.byte_order in ['<', 'littleendian'] else BIG_ENDIAN
        return np.dtype(dtype).newbyteorder(new_byteorder)

    def _decode_str_byteorder(self, dtype, data_size):
        """Helper to adjust string dtype based on byte order (from your original)."""
        from ..helpers import LITTLE_ENDIAN, BIG_ENDIAN
        new_byteorder = LITTLE_ENDIAN if self.byte_order in ['<', 'littleendian'] else BIG_ENDIAN
        return new_byteorder + str(data_size) + dtype

    @staticmethod
    def parse_data_type(data_type):
        """Resolves NumPy dtype (from your original implementation)."""
        type_mapping = {
            'int': np.int64, 'float': np.float32, 'double': np.float64,
            'float16': np.float16, 'float32': np.float32, 'float64': np.float64,
            'int8': np.int8, 'int16': np.int16, 'int32': np.int32, 'int64': np.int64,
            'uint8': np.uint8, 'uint16': np.uint16, 'uint32': np.uint32, 'uint64': np.uint64,
            'string': 's'
        }
        return type_mapping.get(data_type.lower(), None)

    def __del__(self):
        """Cleanup - XML reader doesn't need special cleanup."""
        pass