"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: January 31, 2025

Lazy loading utilities for optimal performance.
"""

import importlib
import sys
import threading
from typing import Any, Dict, Optional, Set
from types import ModuleType

from ..config.logging_setup import get_logger

logger = get_logger("xsystem.utils.lazy_loader")

class LazyLoader:
    """
    Thread-safe lazy loader for modules with caching and performance optimization.
    """
    
    __slots__ = ('_module_path', '_cached_module', '_lock', '_loading')
    
    def __init__(self, module_path: str):
        """
        Initialize lazy loader.
        
        Args:
            module_path: Full module path to load
        """
        self._module_path = module_path
        self._cached_module: Optional[ModuleType] = None
        self._lock = threading.RLock()
        self._loading = False
    
    def __getattr__(self, name: str) -> Any:
        """Get attribute from lazily loaded module."""
        module = self._get_module()
        try:
            return getattr(module, name)
        except AttributeError:
            raise AttributeError(
                f"module '{self._module_path}' has no attribute '{name}'"
            )
    
    def __dir__(self) -> list:
        """Return available attributes from loaded module."""
        module = self._get_module()
        return dir(module)
    
    def _get_module(self) -> ModuleType:
        """Thread-safe module loading with caching."""
        if self._cached_module is not None:
            return self._cached_module
        
        with self._lock:
            # Double-check pattern
            if self._cached_module is not None:
                return self._cached_module
            
            if self._loading:
                # Prevent infinite recursion
                raise ImportError(f"Circular import detected for {self._module_path}")
            
            try:
                self._loading = True
                logger.debug(f"Lazy loading module: {self._module_path}")
                
                self._cached_module = importlib.import_module(self._module_path)
                
                logger.debug(f"Successfully loaded: {self._module_path}")
                return self._cached_module
                
            except Exception as e:
                logger.error(f"Failed to load module {self._module_path}: {e}")
                raise ImportError(f"Failed to load {self._module_path}: {e}") from e
            finally:
                self._loading = False


class LazyModuleRegistry:
    """
    Registry for managing lazy-loaded modules with performance tracking.
    """
    
    __slots__ = ('_modules', '_load_times', '_lock', '_access_counts')
    
    def __init__(self):
        """Initialize the registry."""
        self._modules: Dict[str, LazyLoader] = {}
        self._load_times: Dict[str, float] = {}
        self._access_counts: Dict[str, int] = {}
        self._lock = threading.RLock()
    
    def register_module(self, name: str, module_path: str) -> None:
        """
        Register a module for lazy loading.
        
        Args:
            name: Short name for the module
            module_path: Full import path
        """
        with self._lock:
            if name in self._modules:
                logger.warning(f"Module '{name}' already registered, overwriting")
            
            self._modules[name] = LazyLoader(module_path)
            self._access_counts[name] = 0
            logger.debug(f"Registered lazy module: {name} -> {module_path}")
    
    def get_module(self, name: str) -> LazyLoader:
        """
        Get a lazy-loaded module.
        
        Args:
            name: Module name
            
        Returns:
            LazyLoader instance
            
        Raises:
            KeyError: If module not registered
        """
        with self._lock:
            if name not in self._modules:
                raise KeyError(f"Module '{name}' not registered")
            
            self._access_counts[name] += 1
            return self._modules[name]
    
    def preload_frequently_used(self, threshold: int = 5) -> None:
        """
        Preload modules that are accessed frequently.
        
        Args:
            threshold: Minimum access count to trigger preloading
        """
        with self._lock:
            for name, count in self._access_counts.items():
                if count >= threshold:
                    try:
                        # Force loading
                        _ = self._modules[name]._get_module()
                        logger.info(f"Preloaded frequently used module: {name}")
                    except Exception as e:
                        logger.warning(f"Failed to preload {name}: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get loading statistics.
        
        Returns:
            Dictionary with loading statistics
        """
        with self._lock:
            loaded_count = sum(
                1 for loader in self._modules.values() 
                if loader._cached_module is not None
            )
            
            return {
                'total_registered': len(self._modules),
                'loaded_count': loaded_count,
                'unloaded_count': len(self._modules) - loaded_count,
                'access_counts': self._access_counts.copy(),
                'load_times': self._load_times.copy(),
            }
    
    def clear_cache(self) -> None:
        """Clear all cached modules (for testing/debugging)."""
        with self._lock:
            for loader in self._modules.values():
                loader._cached_module = None
            logger.info("Cleared all cached modules")


# Global registry instance
_global_registry = LazyModuleRegistry()

def register_lazy_module(name: str, module_path: str) -> None:
    """
    Register a module for lazy loading in the global registry.
    
    Args:
        name: Short name for the module
        module_path: Full import path
    """
    _global_registry.register_module(name, module_path)

def get_lazy_module(name: str) -> LazyLoader:
    """
    Get a lazy-loaded module from the global registry.
    
    Args:
        name: Module name
        
    Returns:
        LazyLoader instance
    """
    return _global_registry.get_module(name)

def get_loading_stats() -> Dict[str, Any]:
    """Get loading statistics from the global registry."""
    return _global_registry.get_stats()

def preload_frequently_used(threshold: int = 5) -> None:
    """Preload frequently used modules from the global registry."""
    _global_registry.preload_frequently_used(threshold)
