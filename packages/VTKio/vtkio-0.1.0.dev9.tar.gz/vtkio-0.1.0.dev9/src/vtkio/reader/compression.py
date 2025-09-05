#!/usr/bin/env python
"""
Compression support module for VTK readers.

Handles zlib, lzma, and lz4 compression commonly used in VTK files.
"""

import struct
import zlib
import lzma
import logging
from pathlib import Path
from typing import Optional, Union, Dict, Any
from enum import Enum

from vtkio.config import VTKConfig, ReaderSettings
from vtkio.reader.api import VTKReaderFactory

logger = logging.getLogger(__name__)

# Optional import for lz4 (not always available)
try:
    import lz4.block
    HAS_LZ4 = True
except ImportError:
    HAS_LZ4 = False
    logger.debug("lz4 not available - lz4 compression will not be supported")


class CompressionType(Enum):
    """Compression types using config constants."""
    NONE = 'none'
    ZLIB = 'zlib'
    LZMA = 'lzma'
    LZ4 = 'lz4'

    @classmethod
    def from_string(cls, compression_str: str) -> 'CompressionType':
        """Create CompressionType from string using config validation."""
        normalized = VTKConfig.normalize_compression_type(compression_str)
        return cls(normalized)


class CompressionHandler:
    """Unified handler for VTK compression/decompression operations."""

    @staticmethod
    def detect_compression(data: bytes, compression_header: Optional[str] = None) -> CompressionType:
        """
        Detect compression type from data or header information.

        Parameters
        ----------
        data : bytes
            Raw data to analyze
        compression_header : str, optional
            Header information from XML attributes

        Returns
        -------
        CompressionType
            Detected compression type
        """
        if compression_header:
            header_lower = compression_header.lower()
            if 'zlib' in header_lower:
                return CompressionType.ZLIB
            elif 'lzma' in header_lower or 'xz' in header_lower:
                return CompressionType.LZMA
            elif 'lz4' in header_lower:
                return CompressionType.LZ4

        # Try to detect from magic bytes
        if len(data) >= 4:
            # zlib magic bytes (RFC 1950)
            if data[:2] in [b'\x78\x9c', b'\x78\xda', b'\x78\x01']:
                return CompressionType.ZLIB
            # LZMA/XZ magic bytes
            elif data[:6] == b'\xfd7zXZ\x00':
                return CompressionType.LZMA
            elif data[:4] == b'\x04"M\x18':  # LZ4 magic
                return CompressionType.LZ4

        return CompressionType.NONE

    @staticmethod
    def decompress_data(data: bytes,
                        compression_type: CompressionType,
                        uncompressed_size: Optional[int] = None) -> bytes:
        """
        Decompress data using the specified compression method.

        Parameters
        ----------
        data : bytes
            Compressed data
        compression_type : CompressionType
            Type of compression to use for decompression
        uncompressed_size : int, optional
            Expected uncompressed size (helps with validation)

        Returns
        -------
        bytes
            Decompressed data

        Raises
        ------
        ValueError
            If compression type is not supported or decompression fails
        """
        if compression_type == CompressionType.NONE:
            return data

        try:
            if compression_type == CompressionType.ZLIB:
                decompressed = zlib.decompress(data)
            elif compression_type == CompressionType.LZMA:
                decompressed = lzma.decompress(data)
            elif compression_type == CompressionType.LZ4:
                if not HAS_LZ4:
                    raise ValueError("lz4 library not available")
                # LZ4 requires uncompressed size for decompression
                if uncompressed_size is None:
                    raise ValueError("uncompressed_size required for LZ4 decompression")
                decompressed = lz4.block.decompress(data, uncompressed_size=uncompressed_size)
            else:
                raise ValueError(f"Unsupported compression type: {compression_type}")

            # Validate size if provided
            if uncompressed_size is not None and len(decompressed) != uncompressed_size:
                logger.warning(f"Decompressed size mismatch: expected {uncompressed_size}, got {len(decompressed)}")

            return decompressed

        except Exception as e:
            raise ValueError(f"Decompression failed for {compression_type.value}: {e}")


class CompressedDataProcessor:
    """Processor for handling compressed data arrays in VTK files."""

    def __init__(self, byte_order: str = 'little'):
        """
        Initialize processor with byte order information.

        Parameters
        ----------
        byte_order : str
            Byte order ('little' or 'big')
        """
        self.byte_order = byte_order
        self.endian_char = '<' if byte_order == 'little' else '>'

    def process_compressed_array(self,
                                 compressed_data: bytes,
                                 compression_info: Dict[str, Any]) -> bytes:
        """
        Process a compressed data array from VTK files.

        VTK compressed arrays have a specific structure:
        1. Header with block information
        2. Compressed blocks

        Parameters
        ----------
        compressed_data : bytes
            Raw compressed data from file
        compression_info : dict
            Information about compression (type, block size, etc.)

        Returns
        -------
        bytes
            Decompressed data ready for array parsing
        """
        compression_type = CompressionType(compression_info.get('type', 'none'))

        if compression_type == CompressionType.NONE:
            return compressed_data

        # Parse compression header
        header_info = self._parse_compression_header(compressed_data)

        # Extract and decompress blocks
        decompressed_blocks = []
        offset = header_info['data_offset']

        for i, (block_size, uncompressed_size) in enumerate(header_info['blocks']):
            if offset + block_size > len(compressed_data):
                raise ValueError(f"Block {i} extends beyond data bounds")

            block_data = compressed_data[offset:offset + block_size]
            decompressed_block = CompressionHandler.decompress_data(
                block_data, compression_type, uncompressed_size
            )
            decompressed_blocks.append(decompressed_block)
            offset += block_size

        return b''.join(decompressed_blocks)

    def _parse_compression_header(self, data: bytes) -> Dict[str, Any]:
        """
        Parse VTK compression header.

        VTK compression header format:
        - Number of blocks (uint64)
        - Block size (uint64)
        - Last block size (uint64)
        - Array of compressed block sizes (uint64 each)

        Parameters
        ----------
        data : bytes
            Raw data starting with compression header

        Returns
        -------
        dict
            Parsed header information
        """
        offset = 0
        uint64_fmt = f'{self.endian_char}Q'
        uint64_size = 8

        # Read number of blocks
        num_blocks = struct.unpack_from(uint64_fmt, data, offset)[0]
        offset += uint64_size

        # Read block size (standard block size)
        block_size = struct.unpack_from(uint64_fmt, data, offset)[0]
        offset += uint64_size

        # Read last block size
        last_block_size = struct.unpack_from(uint64_fmt, data, offset)[0]
        offset += uint64_size

        # Read compressed block sizes
        compressed_sizes = []
        for i in range(num_blocks):
            size = struct.unpack_from(uint64_fmt, data, offset)[0]
            compressed_sizes.append(size)
            offset += uint64_size

        # Calculate uncompressed sizes
        blocks = []
        for i, comp_size in enumerate(compressed_sizes):
            if i == num_blocks - 1:  # Last block
                uncomp_size = last_block_size
            else:
                uncomp_size = block_size
            blocks.append((comp_size, uncomp_size))

        return {
            'num_blocks': num_blocks,
            'block_size': block_size,
            'last_block_size': last_block_size,
            'blocks': blocks,
            'data_offset': offset
        }


# Configuration additions for compression
class CompressionSettings:
    """Compression settings using config defaults."""

    def __init__(self,
                 enable_compression: bool = True,
                 preferred_compression: str = None,
                 max_memory_mb: int = None,
                 block_size: int = None):
        """
        Initialize compression settings using config defaults.

        Parameters
        ----------
        enable_compression : bool
            Whether to enable compression support
        preferred_compression : str, optional
            Preferred compression type (uses config default if None)
        max_memory_mb : int, optional
            Max memory for decompression (uses config default if None)
        block_size : int, optional
            Compression block size (uses config default if None)
        """
        self.enable_compression = enable_compression

        # Use config defaults
        self.preferred_compression = CompressionType.from_string(
            preferred_compression or VTKConfig.DEFAULT_COMPRESSION_TYPE
        )
        self.max_memory_mb = max_memory_mb or VTKConfig.MAX_DECOMPRESSION_MEMORY_MB
        self.block_size = block_size or VTKConfig.DEFAULT_COMPRESSION_BLOCK_SIZE

        # Validate using config
        if not VTKConfig.validate_compression_type(self.preferred_compression.value):
            logger.warning(f"Unsupported compression type, falling back to zlib")
            self.preferred_compression = CompressionType.ZLIB


# Example usage in the main API
def load_vtk_data_with_compression(file_path: Union[str, Path],
                                  settings: Optional[ReaderSettings] = None,
                                  compression_settings: Optional[CompressionSettings] = None):
    """
    Load VTK data with compression support.

    Parameters
    ----------
    file_path : Union[str, Path]
        Path to potentially compressed VTK file
    compression_settings : CompressionSettings, optional
        Compression handling settings

    Returns
    -------
    VTK data structure
    """
    file_path = Path(file_path)
    # Use config-based factory
    factory = VTKReaderFactory(settings, compression_settings)

    # Create reader using config logic
    reader = factory.create_reader(file_path)

    return reader.parse()
