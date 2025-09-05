class TestVTKReaderFactory:
    """Test the main VTK reader factory."""

    def test_factory_initialization(self):
        """Test factory can be initialized with and without settings."""
        factory = VTKReaderFactory()
        assert factory.settings is not None

        custom_settings = ReaderSettings(validate_topology=False)
        factory_custom = VTKReaderFactory(custom_settings)
        assert factory_custom.settings.validate_topology is False

    def test_create_reader_hdf5(self, mock_hdf5_file):
        """Test creating HDF5 reader from factory."""
        factory = VTKReaderFactory()
        reader = factory.create_reader(mock_hdf5_file)
        assert isinstance(reader, UnifiedHDF5Reader)

    def test_create_reader_xml(self, mock_xml_file):
        """Test creating XML reader from factory."""
        factory = VTKReaderFactory()
        reader = factory.create_reader(mock_xml_file)
        assert isinstance(reader, UnifiedXMLReader)

    def test_unsupported_extension(self, temp_dir):
        """Test error handling for unsupported file extensions."""
        unsupported_file = temp_dir / "test.txt"
        unsupported_file.touch()

        factory = VTKReaderFactory()
        with pytest.raises(UnsupportedFormatError):
            factory.create_reader(unsupported_file)

    def test_nonexistent_file(self):
        """Test error handling for non-existent files."""
        factory = VTKReaderFactory()
        with pytest.raises(FileNotFoundError):
            factory.create_reader("nonexistent.vtu")


class TestLoadVTKData:
    """Test the main load_vtk_data function."""

    def test_load_hdf5_data(self, mock_hdf5_file):
        """Test loading HDF5 data."""
        data = load_vtk_data(mock_hdf5_file)
        assert data is not None
        # Add more specific assertions based on your VTK structures

    def test_load_xml_data(self, mock_xml_file):
        """Test loading XML data."""
        data = load_vtk_data(mock_xml_file)
        assert data is not None

    def test_load_with_custom_settings(self, mock_hdf5_file):
        """Test loading with custom settings."""
        settings = ReaderSettings(validate_topology=False)
        data = load_vtk_data(mock_hdf5_file, settings=settings)
        assert data is not None

    @pytest.mark.parametrize("file_fixture", ["mock_hdf5_file", "mock_xml_file"])
    def test_load_different_formats(self, request, file_fixture):
        """Parametrized test for different file formats."""
        file_path = request.getfixturevalue(file_fixture)
        data = load_vtk_data(file_path)
        assert data is not None


class TestBackwardCompatibility:
    """Test backward compatibility functions."""

    def test_read_vtkhdf_data_deprecated_warning(self, mock_hdf5_file):
        """Test that deprecated function issues warning."""
        from vtk_reader.api import read_vtkhdf_data

        with pytest.warns(DeprecationWarning, match="read_vtkhdf_data is deprecated"):
            data = read_vtkhdf_data(mock_hdf5_file)
            assert data is not None

    def test_read_vtkxml_data_deprecated_warning(self, mock_xml_file):
        """Test that deprecated function issues warning."""
        from vtk_reader.api import read_vtkxml_data

        with pytest.warns(DeprecationWarning, match="read_vtkxml_data is deprecated"):
            data = read_vtkxml_data(mock_xml_file)
            assert data is not None
