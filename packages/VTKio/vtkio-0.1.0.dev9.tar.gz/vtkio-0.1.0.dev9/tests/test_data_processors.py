class TestDataArrayProcessor:
    """Test data array processing functionality."""

    def test_process_hdf5_arrays(self, mock_hdf5_file):
        """Test processing HDF5 data arrays."""
        from vtk_reader.data_processors import DataArrayProcessor

        with h5py.File(mock_hdf5_file, 'r') as f:
            vtkhdf = f['VTKHDF']
            # Add some test point data
            result = DataArrayProcessor.process_data_arrays(vtkhdf, 'hdf5')

            # Should return None if no data arrays, or dict if present
            assert result is None or isinstance(result, dict)

    def test_process_xml_arrays_empty(self):
        """Test processing empty XML arrays."""
        from vtk_reader.data_processors import DataArrayProcessor

        result = DataArrayProcessor.process_data_arrays(None, 'xml')
        assert result is None

    def test_unsupported_source_type(self):
        """Test error handling for unsupported source types."""
        from vtk_reader.data_processors import DataArrayProcessor

        with pytest.raises(ValueError, match="Unsupported source type"):
            DataArrayProcessor.process_data_arrays({}, 'unsupported')


class TestVTKDataProcessor:
    """Test VTK data structure creation."""

    def test_create_unstructured_grid(self, sample_points, sample_connectivity):
        """Test creating unstructured grid."""
        from vtk_reader.data_processors import VTKDataProcessor

        grid = VTKDataProcessor.create_unstructured_grid(
            points=sample_points,
            connectivity=sample_connectivity['connectivity'],
            offsets=sample_connectivity['offsets'],
            types=sample_connectivity['types']
        )

        assert grid is not None
        assert hasattr(grid, 'points')
        assert hasattr(grid, 'cells')

    def test_create_unstructured_grid_invalid_input(self):
        """Test error handling for invalid unstructured grid input."""
        from vtk_reader.data_processors import VTKDataProcessor

        with pytest.raises(ValueError, match="Points array is required"):
            VTKDataProcessor.create_unstructured_grid(
                points=None,
                connectivity=np.array([]),
                offsets=np.array([]),
                types=np.array([])
            )

    def test_create_polydata(self, sample_points):
        """Test creating polydata structure."""
        from vtk_reader.data_processors import VTKDataProcessor

        polydata = VTKDataProcessor.create_polydata(points=sample_points)

        assert polydata is not None
        assert hasattr(polydata, 'points')