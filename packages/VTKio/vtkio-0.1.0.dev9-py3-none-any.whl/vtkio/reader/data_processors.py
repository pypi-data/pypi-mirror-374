# !/usr/bin/env python
"""
Unified data processing layer for VTK readers.

This module provides standardized processing for data arrays and VTK data structures,
eliminating duplication between XML and HDF5 readers.
"""

__author__ = 'J.P. Morrissey'
__copyright__ = 'Copyright 2022-2025'
__maintainer__ = 'J.P. Morrissey'
__email__ = 'morrissey.jp@gmail.com'
__status__ = 'Development'



from typing import Dict, Any, Optional, Union, List
import numpy as np
import h5py
import logging

from .compression import CompressionType
# Import your existing VTK structures
from ..vtk_structures import (
    Cell, Grid, GridCoordinates, ImageData, PolyData, PolyDataTopology,
    RectilinearData, StructuredData, UnstructuredGrid
)

logger = logging.getLogger(__name__)


class DataArrayProcessor:
    """Unified processor for data arrays from both XML and HDF5 sources with compression support."""

    @staticmethod
    def process_data_arrays(data_source: Union[h5py.Group, Dict, List],
                            source_type: str = 'hdf5',
                            compression_context: Optional[Dict] = None) -> Optional[Dict[str, np.ndarray]]:
        """
        Process data arrays from either HDF5 or XML sources with compression support.

        Parameters
        ----------
        data_source : Union[h5py.Group, Dict, List]
            Source data from HDF5 group or XML dictionary/list
        source_type : str
            Type of source: 'hdf5' or 'xml'
        compression_context : dict, optional
            Compression context including processor and settings

        Returns
        -------
        Optional[Dict[str, np.ndarray]]
            Dictionary of processed arrays or None if no data
        """
        if source_type == 'hdf5':
            return DataArrayProcessor._process_hdf5_arrays(data_source, compression_context)
        elif source_type == 'xml':
            return DataArrayProcessor._process_xml_arrays(data_source, compression_context)
        else:
            raise ValueError(f"Unsupported source type: {source_type}")

    @staticmethod
    def _process_hdf5_arrays(hdf5_group: h5py.Group,
                             compression_context: Optional[Dict] = None) -> Optional[Dict[str, np.ndarray]]:
        """Process HDF5 group data arrays with compression awareness."""
        if not hdf5_group:
            return None

        data = {}
        try:
            for dname, darray in hdf5_group.items():
                # HDF5 handles compression transparently, but log if detected
                if compression_context and hasattr(darray, 'compression'):
                    if darray.compression:
                        logger.debug(f"Reading compressed HDF5 dataset {dname} ({darray.compression})")

                if len(darray.shape) == 0:
                    # Scalar dataset
                    data[dname] = darray[()]
                else:
                    num_comp = darray.shape[-1] if len(darray.shape) > 1 else 1

                    if num_comp <= 1:
                        data[dname] = darray[:].reshape(-1, num_comp).flatten()
                    else:
                        data[dname] = darray[:].reshape(-1, num_comp)

        except Exception as e:
            logger.warning(f"Error processing HDF5 arrays: {e}")
            return None

        return data if data else None

    @staticmethod
    def _process_xml_arrays(xml_data: Union[Dict, List],
                            compression_context: Optional[Dict] = None) -> Optional[Dict[str, np.ndarray]]:
        """Process XML data arrays with compression support."""
        if not xml_data:
            return None

        try:
            xml_reader = compression_context.get('xml_reader') if compression_context else None
            if not xml_reader:
                raise ValueError("XML reader required for processing XML arrays")

            if isinstance(xml_data, list):
                data_arrays = {}
                for data in xml_data:
                    name, array = DataArrayProcessor._extract_single_xml_array(
                        data, xml_reader, compression_context
                    )
                    data_arrays[name] = array
            else:
                name, array = DataArrayProcessor._extract_single_xml_array(
                    xml_data, xml_reader, compression_context
                )
                data_arrays = {name: array}

            return data_arrays

        except Exception as e:
            logger.warning(f"Error processing XML arrays: {e}")
            return None

    @staticmethod
    def _extract_single_xml_array(xml_array_data: Dict[str, Any],
                                  xml_reader,
                                  compression_context: Optional[Dict] = None) -> tuple:
        """Extract single XML array with compression support."""
        array_name = xml_array_data.get('@Name', 'unknown')

        # Check for compression
        compressor = xml_array_data.get('@compressor', 'none')
        compression_type = CompressionType(compressor.lower() if compressor != 'none' else 'none')

        if compression_type == CompressionType.NONE:
            # Use standard extraction
            return xml_reader.extract_data_array(xml_array_data)

        # Handle compressed array
        compression_processor = compression_context.get('compression_processor') if compression_context else None
        if not compression_processor:
            logger.warning(f"No compression processor available for array {array_name}")
            return xml_reader.extract_data_array(xml_array_data)

        try:
            # Extract raw compressed data
            raw_data = xml_reader._extract_array_data_standard(xml_array_data)

            # Decompress using processor
            decompressed_data = compression_processor.process_compressed_array(
                raw_data, {'type': compression_type.value}
            )

            # Convert to numpy array
            array = xml_reader._bytes_to_array(decompressed_data, xml_array_data)
            return array_name, array

        except Exception as e:
            logger.warning(f"Failed to decompress array {array_name}: {e}")
            # Fallback to standard processing
            return xml_reader.extract_data_array(xml_array_data)


class VTKDataProcessor:
    """Unified processor for creating VTK data structures."""

    @staticmethod
    def create_unstructured_grid(points: np.ndarray,
                                 connectivity: np.ndarray,
                                 offsets: np.ndarray,
                                 types: np.ndarray,
                                 point_data: Optional[Dict] = None,
                                 cell_data: Optional[Dict] = None,
                                 field_data: Optional[Dict] = None) -> UnstructuredGrid:
        """Create UnstructuredGrid with standardized validation."""
        # Validate inputs
        if points is None or len(points) == 0:
            raise ValueError("Points array is required and cannot be empty")
        if connectivity is None or offsets is None or types is None:
            raise ValueError("Connectivity, offsets, and types are required")

        topology = Cell(connectivity=connectivity, offsets=offsets, types=types)

        return UnstructuredGrid(
            points=points,
            cells=topology,
            point_data=point_data,
            cell_data=cell_data,
            field_data=field_data
        )

    @staticmethod
    def create_polydata(points: np.ndarray,
                        verts: Optional[PolyDataTopology] = None,
                        lines: Optional[PolyDataTopology] = None,
                        strips: Optional[PolyDataTopology] = None,
                        polys: Optional[PolyDataTopology] = None,
                        point_data: Optional[Dict] = None,
                        cell_data: Optional[Dict] = None,
                        field_data: Optional[Dict] = None) -> PolyData:
        """Create PolyData with standardized validation."""
        if points is None or len(points) == 0:
            logger.warning("PolyData created with empty or missing points")

        return PolyData(
            points=points,
            verts=verts,
            lines=lines,
            strips=strips,
            polys=polys,
            point_data=point_data,
            cell_data=cell_data,
            field_data=field_data
        )

    @staticmethod
    def create_image_data(grid_topology: Grid,
                          point_data: Optional[Dict] = None,
                          cell_data: Optional[Dict] = None,
                          field_data: Optional[Dict] = None) -> ImageData:
        """Create ImageData with standardized validation."""
        if grid_topology is None:
            raise ValueError("Grid topology is required for ImageData")

        return ImageData(
            point_data=point_data,
            cell_data=cell_data,
            field_data=field_data,
            grid=grid_topology
        )

    @staticmethod
    def create_structured_data(points: np.ndarray,
                               whole_extents: np.ndarray,
                               point_data: Optional[Dict] = None,
                               cell_data: Optional[Dict] = None,
                               field_data: Optional[Dict] = None) -> StructuredData:
        """Create StructuredData with standardized validation."""
        if points is None or whole_extents is None:
            raise ValueError("Points and whole_extents are required for StructuredData")

        return StructuredData(
            point_data=point_data,
            cell_data=cell_data,
            field_data=field_data,
            points=points,
            whole_extents=whole_extents
        )

    @staticmethod
    def create_rectilinear_data(coordinates: GridCoordinates,
                                point_data: Optional[Dict] = None,
                                cell_data: Optional[Dict] = None,
                                field_data: Optional[Dict] = None) -> RectilinearData:
        """Create RectilinearData with standardized validation."""
        if coordinates is None:
            raise ValueError("Grid coordinates are required for RectilinearData")

        return RectilinearData(
            point_data=point_data,
            cell_data=cell_data,
            field_data=field_data,
            coordinates=coordinates
        )


class PolyDataTopologyProcessor:
    """Specialized processor for PolyData topology elements."""

    @staticmethod
    def process_hdf5_topology(hdf5_group: h5py.Group,
                              topology_name: str) -> Optional[PolyDataTopology]:
        """Process topology from HDF5 source."""
        try:
            data = DataArrayProcessor._process_hdf5_arrays(hdf5_group[topology_name])
            if data and 'Connectivity' in data and 'Offsets' in data:
                # HDF5 format typically includes the first offset (0)
                offsets = data['Offsets']
                if len(offsets) > 0 and offsets[0] == 0:
                    offsets = offsets[1:]

                return PolyDataTopology(
                    connectivity=data['Connectivity'],
                    offsets=offsets
                )
        except (KeyError, Exception) as e:
            logger.debug(f"No {topology_name} topology found in HDF5: {e}")

        return None

    @staticmethod
    def process_xml_topology(xml_data: Dict,
                             xml_reader: 'XMLVTKReader',
                             topology_name: str) -> Optional[PolyDataTopology]:
        """Process topology from XML source."""
        try:
            topology_data = DataArrayProcessor._process_xml_arrays(
                xml_data[topology_name]['DataArray'], xml_reader
            )

            if topology_data and 'connectivity' in topology_data and 'offsets' in topology_data:
                return PolyDataTopology(
                    connectivity=topology_data['connectivity'],
                    offsets=topology_data['offsets']
                )
        except (KeyError, Exception) as e:
            logger.debug(f"No {topology_name} topology found in XML: {e}")

        return None


class GridTopologyProcessor:
    """Processor for grid topology structures."""

    @staticmethod
    def create_grid_from_attributes(whole_extents: Union[np.ndarray, str],
                                    origin: Union[np.ndarray, str],
                                    spacing: Union[np.ndarray, str],
                                    direction: Union[np.ndarray, str] = None) -> Grid:
        """Create Grid topology from attributes (handles both HDF5 and XML)."""
        # Convert string attributes to numpy arrays if needed
        if isinstance(whole_extents, str):
            whole_extents = np.fromstring(whole_extents, dtype=int, sep=' ')
        if isinstance(origin, str):
            origin = np.fromstring(origin, dtype=np.float32, sep=' ')
        if isinstance(spacing, str):
            spacing = np.fromstring(spacing, dtype=np.float32, sep=' ')
        if isinstance(direction, str):
            direction = np.fromstring(direction, dtype=np.float32, sep=' ')

        return Grid(
            whole_extents=whole_extents,
            origin=origin,
            spacing=spacing,
            direction=direction
        )

    @staticmethod
    def create_grid_coordinates(x_coords: np.ndarray,
                                y_coords: np.ndarray,
                                z_coords: np.ndarray,
                                whole_extents: Union[np.ndarray, str]) -> GridCoordinates:
        """Create GridCoordinates structure."""
        if isinstance(whole_extents, str):
            whole_extents = np.fromstring(whole_extents, sep=' ')

        return GridCoordinates(
            x=x_coords,
            y=y_coords,
            z=z_coords,
            whole_extents=whole_extents
        )


# Utility functions for common operations
def determine_points_key(raw_points: Dict[str, np.ndarray]) -> np.ndarray:
    """Determine the correct points array from raw point data."""
    # Try common point array names
    point_keys = ['points', 'Points', 'coordinates', 'Coordinates']

    for key in point_keys:
        if key in raw_points:
            return raw_points[key]

    # If no standard key found, return the first array
    if raw_points:
        return next(iter(raw_points.values()))

    raise ValueError("No point data found in raw_points dictionary")


def safe_get_hdf5_attr(hdf5_obj: h5py.Group, attr_name: str, default=None):
    """Safely get HDF5 attribute with default fallback."""
    try:
        attr = hdf5_obj.attrs[attr_name]
        # Decode bytes to string if necessary
        if isinstance(attr, bytes):
            return attr.decode('utf-8')
        return attr
    except KeyError:
        logger.debug(f"Attribute {attr_name} not found, using default: {default}")
        return default
