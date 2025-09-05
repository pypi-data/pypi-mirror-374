class TestCustomExceptions:
    """Test custom exception classes."""

    def test_vtk_reader_error_inheritance(self):
        """Test VTK reader error inheritance."""
        error = VTKReaderError("test message")
        assert isinstance(error, Exception)
        assert str(error) == "test message"

    def test_specific_exception_types(self):
        """Test specific exception types inherit correctly."""
        exceptions_to_test = [
            UnsupportedFormatError,
            InvalidVTKFileError,
            MissingDataError,
            DataCorruptionError
        ]

        for exc_type in exceptions_to_test:
            error = exc_type("test")
            assert isinstance(error, VTKReaderError)
            assert isinstance(error, Exception)