class TestUnifiedHDF5Reader:
    """Test HDF5 reader implementation."""

    def test_supported_extensions(self):
        """Test HDF5 reader recognizes correct extensions."""
        reader = UnifiedHDF5Reader
        assert '.h5' in reader.SUPPORTED_EXTENSIONS
        assert '.hdf5' in reader.SUPPORTED_EXTENSIONS

    def test_initialization(self, mock_hdf5_file):
        """Test HDF5 reader initialization."""
        reader = UnifiedHDF5Reader(mock_hdf5_file)
        assert reader.file_path == mock_hdf5_file

    def test_load_file_structure(self, mock_hdf5_file):
        """Test loading HDF5 file structure."""
        reader = UnifiedHDF5Reader(mock_hdf5_file)
        reader._load_file_structure()

        assert reader._hdf5_file is not None
        assert reader._vtkhdf_group is not None

    def test_get_data_type(self, mock_hdf5_file):
        """Test extracting data type from HDF5."""
        reader = UnifiedHDF5Reader(mock_hdf5_file)
        reader._load_file_structure()

        data_type = reader._get_data_type()
        assert data_type == 'UnstructuredGrid'

    def test_extract_points(self, mock_hdf5_file):
        """Test extracting points from HDF5."""
        reader = UnifiedHDF5Reader(mock_hdf5_file)
        reader._load_file_structure()

        points_data = reader._extract_points()
        assert 'points' in points_data
        assert isinstance(points_data['points'], np.ndarray)

    def test_invalid_hdf5_file(self, temp_dir):
        """Test handling of invalid HDF5 files."""
        invalid_file = temp_dir / "invalid.h5"
        invalid_file.write_text("not hdf5 content")

        with pytest.raises(InvalidVTKFileError):
            reader = UnifiedHDF5Reader(invalid_file)
            reader._load_file_structure()

    def test_missing_vtkhdf_group(self, temp_dir):
        """Test handling HDF5 without VTKHDF group."""
        file_path = temp_dir / "no_vtkhdf.h5"

        with h5py.File(file_path, 'w') as f:
            f.create_group('OtherGroup')

        with pytest.raises(InvalidVTKFileError, match="VTKHDF"):
            reader = UnifiedHDF5Reader(file_path)
            reader._load_file_structure()


class TestUnifiedXMLReader:
    """Test XML reader implementation."""

    def test_supported_extensions(self):
        """Test XML reader recognizes correct extensions."""
        reader = UnifiedXMLReader
        expected = {'.vti', '.vtr', '.vts', '.vtu', '.vtp'}
        assert reader.SUPPORTED_EXTENSIONS == expected

    def test_initialization(self, mock_xml_file):
        """Test XML reader initialization."""
        reader = UnifiedXMLReader(mock_xml_file)
        assert reader.file_path == mock_xml_file
        assert reader.encoding == 'utf-8'

    def test_load_file_structure(self, mock_xml_file):
        """Test loading XML file structure."""
        reader = UnifiedXMLReader(mock_xml_file)
        reader._load_file_structure()

        assert reader._xml_data is not None
        assert reader.data_type == 'UnstructuredGrid'

    def test_extract_xml_metadata(self, mock_xml_file):
        """Test extracting XML metadata."""
        reader = UnifiedXMLReader(mock_xml_file)
        reader._load_file_structure()

        assert reader.data_type == 'UnstructuredGrid'
        assert reader.file_version == 2.0
        assert reader.byte_order == 'littleendian'

    def test_malformed_xml(self, temp_dir):
        """Test handling of malformed XML."""
        malformed_file = temp_dir / "malformed.vtu"
        malformed_file.write_text("<VTKFile><InvalidXML", encoding='utf-8')

        with pytest.raises(InvalidVTKFileError):
            reader = UnifiedXMLReader(malformed_file)
            reader._load_file_structure()
