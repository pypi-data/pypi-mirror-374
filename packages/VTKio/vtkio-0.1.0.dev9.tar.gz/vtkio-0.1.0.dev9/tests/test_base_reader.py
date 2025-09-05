class TestBaseVTKReader:
    """Test base reader functionality."""

    def test_file_validation_nonexistent(self):
        """Test validation fails for non-existent files."""
        from vtk_reader.base_reader import BaseVTKReader

        class TestReader(BaseVTKReader):
            def _is_supported_format(self):
                return True

            def _load_file_structure(self):
                pass

            def _get_data_type(self):
                return "Test"

            def _extract_raw_data_arrays(self, section):
                return None

            def _get_source_type(self):
                return "test"

            def _extract_points(self):
                return {}

            def _extract_connectivity(self):
                return {}

            def _extract_polydata_topology(self):
                return {}

            def _extract_image_grid(self):
                return None

            def _extract_extents(self):
                return None

            def _extract_grid_coordinates(self):
                return None

        with pytest.raises(FileNotFoundError):
            TestReader("nonexistent.file")

    def test_empty_file_validation(self, temp_dir):
        """Test validation fails for empty files."""
        empty_file = temp_dir / "empty.vtu"
        empty_file.touch()

        with pytest.raises(InvalidVTKFileError, match="empty"):
            UnifiedXMLReader(empty_file)

    def test_standard_parsing_pattern_success(self, mock_xml_file):
        """Test the standard parsing pattern works correctly."""
        reader = UnifiedXMLReader(mock_xml_file)
        data = reader.parse()
        assert data is not None

    def test_error_handling_in_parse(self, mock_xml_file):
        """Test error handling in parse method."""
        reader = UnifiedXMLReader(mock_xml_file)

        # Mock a method to raise an exception
        with patch.object(reader, '_load_file_structure', side_effect=Exception("Test error")):
            with pytest.raises(VTKReaderError):
                reader.parse()