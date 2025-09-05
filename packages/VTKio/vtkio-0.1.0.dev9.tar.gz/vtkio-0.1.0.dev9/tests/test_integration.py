class TestIntegrationWithRealData:
    """Integration tests using real VTK data files."""

    def test_load_all_xml_formats(self, vtk_xml_files):
        """Test loading different XML VTK formats."""
        try:
            data = load_vtk_data(vtk_xml_files)
            assert data is not None

            # Basic validation that we got a VTK structure
            assert hasattr(data, 'points') or hasattr(data, 'grid')

        except Exception as e:
            pytest.fail(f"Failed to load {vtk_xml_files}: {e}")

    def test_load_hdf5_formats(self, vtk_hdf5_files):
        """Test loading HDF5 VTK formats."""
        try:
            data = load_vtk_data(vtk_hdf5_files)
            assert data is not None

        except Exception as e:
            pytest.fail(f"Failed to load {vtk_hdf5_files}: {e}")

    def test_file_validation_integration(self, vtk_xml_files):
        """Test file validation with real files."""
        from vtk_reader.api import validate_vtk_file

        result = validate_vtk_file(vtk_xml_files)
        assert result['is_valid'] is True
        assert 'vtk_type' in result
        assert 'file_size_mb' in result

    def test_get_file_info_integration(self, vtk_xml_files):
        """Test getting file info from real files."""
        from vtk_reader.api import get_file_info

        info = get_file_info(vtk_xml_files)
        assert info['is_valid'] is True
        assert 'file_path' in info
        assert 'reader_type' in info


class TestErrorHandlingIntegration:
    """Integration tests for error handling."""

    def test_corrupted_file_handling(self, temp_dir):
        """Test handling of corrupted files."""
        corrupted_file = temp_dir / "corrupted.vtu"
        corrupted_file.write_text("corrupted content", encoding='utf-8')

        with pytest.raises((InvalidVTKFileError, VTKReaderError)):
            load_vtk_data(corrupted_file)

    def test_permission_error_handling(self, temp_dir, mock_xml_file):
        """Test handling of permission errors."""
        # This test may need to be adapted based on your OS
        import os
        import stat

        # Create a file and remove read permissions
        protected_file = temp_dir / "protected.vtu"
        protected_file.write_text(mock_xml_file.read_text())

        try:
            os.chmod(protected_file, stat.S_IWRITE)  # Write only

            with pytest.raises((PermissionError, VTKReaderError)):
                load_vtk_data(protected_file)

        finally:
            # Restore permissions for cleanup
            try:
                os.chmod(protected_file, stat.S_IREAD | stat.S_IWRITE)
            except:
                pass


class TestPerformanceAndMemory:
    """Performance and memory usage tests."""

    @pytest.mark.slow
    def test_large_file_handling(self, vtk_hdf5_files):
        """Test handling of large files (marked as slow test)."""
        from vtk_reader.api import QuickStart

        # Use performance-optimized settings
        settings = QuickStart.for_large_files()
        data = load_vtk_data(vtk_hdf5_files, settings=settings)
        assert data is not None

    def test_memory_usage_settings(self, mock_hdf5_file):
        """Test memory usage limitation settings."""
        settings = ReaderSettings(max_memory_usage_mb=64)  # Very low limit

        # Should still work for small test files
        data = load_vtk_data(mock_hdf5_file, settings=settings)
        assert data is not None
