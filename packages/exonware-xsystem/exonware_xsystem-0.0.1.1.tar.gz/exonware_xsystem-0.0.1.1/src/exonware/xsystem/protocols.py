"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: January 31, 2025

Protocol definitions for xSystem - Better type safety and duck typing.

This module defines Protocol classes that improve type checking and enable
better IDE support without requiring inheritance.
"""

from typing import Any, Protocol, Union, Optional, Dict, List
from typing_extensions import runtime_checkable


@runtime_checkable
class Serializable(Protocol):
    """Protocol for objects that can be serialized."""
    
    def dumps(self, data: Any, **kwargs: Any) -> Union[str, bytes]:
        """Serialize data to string or bytes."""
        ...
    
    def loads(self, data: Union[str, bytes], **kwargs: Any) -> Any:
        """Deserialize data from string or bytes."""
        ...


@runtime_checkable
class AsyncSerializable(Protocol):
    """Protocol for objects that support async serialization."""
    
    async def dumps_async(self, data: Any, **kwargs: Any) -> Union[str, bytes]:
        """Asynchronously serialize data to string or bytes."""
        ...
    
    async def loads_async(self, data: Union[str, bytes], **kwargs: Any) -> Any:
        """Asynchronously deserialize data from string or bytes."""
        ...


@runtime_checkable
class Hashable(Protocol):
    """Protocol for objects that can be hashed securely."""
    
    def hash(self, data: Union[str, bytes], **kwargs: Any) -> str:
        """Generate hash of data."""
        ...


@runtime_checkable
class Encryptable(Protocol):
    """Protocol for objects that support encryption/decryption."""
    
    def encrypt(self, data: Union[str, bytes], **kwargs: Any) -> bytes:
        """Encrypt data."""
        ...
    
    def decrypt(self, data: bytes, **kwargs: Any) -> Union[str, bytes]:
        """Decrypt data."""
        ...


@runtime_checkable
class Validatable(Protocol):
    """Protocol for objects that support data validation."""
    
    def validate(self, data: Any, **kwargs: Any) -> bool:
        """Validate data against rules."""
        ...
    
    def get_errors(self) -> List[Dict[str, Any]]:
        """Get validation errors."""
        ...


@runtime_checkable
class Cacheable(Protocol):
    """Protocol for objects that support caching."""
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache."""
        ...
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        ...
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        ...
    
    def clear(self) -> None:
        """Clear all cached values."""
        ...


@runtime_checkable
class Monitorable(Protocol):
    """Protocol for objects that support performance monitoring."""
    
    def start_monitoring(self) -> None:
        """Start performance monitoring."""
        ...
    
    def stop_monitoring(self) -> None:
        """Stop performance monitoring."""
        ...
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        ...


@runtime_checkable
class Configurable(Protocol):
    """Protocol for objects that support configuration."""
    
    def configure(self, **config: Any) -> None:
        """Configure object with parameters."""
        ...
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        ...


# Type aliases for common patterns
SerializationData = Union[str, bytes, Dict[str, Any], List[Any]]
HashAlgorithm = Union[str, int]  # Algorithm name or ID
EncryptionKey = Union[str, bytes]
ValidationRule = Union[str, Dict[str, Any]]
CacheKey = str
ConfigValue = Union[str, int, float, bool, None]
