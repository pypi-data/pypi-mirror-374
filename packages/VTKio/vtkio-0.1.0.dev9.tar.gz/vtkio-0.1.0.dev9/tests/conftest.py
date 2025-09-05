import pytest
import tempfile
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch
import h5py
from typing import Dict, Any

# Import your modules (adjust paths as needed)
from vtk_reader.api import VTKReaderFactory, load_vtk_data
from vtk_reader.config import VTKConfig, ReaderSettings
from vtk_reader.exceptions import (
    VTKReaderError, UnsupportedFormatError, InvalidVTKFileError,
    MissingDataError, DataCorruptionError
)
from vtk_reader.concrete_readers import UnifiedHDF5Reader, UnifiedXMLReader


@pytest.fixture(scope="session")
def test_data_dir():
    """Path to test data directory."""
    return Path("TestData")


@pytest.fixture
def sample_settings():
    """Sample reader settings for testing."""
    return ReaderSettings(
        validate_topology=True,
        validate_data_consistency=True,
        strict_validation=False,
        continue_on_data_errors=False,
        max_memory_usage_mb=1024,
        chunk_size=8192
    )


@pytest.fixture
def temp_dir():
    """Temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_points():
    """Sample 3D points for testing."""
    return np.array([
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0]
    ], dtype=np.float32)


@pytest.fixture
def sample_connectivity():
    """Sample connectivity data for unstructured grid."""
    return {
        'connectivity': np.array([0, 1, 2, 0, 1, 3], dtype=np.int32),
        'offsets': np.array([3, 6], dtype=np.int32),
        'types': np.array([5, 5], dtype=np.uint8)  # VTK triangle cells
    }


@pytest.fixture
def mock_hdf5_file(temp_dir):
    """Create a mock HDF5 file for testing."""
    file_path = temp_dir / "test.h5"

    with h5py.File(file_path, 'w') as f:
        vtkhdf = f.create_group('VTKHDF')
        vtkhdf.attrs['Type'] = b'UnstructuredGrid'
        vtkhdf.attrs['Version'] = b'1.0'

        # Create sample datasets
        points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32)
        vtkhdf.create_dataset('Points', data=points)
        vtkhdf.create_dataset('Connectivity', data=[0, 1, 2])
        vtkhdf.create_dataset('Offsets', data=[0, 3])
        vtkhdf.create_dataset('Types', data=[5])

    return file_path


@pytest.fixture
def sample_xml_content():
    """Sample VTU XML content for testing."""
    return '''<?xml version="1.0"?>
<VTKFile type="UnstructuredGrid" version="2.0" byte_order="LittleEndian" header_type="UInt64">
  <UnstructuredGrid>
    <Piece NumberOfPoints="3" NumberOfCells="1">
      <Points>
        <DataArray type="Float32" Name="Points" NumberOfComponents="3" format="ascii">
          0 0 0 1 0 0 0 1 0
        </DataArray>
      </Points>
      <Cells>
        <DataArray type="Int64" Name="connectivity" format="ascii">
          0 1 2
        </DataArray>
        <DataArray type="Int64" Name="offsets" format="ascii">
          3
        </DataArray>
        <DataArray type="UInt8" Name="types" format="ascii">
          5
        </DataArray>
      </Cells>
    </Piece>
  </UnstructuredGrid>
</VTKFile>'''


@pytest.fixture
def mock_xml_file(temp_dir, sample_xml_content):
    """Create a mock XML file for testing."""
    file_path = temp_dir / "test.vtu"
    file_path.write_text(sample_xml_content, encoding='utf-8')
    return file_path


# Parametrized fixtures for different file types
@pytest.fixture(params=['vtu', 'vti', 'vtr', 'vts', 'vtp'])
def vtk_xml_files(request, test_data_dir):
    """Parametrized fixture for different XML VTK file types."""
    file_type = request.param
    data_dir = test_data_dir / file_type

    if not data_dir.exists():
        pytest.skip(f"Test data directory {data_dir} not found")

    files = list(data_dir.glob(f"*.{file_type}"))
    if not files:
        pytest.skip(f"No {file_type} files found in {data_dir}")

    return files[0]  # Return first file found


@pytest.fixture(params=['h5', 'hdf5'])
def vtk_hdf5_files(request, test_data_dir):
    """Parametrized fixture for HDF5 VTK files."""
    ext = request.param

    # Look in common directories
    for subdir in ['h5', 'hdf5', 'vtkhdf']:
        data_dir = test_data_dir / subdir
        if data_dir.exists():
            files = list(data_dir.glob(f"*.{ext}"))
            if files:
                return files[0]

    pytest.skip(f"No {ext} files found in test data")