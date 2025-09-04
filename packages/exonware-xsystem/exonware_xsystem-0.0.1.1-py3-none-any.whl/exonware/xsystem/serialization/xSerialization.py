"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: January 31, 2025

xSerialization - Self-transforming intelligent serializer that detects format
and morphs into the appropriate specialized serializer.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Type, Union

from .aSerialization import aSerialization
from .iSerialization import iSerialization
from .format_detector import FormatDetector
from ..config.logging_setup import get_logger

logger = get_logger("xsystem.serialization.xSerialization")


class xSerialization(aSerialization):
    """
    Intelligent self-transforming serializer that automatically detects format
    and replaces itself with the appropriate specialized serializer.
    
    This is a smart proxy that:
    1. Detects the format on first use
    2. Creates the appropriate specialized serializer
    3. Delegates all future calls to the specialized serializer
    4. Maintains the same interface throughout
    
    Usage:
        serializer = xSerialization()
        
        # First call triggers format detection and transformation
        result = serializer.dumps(data, file_path="data.json")  # Becomes JsonSerializer
        
        # All subsequent calls use the specialized serializer
        more_data = serializer.loads(result)  # Still JsonSerializer
    """
    
    def __init__(self, confidence_threshold: float = 0.7):
        """
        Initialize the intelligent serializer.
        
        Args:
            confidence_threshold: Minimum confidence for format detection
        """
        # Initialize instance attributes BEFORE calling super()
        self._detector = FormatDetector(confidence_threshold)
        self._specialized_serializer: Optional[iSerialization] = None
        self._detected_format: Optional[str] = None
        self._confidence_threshold = confidence_threshold
        
        # Initialize base class with reasonable defaults
        super().__init__()
        
        logger.debug("xSerialization initialized - ready for format detection")
    
    def _get_serializer_class(self, format_name: str) -> Type[iSerialization]:
        """
        Get serializer class for format name.
        
        Args:
            format_name: Format name (e.g., 'JSON', 'YAML')
            
        Returns:
            Serializer class
        """
        module_map = {
            'JSON': ('json', 'JsonSerializer'),
            'YAML': ('yaml', 'YamlSerializer'),
            'TOML': ('toml', 'TomlSerializer'),
            'XML': ('xml', 'XmlSerializer'),
            'CSV': ('csv', 'CsvSerializer'),
            'ConfigParser': ('configparser', 'ConfigParserSerializer'),
            'FormData': ('formdata', 'FormDataSerializer'),
            'Multipart': ('multipart', 'MultipartSerializer'),
            
            # Binary formats
            'BSON': ('bson', 'BsonSerializer'),
            'MessagePack': ('msgpack', 'MsgPackSerializer'),
            'CBOR': ('cbor', 'CborSerializer'),
            'Pickle': ('pickle', 'PickleSerializer'),
            'Marshal': ('marshal', 'MarshalSerializer'),
            'SQLite3': ('sqlite3', 'Sqlite3Serializer'),
            'DBM': ('dbm', 'DbmSerializer'),
            'Shelve': ('shelve', 'ShelveSerializer'),
            'Plistlib': ('plistlib', 'PlistlibSerializer'),
            
            # Schema-based formats
            'Avro': ('avro', 'AvroSerializer'),
            'Protobuf': ('protobuf', 'ProtobufSerializer'),
            'Thrift': ('thrift', 'ThriftSerializer'),
            'Parquet': ('parquet', 'ParquetSerializer'),
            'ORC': ('orc', 'OrcSerializer'),
            'CapnProto': ('capnproto', 'CapnProtoSerializer'),
            'FlatBuffers': ('flatbuffers', 'FlatBuffersSerializer'),
        }
        
        if format_name not in module_map:
            raise ValueError(f"Unknown format: {format_name}")
        
        module_name, class_name = module_map[format_name]
        
        try:
            # Import from current package
            module = __import__(f'exonware.xsystem.serialization.{module_name}', 
                              fromlist=[class_name])
            return getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Serializer for {format_name} not available: {e}")
    
    def _transform_to_specialized(
        self, 
        format_name: str, 
        file_path: Optional[Union[str, Path]] = None,
        content: Optional[Union[str, bytes]] = None,
        data: Optional[bytes] = None
    ) -> None:
        """
        Transform this instance into a specialized serializer.
        
        Args:
            format_name: Detected format name
            file_path: Optional file path used for detection
            content: Optional content used for detection
            data: Optional binary data used for detection
        """
        try:
            serializer_class = self._get_serializer_class(format_name)
            
            # Create specialized serializer with same configuration
            self._specialized_serializer = serializer_class(
                validate_input=self.validate_input,
                max_depth=self.max_depth,
                max_size_mb=self.max_size_mb,
                use_atomic_writes=self.use_atomic_writes,
                validate_paths=self.validate_paths,
                text_encoding=self.text_encoding,
                base64_encoding=self.base64_encoding,
            )
            
            self._detected_format = format_name
            
            logger.info(f"xSerialization transformed to {format_name}Serializer")
            
        except Exception as e:
            logger.error(f"Failed to transform to {format_name}: {e}")
            # Fallback to JSON serializer
            from .json import JsonSerializer
            self._specialized_serializer = JsonSerializer()
            self._detected_format = 'JSON'
            logger.warning("Fallback to JsonSerializer due to transformation failure")
    
    def _detect_and_transform(
        self, 
        data: Optional[Any] = None,
        file_path: Optional[Union[str, Path]] = None,
        content: Optional[Union[str, bytes]] = None,
        binary_data: Optional[bytes] = None,
        format_hint: Optional[str] = None
    ) -> None:
        """
        Detect format and transform to specialized serializer.
        
        Args:
            data: Data being serialized (for format hints)
            file_path: File path for extension-based detection
            content: Content for pattern-based detection
            binary_data: Binary data for magic byte detection
            format_hint: Optional format hint to override detection
        """
        if self._specialized_serializer is not None:
            return  # Already transformed
        
        # Use format hint if provided
        if format_hint:
            format_name = format_hint.upper()
            logger.debug(f"Using format hint: {format_name}")
        else:
            # Auto-detect format
            format_name = self._detector.get_best_format(
                file_path=file_path,
                content=content,
                data=binary_data
            )
            
            if not format_name:
                # Try to infer from data type if no other clues
                if data is not None:
                    if isinstance(data, (dict, list)):
                        format_name = 'JSON'  # Most common for structured data
                    elif isinstance(data, str):
                        format_name = 'JSON'  # Assume JSON string
                    elif isinstance(data, bytes):
                        format_name = 'MessagePack'  # Good binary default
                    else:
                        format_name = 'JSON'  # Safe default
                else:
                    format_name = 'JSON'  # Ultimate fallback
                
                logger.debug(f"Auto-detected format: {format_name}")
        
        # Transform to specialized serializer
        self._transform_to_specialized(format_name, file_path, content, binary_data)
    
    def _ensure_specialized(self, **detection_kwargs) -> iSerialization:
        """
        Ensure we have a specialized serializer, detecting if needed.
        
        Args:
            **detection_kwargs: Arguments for format detection
            
        Returns:
            The specialized serializer instance
        """
        if self._specialized_serializer is None:
            self._detect_and_transform(**detection_kwargs)
        
        return self._specialized_serializer
    
    # =============================================================================
    # PROPERTY DELEGATION - Delegate to specialized serializer after transformation
    # =============================================================================
    
    @property
    def format_name(self) -> str:
        """Get format name - detects if needed."""
        if self._specialized_serializer is None:
            return "Auto-Detect"
        return self._specialized_serializer.format_name
    
    @property
    def file_extensions(self) -> list[str]:
        """Get file extensions - detects if needed."""
        if self._specialized_serializer is None:
            return []  # Unknown until detection
        return self._specialized_serializer.file_extensions
    
    @property
    def mime_type(self) -> str:
        """Get MIME type - detects if needed."""
        if self._specialized_serializer is None:
            return "application/octet-stream"  # Generic until detection
        return self._specialized_serializer.mime_type
    
    @property
    def is_binary_format(self) -> bool:
        """Check if binary format - detects if needed."""
        if self._specialized_serializer is None:
            return False  # Assume text until detection
        return self._specialized_serializer.is_binary_format
    
    @property
    def supports_streaming(self) -> bool:
        """Check streaming support - detects if needed."""
        if self._specialized_serializer is None:
            return False  # Unknown until detection
        return self._specialized_serializer.supports_streaming
    
    # =============================================================================
    # CORE SERIALIZATION METHODS - Auto-detect and delegate
    # =============================================================================
    
    def dumps(self, data: Any, file_path: Optional[Union[str, Path]] = None, format_hint: Optional[str] = None) -> Union[str, bytes]:
        """
        Serialize data - auto-detects format on first use.
        
        Args:
            data: Data to serialize
            file_path: Optional file path for format detection
            format_hint: Optional format hint
            
        Returns:
            Serialized data
        """
        specialized = self._ensure_specialized(
            data=data, 
            file_path=file_path, 
            format_hint=format_hint
        )
        return specialized.dumps(data)
    
    def dumps_text(self, data: Any) -> str:
        """Serialize to text - delegates to specialized serializer."""
        specialized = self._ensure_specialized(data=data)
        return specialized.dumps_text(data)
    
    def dumps_binary(self, data: Any) -> bytes:
        """Serialize to binary - delegates to specialized serializer."""
        specialized = self._ensure_specialized(data=data)
        return specialized.dumps_binary(data)
    
    def loads(self, data: Union[str, bytes], format_hint: Optional[str] = None) -> Any:
        """
        Deserialize data - auto-detects format from content.
        
        Args:
            data: Data to deserialize
            format_hint: Optional format hint
            
        Returns:
            Deserialized object
        """
        specialized = self._ensure_specialized(
            content=data,
            binary_data=data if isinstance(data, bytes) else None,
            format_hint=format_hint
        )
        return specialized.loads(data)
    
    def loads_text(self, data: str) -> Any:
        """Deserialize from text - auto-detects format."""
        specialized = self._ensure_specialized(content=data)
        return specialized.loads_text(data)
    
    def loads_bytes(self, data: bytes) -> Any:
        """Deserialize from bytes - auto-detects format."""
        specialized = self._ensure_specialized(binary_data=data)
        return specialized.loads_bytes(data)
    
    # =============================================================================
    # FILE OPERATIONS - Auto-detect from file path/content
    # =============================================================================
    
    def save_file(self, data: Any, file_path: Union[str, Path], format_hint: Optional[str] = None) -> None:
        """
        Save to file - auto-detects format from file extension.
        
        Args:
            data: Data to save
            file_path: File path
            format_hint: Optional format hint
        """
        specialized = self._ensure_specialized(
            data=data,
            file_path=file_path,
            format_hint=format_hint
        )
        specialized.save_file(data, file_path)
    
    def load_file(self, file_path: Union[str, Path], format_hint: Optional[str] = None) -> Any:
        """
        Load from file - auto-detects format from file extension and content.
        
        Args:
            file_path: File path to load
            format_hint: Optional format hint
            
        Returns:
            Loaded data
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Try to sample content for detection if no hint provided
        if not format_hint:
            try:
                # Try reading as text first
                with open(path, 'r', encoding='utf-8') as f:
                    sample = f.read(1024)
                specialized = self._ensure_specialized(
                    file_path=file_path,
                    content=sample
                )
            except UnicodeDecodeError:
                # Binary file, read as bytes
                with open(path, 'rb') as f:
                    sample = f.read(1024)
                specialized = self._ensure_specialized(
                    file_path=file_path,
                    binary_data=sample
                )
        else:
            specialized = self._ensure_specialized(
                file_path=file_path,
                format_hint=format_hint
            )
        
        return specialized.load_file(file_path)
    
    # =============================================================================
    # ASYNC METHODS - Delegate to specialized serializer
    # =============================================================================
    
    async def dumps_async(self, data: Any, file_path: Optional[Union[str, Path]] = None, format_hint: Optional[str] = None) -> Union[str, bytes]:
        """Async serialize - auto-detects and delegates."""
        specialized = self._ensure_specialized(
            data=data,
            file_path=file_path,
            format_hint=format_hint
        )
        return await specialized.dumps_async(data)
    
    async def loads_async(self, data: Union[str, bytes], format_hint: Optional[str] = None) -> Any:
        """Async deserialize - auto-detects and delegates."""
        specialized = self._ensure_specialized(
            content=data,
            binary_data=data if isinstance(data, bytes) else None,
            format_hint=format_hint
        )
        return await specialized.loads_async(data)
    
    async def save_file_async(self, data: Any, file_path: Union[str, Path], format_hint: Optional[str] = None) -> None:
        """Async save file - auto-detects and delegates."""
        specialized = self._ensure_specialized(
            data=data,
            file_path=file_path,
            format_hint=format_hint
        )
        await specialized.save_file_async(data, file_path)
    
    async def load_file_async(self, file_path: Union[str, Path], format_hint: Optional[str] = None) -> Any:
        """Async load file - auto-detects and delegates."""
        # For async, rely more on extension detection to avoid blocking I/O
        specialized = self._ensure_specialized(
            file_path=file_path,
            format_hint=format_hint
        )
        return await specialized.load_file_async(file_path)
    
    # =============================================================================
    # DELEGATION METHODS - Pass through to specialized serializer
    # =============================================================================
    
    def validate_data(self, data: Any) -> bool:
        """Validate data - delegates to specialized serializer."""
        specialized = self._ensure_specialized(data=data)
        return specialized.validate_data(data)
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get schema info - delegates to specialized serializer."""
        if self._specialized_serializer is None:
            return {
                "format": "Auto-Detect",
                "status": "Not yet detected",
                "description": "Intelligent auto-detecting serializer"
            }
        return self._specialized_serializer.get_schema_info()
    
    def estimate_size(self, data: Any) -> int:
        """Estimate size - delegates to specialized serializer."""
        specialized = self._ensure_specialized(data=data)
        return specialized.estimate_size(data)
    
    def configure(self, **options: Any) -> None:
        """Configure - applies to specialized serializer if exists."""
        if self._specialized_serializer is not None:
            self._specialized_serializer.configure(**options)
        else:
            # Store for when we transform
            for key, value in options.items():
                if hasattr(self, key):
                    setattr(self, key, value)
    
    def reset_configuration(self) -> None:
        """Reset configuration - delegates to specialized serializer."""
        if self._specialized_serializer is not None:
            self._specialized_serializer.reset_configuration()
        else:
            # Reset our own configuration
            super().__init__()
    
    # =============================================================================
    # INTROSPECTION METHODS
    # =============================================================================
    
    def get_detected_format(self) -> Optional[str]:
        """
        Get the detected format name.
        
        Returns:
            Detected format name or None if not yet detected
        """
        return self._detected_format
    
    def is_transformed(self) -> bool:
        """
        Check if this serializer has been transformed to a specialized one.
        
        Returns:
            True if transformed, False if still in auto-detect mode
        """
        return self._specialized_serializer is not None
    
    def get_specialized_serializer(self) -> Optional[iSerialization]:
        """
        Get the underlying specialized serializer.
        
        Returns:
            Specialized serializer instance or None if not yet transformed
        """
        return self._specialized_serializer
    
    def force_format(self, format_name: str) -> None:
        """
        Force transformation to a specific format.
        
        Args:
            format_name: Format name to transform to
        """
        self._transform_to_specialized(format_name.upper())
        logger.info(f"Forced transformation to {format_name}")


# Convenience functions
def create_auto_serializer(confidence_threshold: float = 0.7) -> xSerialization:
    """
    Create a new auto-detecting serializer.
    
    Args:
        confidence_threshold: Minimum confidence for format detection
        
    Returns:
        New xSerialization instance
    """
    return xSerialization(confidence_threshold)


# Global instance for convenience
_global_x_serializer = xSerialization()

# Static functions - clean API without prefixes
def dumps(data: Any, file_path: Optional[Union[str, Path]] = None, format_hint: Optional[str] = None) -> Union[str, bytes]:
    """
    Smart serialization function that auto-detects format.
    
    Args:
        data: Data to serialize
        file_path: Optional file path for format detection
        format_hint: Optional format hint to override detection
        
    Returns:
        Serialized data in detected format
    """
    return _global_x_serializer.dumps(data, file_path, format_hint)

def loads(data: Union[str, bytes], format_hint: Optional[str] = None) -> Any:
    """
    Smart deserialization function that auto-detects format.
    
    Args:
        data: Data to deserialize
        format_hint: Optional format hint to override detection
        
    Returns:
        Deserialized Python object
    """
    return _global_x_serializer.loads(data, format_hint)

def save_file(data: Any, file_path: Union[str, Path], format_hint: Optional[str] = None) -> None:
    """
    Smart file saving that auto-detects format from extension.
    
    Args:
        data: Data to save
        file_path: File path (format detected from extension)
        format_hint: Optional format hint to override detection
    """
    return _global_x_serializer.save_file(data, file_path, format_hint)

def load_file(file_path: Union[str, Path], format_hint: Optional[str] = None) -> Any:
    """
    Smart file loading that auto-detects format from extension and content.
    
    Args:
        file_path: File path to load
        format_hint: Optional format hint to override detection
        
    Returns:
        Loaded and deserialized data
    """
    return _global_x_serializer.load_file(file_path, format_hint)
