class TestVTKConfig:
    """Test VTK configuration functionality."""

    def test_config_constants(self):
        """Test that config constants are defined."""
        assert hasattr(VTKConfig, 'SUPPORTED_HDF5_EXTENSIONS')
        assert hasattr(VTKConfig, 'SUPPORTED_XML_EXTENSIONS')
        assert hasattr(VTKConfig, 'DEFAULT_ENCODING')

    def test_get_reader_class_for_extension(self):
        """Test reader class determination from file extension."""
        # Test HDF5 extensions
        for ext in ['.h5', '.hdf5']:
            test_file = Path(f"test{ext}")
            reader_class = VTKConfig.get_reader_class_for_extension(test_file)
            assert reader_class == 'UnifiedHDF5Reader'

        # Test XML extensions
        for ext in ['.vtu', '.vti', '.vtp']:
            test_file = Path(f"test{ext}")
            reader_class = VTKConfig.get_reader_class_for_extension(test_file)
            assert reader_class == 'UnifiedXMLReader'


class TestReaderSettings:
    """Test reader settings configuration."""

    def test_settings_initialization(self):
        """Test reader settings can be initialized."""
        settings = ReaderSettings()
        assert settings is not None

        # Test with custom values
        custom_settings = ReaderSettings(
            validate_topology=False,
            max_memory_usage_mb=2048
        )
        assert custom_settings.validate_topology is False
        assert custom_settings.max_memory_usage_mb == 2048