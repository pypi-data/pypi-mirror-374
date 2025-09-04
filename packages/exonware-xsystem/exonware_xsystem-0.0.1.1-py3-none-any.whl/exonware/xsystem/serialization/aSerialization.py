"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: January 31, 2025

Abstract base class for serialization implementations with full xSystem integration.

Provides common functionality for all serializers including:
- Security validation (path and data validation)
- Performance monitoring and limits
- Atomic file operations using xSystem I/O utilities
- Error handling and logging
- Thread-safe operations
- Smart delegation between text and binary operations

All file operations delegate to xSystem I/O utilities rather than implementing
custom file handling, following the production library principle.
"""

import sys
import ast
import types
import logging
import base64
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, AsyncIterator, BinaryIO, Dict, List, Optional, TextIO, Union, Set

from .iSerialization import iSerialization
from ..config.logging_setup import get_logger
from ..io.atomic_file import AtomicFileWriter, safe_read_text, safe_read_bytes, safe_write_text, safe_write_bytes
from ..security.path_validator import PathValidator, PathSecurityError
from ..validation.data_validator import DataValidator, ValidationError
from ..monitoring.performance_validator import performance_monitor

logger = get_logger("xsystem.serialization.base")


class SerializationError(Exception):
    """Base exception for serialization errors."""
    
    def __init__(self, message: str, format_name: str = "", original_error: Optional[Exception] = None):
        super().__init__(message)
        self.format_name = format_name
        self.original_error = original_error


class aSerialization(iSerialization, ABC):
    """
    Abstract base class providing common serialization functionality 
    with xSystem integration for security, validation, and file operations.
    
    🔄 ASYNC INTEGRATION:
       All serializers automatically inherit async capabilities through the unified
       iSerialization interface. Default async implementations delegate to sync
       methods via asyncio.to_thread(). Override async methods for performance
       when there's a real benefit (file I/O, streaming, network operations).
    
    🚨 IMPLEMENTATION REMINDER FOR ALL SERIALIZERS:
       DO NOT HARDCODE SERIALIZATION LOGIC - USE OFFICIAL LIBRARIES!
       
       Examples of CORRECT implementations:
       ✅ JSON: json.dumps() / json.loads()
       ✅ YAML: yaml.dump() / yaml.safe_load()  
       ✅ TOML: tomli_w.dumps() / tomllib.loads()
       ✅ XML: defusedxml.etree.tostring() / defusedxml.etree.fromstring()
       ✅ BSON: bson.encode() / bson.decode()
       ✅ Pickle: pickle.dumps() / pickle.loads()
       ✅ Marshal: marshal.dumps() / marshal.loads()
       ✅ CSV: csv.writer() / csv.reader()
       
       NEVER write custom parsers/writers for established formats!
    """

    def __init__(
        self,
        validate_input: bool = True,
        max_depth: int = 100,
        max_size_mb: float = 10.0,
        use_atomic_writes: bool = True,
        validate_paths: bool = True,
        base_path: Optional[Union[str, Path]] = None,
        text_encoding: str = 'utf-8',
        base64_encoding: str = 'ascii',
        allow_unsafe: bool = False,
        enable_sandboxing: bool = True,
        trusted_types: Optional[Set[type]] = None,
    ) -> None:
        """
        Initialize abstract serialization with xSystem utilities.

        Args:
            validate_input: Whether to validate input data for security
            max_depth: Maximum nesting depth allowed
            max_size_mb: Maximum data size in MB
            use_atomic_writes: Whether to use atomic file operations
            validate_paths: Whether to validate file paths for security
            base_path: Base path for path validation (None for no restriction)
            text_encoding: Text encoding for file operations (default: utf-8 for Arabic/international support)
            base64_encoding: Encoding for base64 strings (default: ascii - standard for base64)
            allow_unsafe: Allow unsafe operations without warnings (for binary formats)
            enable_sandboxing: Enable sandboxing for untrusted data deserialization
            trusted_types: Set of types considered safe for deserialization (None = use defaults)
        """
        self.validate_input = validate_input
        self.max_depth = max_depth
        self.max_size_mb = max_size_mb
        self.use_atomic_writes = use_atomic_writes
        self.validate_paths = validate_paths
        self.allow_unsafe = allow_unsafe
        self.text_encoding = text_encoding
        self.base64_encoding = base64_encoding
        self.enable_sandboxing = enable_sandboxing
        
        # Set up trusted types for sandboxing
        self.trusted_types = trusted_types or {
            # Basic safe types
            str, int, float, bool, type(None),
            # Collections
            list, dict, tuple, set, frozenset,
            # Common safe types
            bytes, bytearray,
        }

        # Initialize xSystem components
        if validate_input:
            self._data_validator = DataValidator(max_dict_depth=max_depth)
        
        if validate_paths:
            self._path_validator = PathValidator(
                base_path=base_path,
                max_path_length=4096,
                check_existence=False  # We'll handle creation
            )

        # Configuration storage
        self._config: Dict[str, Any] = {
            'validate_input': validate_input,
            'max_depth': max_depth,
            'max_size_mb': max_size_mb,
            'use_atomic_writes': use_atomic_writes,
            'validate_paths': validate_paths,
            'base_path': str(base_path) if base_path else None,
            'text_encoding': text_encoding,
            'base64_encoding': base64_encoding,
            'enable_sandboxing': enable_sandboxing,
            'trusted_types': [t.__name__ for t in self.trusted_types],
        }

        logger.debug(f"Initialized {self.format_name} serializer with validation: {validate_input}")

    def _is_risky_format(self) -> bool:
        """Check if this format is considered risky for security."""
        risky_formats = {'Pickle', 'Marshal', 'CBOR', 'BSON', 'MessagePack'}
        return self.format_name in risky_formats

    def _issue_security_warning_if_needed(self, operation: str = "deserialization") -> None:
        """Issue security warning for risky formats if not explicitly allowed."""
        if not self.allow_unsafe and self._is_risky_format():
            import warnings
            warnings.warn(
                f"{self.format_name} {operation} can be unsafe with untrusted data. "
                f"Ensure data comes from a trusted source or set allow_unsafe=True to suppress this warning.",
                UserWarning,
                stacklevel=3
            )

    # =============================================================================
    # VALIDATION AND SECURITY METHODS
    # =============================================================================

    def _validate_data_security(self, data: Any) -> None:
        """Validate data for security using xSystem validators."""
        if not self.validate_input:
            return

        try:
            # Check data size
            size_estimate = sys.getsizeof(str(data)) / (1024 * 1024)
            if size_estimate > self.max_size_mb:
                raise SerializationError(
                    f"Data size ({size_estimate:.2f}MB) exceeds limit ({self.max_size_mb}MB)",
                    format_name=self.format_name
                )

            # Validate structure depth and safety
            self._data_validator.validate_data_structure(data)
            
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Data validation passed for {self.format_name}")

        except ValidationError as e:
            raise SerializationError(
                f"{self.format_name} validation failed: {e}",
                format_name=self.format_name,
                original_error=e
            ) from e
        except Exception as e:
            raise SerializationError(
                f"{self.format_name} validation error: {e}",
                format_name=self.format_name,
                original_error=e
            ) from e

    def _validate_deserialized_data_sandbox(self, data: Any, source: str = "unknown") -> None:
        """
        Validate deserialized data in a sandbox to prevent malicious code execution.
        
        This method checks for potentially dangerous objects, functions, modules,
        and other constructs that could be used for code execution attacks.
        
        Args:
            data: Deserialized data to validate
            source: Source of the data (for logging)
            
        Raises:
            SerializationError: If dangerous content is detected
        """
        if not self.enable_sandboxing:
            return
            
        try:
            self._recursive_sandbox_check(data, set(), 0)
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Sandbox validation passed for {self.format_name} data from {source}")
        except Exception as e:
            raise SerializationError(
                f"Sandbox validation failed for {self.format_name} data: {e}",
                format_name=self.format_name,
                original_error=e
            ) from e
    
    def _recursive_sandbox_check(self, obj: Any, visited: Set[int], depth: int) -> None:
        """
        Recursively check object for dangerous content.
        
        Args:
            obj: Object to check
            visited: Set of already visited object IDs (cycle detection)
            depth: Current recursion depth
            
        Raises:
            SerializationError: If dangerous content is detected
        """
        # Prevent infinite recursion and cycles
        if depth > self.max_depth:
            raise SerializationError(f"Sandbox check exceeded max depth {self.max_depth}")
        
        obj_id = id(obj)
        if obj_id in visited:
            return  # Already checked
        visited.add(obj_id)
        
        # Check object type
        obj_type = type(obj)
        
        # Allow trusted types
        if obj_type in self.trusted_types:
            # For collections, recursively check contents
            if isinstance(obj, dict):
                for key, value in obj.items():
                    self._recursive_sandbox_check(key, visited, depth + 1)
                    self._recursive_sandbox_check(value, visited, depth + 1)
            elif isinstance(obj, (list, tuple, set, frozenset)):
                for item in obj:
                    self._recursive_sandbox_check(item, visited, depth + 1)
            return
        
        # Check for dangerous types
        dangerous_types = {
            types.FunctionType, types.MethodType, types.LambdaType,
            types.GeneratorType, types.CoroutineType,
            types.ModuleType, types.CodeType, types.FrameType,
            type, type(type), type(lambda: None),
        }
        
        if obj_type in dangerous_types:
            raise SerializationError(
                f"Dangerous type detected: {obj_type.__name__}. "
                f"This could indicate a code injection attempt."
            )
        
        # Check for dangerous attributes
        dangerous_attrs = {
            '__code__', '__func__', '__globals__', '__closure__',
            '__dict__', '__class__', '__bases__', '__mro__',
            '__subclasshook__', '__import__', 'eval', 'exec',
            '__builtins__', '__loader__', '__package__'
        }
        
        if hasattr(obj, '__dict__'):
            obj_dict = getattr(obj, '__dict__', {})
            for attr_name in dangerous_attrs:
                if attr_name in obj_dict:
                    raise SerializationError(
                        f"Dangerous attribute detected: {attr_name}. "
                        f"This could indicate a code injection attempt."
                    )
        
        # Check for objects with dangerous methods
        if hasattr(obj, '__reduce__') or hasattr(obj, '__reduce_ex__'):
            # These methods are used by pickle and can be exploited
            if not self.allow_unsafe:
                raise SerializationError(
                    f"Object with __reduce__ method detected: {obj_type.__name__}. "
                    f"This could be used for code execution attacks."
                )
        
        # Check string content for potential code injection
        if isinstance(obj, str):
            suspicious_patterns = [
                'import ', '__import__', 'eval(', 'exec(',
                'subprocess', 'os.system', 'os.popen',
                '__builtins__', 'globals()', 'locals()',
                'compile(', 'memoryview', 'bytearray'
            ]
            obj_lower = obj.lower()
            for pattern in suspicious_patterns:
                if pattern in obj_lower:
                    logger.warning(f"Suspicious string pattern detected: {pattern}")
                    # Don't fail for strings, just log warning
                    break
        
        # For unknown types, check if they have safe attributes only
        if hasattr(obj, '__dict__'):
            for attr_name, attr_value in getattr(obj, '__dict__', {}).items():
                if not attr_name.startswith('_'):  # Skip private attributes
                    self._recursive_sandbox_check(attr_value, visited, depth + 1)

    def _validate_file_path(self, file_path: Union[str, Path]) -> Path:
        """Validate file path using xSystem path validator."""
        if not self.validate_paths:
            return Path(file_path)

        try:
            validated_path = self._path_validator.validate_path(str(file_path))
            return validated_path
        except PathSecurityError as e:
            raise SerializationError(
                f"Path validation failed: {e}",
                format_name=self.format_name,
                original_error=e
            ) from e

    def _handle_serialization_error(self, operation: str, error: Exception) -> None:
        """
        Unified error handling for all serializers.
        
        Args:
            operation: Operation name (e.g., "serialization", "deserialization")
            error: Original exception
            
        Raises:
            SerializationError: Wrapped error with format context
        """
        raise SerializationError(
            f"{self.format_name} {operation} failed: {error}",
            format_name=self.format_name,
            original_error=error
        ) from error

    # =============================================================================
    # PRIVATE FILE I/O UTILITIES
    # =============================================================================

    def _safe_file_write(self, data: str, file_path: Path) -> None:
        """Write text file using xSystem I/O utilities."""
        try:
            # Use xSystem safe_write_text utility (handles atomic writes internally)
            safe_write_text(file_path, data, encoding=self.text_encoding, backup=self.use_atomic_writes)
            logger.debug(f"Wrote {self.format_name} text to {file_path}")

        except Exception as e:
            raise SerializationError(
                f"Failed to write text file {file_path}: {e}",
                format_name=self.format_name,
                original_error=e
            ) from e

    def _safe_file_write_binary(self, data: bytes, file_path: Path) -> None:
        """Write binary file using xSystem I/O utilities."""
        try:
            # Use xSystem safe_write_bytes utility (handles atomic writes internally)
            safe_write_bytes(file_path, data, backup=self.use_atomic_writes)
            logger.debug(f"Wrote {self.format_name} binary to {file_path}")

        except Exception as e:
            raise SerializationError(
                f"Failed to write binary file {file_path}: {e}",
                format_name=self.format_name,
                original_error=e
            ) from e

    def _safe_file_read(self, file_path: Path) -> str:
        """Read text file using xSystem I/O utilities."""
        try:
            # Use xSystem safe_read_text utility (handles size validation internally)
            content = safe_read_text(file_path, encoding=self.text_encoding, max_size_mb=self.max_size_mb)
            logger.debug(f"Read {self.format_name} text from {file_path}")
            return content

        except Exception as e:
            raise SerializationError(
                f"Failed to read text file {file_path}: {e}",
                format_name=self.format_name,
                original_error=e
            ) from e

    def _safe_file_read_binary(self, file_path: Path) -> bytes:
        """Read binary file using xSystem I/O utilities."""
        try:
            # Use xSystem safe_read_bytes utility (handles size validation internally)
            content = safe_read_bytes(file_path, max_size_mb=self.max_size_mb)
            logger.debug(f"Read {self.format_name} binary from {file_path}")
            return content

        except Exception as e:
            raise SerializationError(
                f"Failed to read binary file {file_path}: {e}",
                format_name=self.format_name,
                original_error=e
            ) from e

    # =============================================================================
    # SMART DELEGATION - CORE SERIALIZATION METHODS
    # =============================================================================

    def dumps(self, data: Any) -> Union[str, bytes]:
        """
        Serialize data to string or bytes based on format type.
        
        Automatically delegates to dumps_text() or dumps_binary() based on 
        is_binary_format property.
        """
        if self.is_binary_format:
            return self.dumps_binary(data)
        else:
            return self.dumps_text(data)

    def loads(self, data: Union[str, bytes]) -> Any:
        """
        Deserialize from string or bytes with automatic sandboxing.
        
        Automatically handles both text and binary data based on input type
        and format capabilities. Applies sandboxing validation to prevent
        code injection attacks.
        """
        # Perform deserialization
        if isinstance(data, bytes):
            result = self.loads_bytes(data)
        else:
            result = self.loads_text(data)
        
        # Apply sandboxing validation to the result
        self._validate_deserialized_data_sandbox(result, "loads")
        
        return result

    # Text format fallback for binary formats that support base64
    def _convert_binary_to_text(self, binary_data: bytes) -> str:
        """Convert binary data to base64 text for text-based interfaces."""
        return base64.b64encode(binary_data).decode(self.base64_encoding)

    def _convert_text_to_binary(self, text_data: str) -> bytes:
        """Convert base64 text back to binary data."""
        return base64.b64decode(text_data.encode(self.base64_encoding))

    # Default implementations that delegate appropriately
    @abstractmethod
    def dumps_text(self, data: Any) -> str:
        """
        Abstract method for text serialization.
        
        All text formats must implement this method.
        Binary formats can optionally implement this for base64 support.
        """
        pass

    @abstractmethod
    def dumps_binary(self, data: Any) -> bytes:
        """
        Abstract method for binary serialization.
        
        All binary formats must implement this method.
        Text formats should raise NotImplementedError if called.
        """
        pass

    @abstractmethod
    def loads_text(self, data: str) -> Any:
        """
        Abstract method for text deserialization.
        
        All text formats must implement this method.
        Binary formats can optionally implement this for base64 support.
        """
        pass

    @abstractmethod
    def loads_bytes(self, data: bytes) -> Any:
        """
        Abstract method for binary deserialization.
        
        All binary formats must implement this method.
        Text formats should raise NotImplementedError if called.
        """
        pass

    # =============================================================================
    # SMART DELEGATION - FILE-LIKE OBJECT METHODS
    # =============================================================================

    def dump(self, data: Any, fp: Union[TextIO, BinaryIO]) -> None:
        """
        Serialize data to file-like object.
        
        Automatically chooses text or binary mode based on format type.
        """
        if self.is_binary_format:
            self.dump_binary(data, fp)
        else:
            self.dump_text(data, fp)

    def dump_text(self, data: Any, fp: TextIO) -> None:
        """Serialize data to text file-like object."""
        try:
            self._validate_data_security(data)
            serialized_data = self.dumps_text(data)
            fp.write(serialized_data)
            logger.debug(f"Successfully dumped {self.format_name} text data to file object")

        except SerializationError:
            raise
        except Exception as e:
            self._handle_serialization_error("text dump", e)

    def dump_binary(self, data: Any, fp: BinaryIO) -> None:
        """Serialize data to binary file-like object."""
        try:
            self._validate_data_security(data)
            serialized_data = self.dumps_binary(data)
            fp.write(serialized_data)
            logger.debug(f"Successfully dumped {self.format_name} binary data to file object")

        except SerializationError:
            raise
        except Exception as e:
            self._handle_serialization_error("binary dump", e)

    def load(self, fp: Union[TextIO, BinaryIO]) -> Any:
        """
        Deserialize from file-like object.
        
        Automatically handles text or binary file-like objects.
        """
        try:
            # Try to detect if it's binary or text based on the file object
            if hasattr(fp, 'mode') and 'b' in fp.mode:
                return self.load_binary(fp)
            else:
                return self.load_text(fp)
        except Exception:
            # Fallback: try based on format type
            if self.is_binary_format:
                return self.load_binary(fp)
            else:
                return self.load_text(fp)

    def load_text(self, fp: TextIO) -> Any:
        """Deserialize from text file-like object."""
        try:
            content = fp.read()
            
            # Check size
            if len(content) > self.max_size_mb * 1024 * 1024:
                raise SerializationError(
                    f"Content too large: {len(content)} bytes",
                    format_name=self.format_name
                )
            
            data = self.loads_text(content)
            
            if self.validate_input:
                self._validate_data_security(data)
            
            logger.debug(f"Successfully loaded {self.format_name} text data from file object")
            return data

        except SerializationError:
            raise
        except Exception as e:
            self._handle_serialization_error("text load", e)

    def load_binary(self, fp: BinaryIO) -> Any:
        """Deserialize from binary file-like object."""
        try:
            content = fp.read()
            
            # Check size
            if len(content) > self.max_size_mb * 1024 * 1024:
                raise SerializationError(
                    f"Content too large: {len(content)} bytes",
                    format_name=self.format_name
                )
            
            data = self.loads_bytes(content)
            
            if self.validate_input:
                self._validate_data_security(data)
            
            logger.debug(f"Successfully loaded {self.format_name} binary data from file object")
            return data

        except SerializationError:
            raise
        except Exception as e:
            self._handle_serialization_error("binary load", e)

    # =============================================================================
    # SMART DELEGATION - FILE PATH METHODS
    # =============================================================================

    @performance_monitor("serialization_save")
    def save_file(self, data: Any, file_path: Union[str, Path]) -> None:
        """
        Save data to file with automatic binary/text handling.

        Args:
            data: Data to serialize
            file_path: Path to save file

        Raises:
            SerializationError: If saving fails
        """
        try:
            # Validate data
            self._validate_data_security(data)
            
            # Validate and resolve path
            validated_path = self._validate_file_path(file_path)
            
            # Ensure parent directory exists
            validated_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Auto-choose based on format type
            if self.is_binary_format:
                serialized_data = self.dumps_binary(data)
                self._safe_file_write_binary(serialized_data, validated_path)
            else:
                serialized_data = self.dumps_text(data)
                self._safe_file_write(serialized_data, validated_path)
            
            logger.info(f"Successfully saved {self.format_name} data to {validated_path}")

        except SerializationError:
            raise
        except Exception as e:
            raise SerializationError(
                f"Unexpected error saving file {file_path}: {e}",
                format_name=self.format_name,
                original_error=e
            ) from e

    @performance_monitor("serialization_load")
    def load_file(self, file_path: Union[str, Path]) -> Any:
        """
        Load data from file with automatic binary/text handling.

        Args:
            file_path: Path to load from

        Returns:
            Deserialized Python object

        Raises:
            SerializationError: If loading fails
        """
        # Issue security warning for risky formats
        self._issue_security_warning_if_needed("file deserialization")
        
        try:
            # Validate and resolve path
            validated_path = self._validate_file_path(file_path)
            
            # Check file exists
            if not validated_path.exists():
                raise SerializationError(
                    f"File not found: {validated_path}",
                    format_name=self.format_name
                )
            
            # Auto-choose based on format type
            if self.is_binary_format:
                content = self._safe_file_read_binary(validated_path)
                data = self.loads_bytes(content)
            else:
                content = self._safe_file_read(validated_path)
                data = self.loads_text(content)
            
            # Validate loaded data if configured
            if self.validate_input:
                self._validate_data_security(data)
            
            # Apply sandboxing validation to prevent code injection
            self._validate_deserialized_data_sandbox(data, f"file:{validated_path}")
            
            logger.info(f"Successfully loaded {self.format_name} data from {validated_path}")
            return data

        except SerializationError:
            raise
        except Exception as e:
            raise SerializationError(
                f"Unexpected error loading file {file_path}: {e}",
                format_name=self.format_name,
                original_error=e
            ) from e

    # =============================================================================
    # VALIDATION AND UTILITY METHODS
    # =============================================================================

    def validate_data(self, data: Any) -> bool:
        """
        Validate data for serialization compatibility.

        Args:
            data: Data to validate

        Returns:
            True if data can be serialized

        Raises:
            SerializationError: If validation fails
        """
        try:
            self._validate_data_security(data)
            return True
        except SerializationError:
            return False

    def estimate_size(self, data: Any) -> int:
        """
        Estimate serialized size in bytes.

        Args:
            data: Data to estimate

        Returns:
            Estimated size in bytes
        """
        try:
            # Quick estimation using string representation
            return sys.getsizeof(str(data))
        except Exception:
            # Fallback conservative estimate
            return 1024  # 1KB

    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get schema information for this serialization format.

        Returns:
            Dictionary with schema information
        """
        return {
            'format_name': self.format_name,
            'file_extensions': self.file_extensions,
            'mime_type': self.mime_type,
            'is_binary_format': self.is_binary_format,
            'supports_streaming': self.supports_streaming,
            'max_depth': self.max_depth,
            'max_size_mb': self.max_size_mb,
            'validation_enabled': self.validate_input,
            'security_features': {
                'path_validation': self.validate_paths,
                'atomic_writes': self.use_atomic_writes,
                'data_validation': self.validate_input,
            },
            'encoding_settings': {
                'text_encoding': self.text_encoding,
                'base64_encoding': self.base64_encoding,
            },
            'supported_operations': {
                'text_serialization': True,  # All formats support text via base64 fallback
                'binary_serialization': self.is_binary_format,
                'streaming': self.supports_streaming,
                'file_operations': True,
                'validation': True,
            }
        }

    # =============================================================================
    # CONFIGURATION METHODS
    # =============================================================================

    def configure(self, **options: Any) -> None:
        """
        Configure serialization options.

        Args:
            **options: Configuration options
        """
        for key, value in options.items():
            if hasattr(self, f'_{key}') or key in self._config:
                self._config[key] = value
                if hasattr(self, key):
                    setattr(self, key, value)
                logger.debug(f"Updated {self.format_name} config: {key} = {value}")

    def reset_configuration(self) -> None:
        """Reset configuration to defaults."""
        default_config = {
            'validate_input': True,
            'max_depth': 100,
            'max_size_mb': 10.0,
            'use_atomic_writes': True,
            'validate_paths': True,
            'base_path': None,
            'text_encoding': 'utf-8',
            'base64_encoding': 'ascii',
        }
        
        self._config.update(default_config)
        for key, value in default_config.items():
            if hasattr(self, key):
                setattr(self, key, value)
                
        logger.debug(f"Reset {self.format_name} configuration to defaults")

    def get_configuration(self) -> Dict[str, Any]:
        """
        Get current configuration.

        Returns:
            Current configuration dictionary
        """
        return self._config.copy()

    def get_config(self) -> Dict[str, Any]:
        """
        Get current configuration (alias for get_configuration).

        Returns:
            Current configuration dictionary
        """
        return self.get_configuration()

    # =============================================================================
    # ASYNC IMPLEMENTATIONS - Default implementations using asyncio.to_thread
    # =============================================================================

    async def dumps_async(self, data: Any) -> Union[str, bytes]:
        """
        Async version of dumps() - delegates to sync version via asyncio.to_thread.
        Override in specific serializers for native async implementation when beneficial.
        """
        import asyncio
        return await asyncio.to_thread(self.dumps, data)

    async def dumps_text_async(self, data: Any) -> str:
        """Async version of dumps_text()."""
        import asyncio
        return await asyncio.to_thread(self.dumps_text, data)

    async def dumps_binary_async(self, data: Any) -> bytes:
        """Async version of dumps_binary()."""
        import asyncio
        return await asyncio.to_thread(self.dumps_binary, data)

    async def loads_async(self, data: Union[str, bytes]) -> Any:
        """Async version of loads()."""
        import asyncio
        return await asyncio.to_thread(self.loads, data)

    async def loads_text_async(self, data: str) -> Any:
        """Async version of loads_text()."""
        import asyncio
        return await asyncio.to_thread(self.loads_text, data)

    async def loads_bytes_async(self, data: bytes) -> Any:
        """Async version of loads_bytes()."""
        import asyncio
        return await asyncio.to_thread(self.loads_bytes, data)

    async def save_file_async(self, data: Any, file_path: Union[str, Path]) -> None:
        """
        Async file save with aiofiles when available, fallback to thread.
        """
        try:
            import aiofiles
            
            # Serialize data first
            serialized_data = await self.dumps_async(data)
            
            # Determine mode based on format type
            mode = 'wb' if self.is_binary_format else 'w'
            encoding = None if self.is_binary_format else self.text_encoding
            
            async with aiofiles.open(file_path, mode, encoding=encoding) as f:
                await f.write(serialized_data)
                
        except ImportError:
            # Fallback to sync version in thread
            import asyncio
            await asyncio.to_thread(self.save_file, data, file_path)

    async def load_file_async(self, file_path: Union[str, Path]) -> Any:
        """
        Async file load with aiofiles when available, fallback to thread.
        """
        try:
            import aiofiles
            
            # Determine mode based on format type
            mode = 'rb' if self.is_binary_format else 'r'
            encoding = None if self.is_binary_format else self.text_encoding
            
            async with aiofiles.open(file_path, mode, encoding=encoding) as f:
                content = await f.read()
                
            return await self.loads_async(content)
            
        except ImportError:
            # Fallback to sync version in thread
            import asyncio
            return await asyncio.to_thread(self.load_file, file_path)

    async def stream_serialize(self, data: Any, chunk_size: int = 8192) -> AsyncIterator[Union[str, bytes]]:
        """
        Default streaming implementation: serialize all, then yield chunks.
        Override for formats that support true streaming.
        """
        if not self.supports_streaming:
            raise NotImplementedError(f"{self.format_name} does not support streaming")
        
        # Default implementation: serialize all, then chunk
        serialized_data = await self.dumps_async(data)
        
        for i in range(0, len(serialized_data), chunk_size):
            yield serialized_data[i:i + chunk_size]

    async def stream_deserialize(self, data_stream: AsyncIterator[Union[str, bytes]]) -> Any:
        """
        Default streaming deserialization: collect all chunks, then deserialize.
        Override for formats that support true streaming.
        """
        if not self.supports_streaming:
            raise NotImplementedError(f"{self.format_name} does not support streaming")
        
        # Collect all chunks
        chunks = []
        async for chunk in data_stream:
            chunks.append(chunk)
        
        # Combine chunks based on format type
        if self.is_binary_format:
            combined_data = b''.join(chunks)
        else:
            combined_data = ''.join(chunks)
        
        return await self.loads_async(combined_data)

    async def serialize_batch(self, data_list: List[Any]) -> List[Union[str, bytes]]:
        """
        Concurrent batch serialization using asyncio.gather.
        """
        import asyncio
        
        tasks = [self.dumps_async(data) for data in data_list]
        return await asyncio.gather(*tasks)

    async def deserialize_batch(self, data_list: List[Union[str, bytes]]) -> List[Any]:
        """
        Concurrent batch deserialization using asyncio.gather.
        """
        import asyncio
        
        tasks = [self.loads_async(data) for data in data_list]
        return await asyncio.gather(*tasks)

    async def save_batch_files(self, data_dict: Dict[Union[str, Path], Any]) -> None:
        """
        Concurrent batch file saving using asyncio.gather.
        """
        import asyncio
        
        tasks = [self.save_file_async(data, path) for path, data in data_dict.items()]
        await asyncio.gather(*tasks)

    async def load_batch_files(self, file_paths: List[Union[str, Path]]) -> Dict[Union[str, Path], Any]:
        """
        Concurrent batch file loading using asyncio.gather.
        """
        import asyncio
        
        tasks = [self.load_file_async(path) for path in file_paths]
        results = await asyncio.gather(*tasks)
        
        return dict(zip(file_paths, results))

    async def validate_data_async(self, data: Any) -> bool:
        """Async version of validate_data()."""
        import asyncio
        return await asyncio.to_thread(self.validate_data, data)

    async def estimate_size_async(self, data: Any) -> int:
        """Async version of estimate_size()."""
        import asyncio
        return await asyncio.to_thread(self.estimate_size, data)

    # =============================================================================
    # ABSTRACT METHODS - MUST BE IMPLEMENTED BY CONCRETE CLASSES
    # =============================================================================

    @property
    @abstractmethod
    def format_name(self) -> str:
        """Get the serialization format name."""
        pass

    @property
    @abstractmethod
    def file_extensions(self) -> list[str]:
        """Get supported file extensions."""
        pass

    @property
    @abstractmethod
    def mime_type(self) -> str:
        """Get the MIME type."""
        pass

    @property
    @abstractmethod
    def is_binary_format(self) -> bool:
        """Whether this is a binary format."""
        pass

    @property
    @abstractmethod
    def supports_streaming(self) -> bool:
        """Whether streaming is supported."""
        pass

    # Note: dumps, loads, dumps_text, dumps_binary, loads_text, loads_bytes
    # are now implemented with smart delegation. Concrete classes should
    # override the appropriate text/binary methods based on their format type.